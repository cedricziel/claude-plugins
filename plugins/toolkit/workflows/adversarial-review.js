export const meta = {
  name: 'adversarial-review',
  description: 'Multi-lens code review where every finding must survive independent refutation',
  whenToUse: 'Before merging a non-trivial PR or branch, when a single review pass is not enough confidence',
  phases: [
    { title: 'Review', detail: 'one reviewer per lens over the diff' },
    { title: 'Verify', detail: 'three refuters per finding, distinct angles' },
    { title: 'Critic', detail: 'what did the reviewers miss?' },
  ],
}

// args: { diffPath: string, target: string, votes?: number, maxFindings?: number, reviewModel?: string }
const diffPath = args?.diffPath
if (!diffPath) throw new Error('args.diffPath is required — invoke via /adversarial-review, which produces it with scripts/review-target.sh')
const target = args?.target || 'working tree'
const VOTES = args?.votes ?? 3
const MAX = args?.maxFindings ?? 8
const THINK = args?.reviewModel ?? args?.thinkModel ?? 'opus'   // review, refute, critique are judgment work

const LENSES = [
  'correctness (logic errors, off-by-one, wrong branch conditions, unhandled cases)',
  'security (injection, authz gaps, secrets, unsafe deserialization, path traversal)',
  'concurrency and resource handling (races, leaks, missing cleanup, cancellation)',
  'test coverage (behaviour changed without a test that would catch a regression)',
  'spec and docs drift (behaviour that contradicts or is missing from specs, docs, CLAUDE.md, skills)',
]

const SEVERITY = { critical: 0, high: 1, medium: 2, low: 3 }

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'integer' },
          title: { type: 'string', description: 'one line, the claim alone' },
          claim: { type: 'string', description: 'what is wrong, precisely' },
          failure_scenario: { type: 'string', description: 'concrete input/state → wrong output or crash' },
          severity: { type: 'string', enum: ['critical', 'high', 'medium', 'low'] },
        },
        required: ['file', 'line', 'title', 'claim', 'failure_scenario', 'severity'],
      },
    },
  },
  required: ['findings'],
}

const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string', description: 'the evidence, with file:line references' },
  },
  required: ['refuted', 'reason'],
}

const GAPS = {
  type: 'object',
  properties: {
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['gaps'],
}

const REFUTERS = [
  'read the surrounding code and callers and show the failing path is unreachable or already guarded',
  'find an existing test, type, or invariant in the repo that already prevents this failure',
  'construct the exact failing input or state described and show that it does NOT actually fail',
]

const key = (f) => `${f.file}:${f.line}:${f.title.toLowerCase().replace(/\W+/g, ' ').trim()}`

phase('Review')
const reviews = await parallel(LENSES.map((lens) => () =>
  agent(
    `You are reviewing a code change (${target}) through ONE lens only: ${lens}.
Read the unified diff at ${diffPath}. Open the surrounding files in the repository when the diff alone is not enough to judge.
Report only defects that have a concrete failure scenario. Do not report style, naming, or hypothetical concerns.
Line numbers must refer to the NEW side of the diff.`,
    { label: `review:${lens.split(' ')[0]}`, phase: 'Review', schema: FINDINGS, model: THINK },
  ),
))

// Barrier is deliberate: dedup and ranking need the full set of findings.
const seen = new Set()
const all = reviews.filter(Boolean).flatMap((r) => r.findings).filter((f) => {
  const k = key(f)
  if (seen.has(k)) return false
  seen.add(k)
  return true
})
all.sort((a, b) => (SEVERITY[a.severity] ?? 9) - (SEVERITY[b.severity] ?? 9))
const chosen = all.slice(0, MAX)
log(`${all.length} unique findings from ${reviews.filter(Boolean).length} lenses; verifying top ${chosen.length}`)
if (all.length > chosen.length) log(`dropped ${all.length - chosen.length} lower-severity findings (raise maxFindings to include them)`)

phase('Verify')
const judged = await parallel(chosen.map((f) => () =>
  parallel(REFUTERS.slice(0, VOTES).map((angle, i) => () =>
    agent(
      `A reviewer claims a defect in ${f.file}:${f.line} (change: ${target}, diff at ${diffPath}):
Title: ${f.title}
Claim: ${f.claim}
Failure scenario: ${f.failure_scenario}

Your job is to REFUTE this claim. Approach: ${angle}.
Read the actual code in the repository; do not reason from the diff alone.
If you cannot find solid evidence either way, answer refuted=true — the burden of proof is on the claim.`,
      { label: `refute:${f.file.split('/').pop()}#${i + 1}`, phase: 'Verify', schema: VERDICT, model: THINK },
    ),
  )).then((votes) => {
    const v = votes.filter(Boolean)
    const upheld = v.filter((x) => !x.refuted).length
    return { ...f, votes: v, survives: v.length > 0 && upheld * 2 >= v.length + (v.length % 2) }
  }),
))

const confirmed = judged.filter((j) => j.survives)
const rejected = judged.filter((j) => !j.survives)
log(`${confirmed.length} confirmed, ${rejected.length} refuted`)

phase('Critic')
const critic = await agent(
  `A multi-lens review of ${target} (diff at ${diffPath}) confirmed these findings:
${confirmed.map((f) => `- ${f.file}:${f.line} ${f.title}`).join('\n') || '- none'}

What did the reviewers miss? Read the diff and the touched files. Name only concrete, unexamined risks — behaviours, inputs, or interactions the findings above do not cover. If nothing is missing, return an empty list.`,
  { label: 'critic', phase: 'Critic', schema: GAPS, model: THINK },
)

return {
  target,
  confirmed: confirmed.map(({ votes, survives, ...f }) => ({ ...f, evidence: votes.filter((v) => !v.refuted).map((v) => v.reason) })),
  rejected: rejected.map((f) => ({ file: f.file, line: f.line, title: f.title, why: f.votes.filter((v) => v.refuted).map((v) => v.reason)[0] })),
  gaps: critic?.gaps ?? [],
  dropped: all.length - chosen.length,
}
