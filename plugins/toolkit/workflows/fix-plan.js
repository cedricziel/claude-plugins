export const meta = {
  name: 'fix-plan',
  description: 'Plan a single-PR fix before coding: files, the failing test, sequence, risks, size — judgment step on the strong model, proposed for human approval',
  whenToUse: 'After issue-triage decided fix-small, before fix-small. Skipped by /issue-run when the change is trivially small. Args: { number, repo, issue, evidence, repoDir? } from issue-triage',
  phases: [{ title: 'Plan', detail: 'one opus agent' }, { title: 'Critique', detail: 'planning critic' }],
}

// args: { repoDir?, number, repo, issue: {title, kind, expected, claims[]}, evidence: {code, history, premise}, sizeLines?, minLines?, targetLines?, maxLines? }
const THINK = args?.thinkModel ?? 'opus'   // judgment: decide, review, refute, critique
const { number, repo, issue, evidence } = args
if (!number || !repo || !issue || !evidence) throw new Error('args.number, repo, issue and evidence are required — invoke via /issue-run, which supplies them from issue-triage')
const AT = args.repoDir ? `Work in the repository checkout at ${args.repoDir} (cd there first; git and CLI commands run against that repo). ` : ''
const TARGET = args.targetLines ?? 200
const MAX = args.maxLines ?? 500
const MIN = args.minLines ?? 50
if (typeof args.sizeLines === 'number' && args.sizeLines < MIN) {
  log(`estimated ${args.sizeLines} lines (< ${MIN}); a diff you can describe in one sentence needs no plan — skipping`)
  return { plan: null, critique: null, refused: `change under ${MIN} lines` }
}

const PLAN = {
  type: 'object',
  properties: {
    summary: { type: 'string', description: 'two sentences: what will change and why this way' },
    files: { type: 'array', items: { type: 'object', properties: { path: { type: 'string' }, change: { type: 'string' } }, required: ['path', 'change'] } },
    failingTest: { type: 'string', description: 'the test to write or reuse first, and what it asserts' },
    steps: { type: 'array', items: { type: 'string' }, description: 'ordered, each one commit-sized' },
    risks: { type: 'array', items: { type: 'string' } },
    outOfScope: { type: 'array', items: { type: 'string' }, description: 'tempting adjacent changes NOT to make' },
    estimatedLines: { type: 'integer' },
    tooBig: { type: 'boolean', description: 'true if an honest plan exceeds maxLines — then it is a stack, not a fix' },
  },
  required: ['summary', 'files', 'failingTest', 'steps', 'risks', 'outOfScope', 'estimatedLines', 'tooBig'],
}
const CRITIQUE = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' },
    problems: { type: 'array', items: { type: 'string' }, description: 'missing case, wrong file, plan solves the test not the issue, hidden scope' },
  },
  required: ['ok', 'problems'],
}

const brief = `${AT}Issue ${repo}#${number} "${issue.title}" (${issue.kind}). Expected: ${issue.expected}
Claims: ${issue.claims.map((c) => `- ${c}`).join('\n')}
Evidence from triage — code: ${evidence.code?.summary} | history: ${evidence.history?.summary} | premise: ${evidence.premise?.detail}
Reproducing test: ${evidence.premise?.testPath || 'none yet'}`

phase('Plan')
let plan = await agent(
  `${brief}

Write the plan for a single PR that fixes exactly this issue. Read the code; do not plan from the issue text alone.
Aim for about ${TARGET} changed lines; if an honest plan needs more than ${MAX}, say tooBig=true and explain — do not shrink the fix to fit.
Name the adjacent things you are deliberately not touching.`,
  { label: 'plan', phase: 'Plan', schema: PLAN, model: THINK },
)
if (!plan) throw new Error('no plan produced')

phase('Critique')
const critique = await agent(
  `${brief}

Proposed plan: ${JSON.stringify(plan)}

You are the planning critic. Find what is wrong with this plan: a case the issue implies that the plan misses, a file the change must touch that is absent, a step that makes the reproducing test pass without fixing the reported behaviour, hidden scope, a risk not named. Read the code to check. ok=true only if you found nothing material.`,
  { label: 'critic', phase: 'Critique', schema: CRITIQUE, model: THINK },
)
if (critique && !critique.ok) {
  log(`critic found ${critique.problems.length} problem(s); revising once`)
  const revised = await agent(
    `${brief}

Your previous plan: ${JSON.stringify(plan)}
A critic objected:\n${critique.problems.map((p) => `- ${p}`).join('\n')}
Revise the plan to address each objection (or state in risks why an objection is wrong).`,
    { label: 'revise', phase: 'Plan', schema: PLAN, model: THINK },
  )
  if (revised) plan = revised
}

return { plan, critique, refused: null }
