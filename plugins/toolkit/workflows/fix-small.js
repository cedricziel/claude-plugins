export const meta = {
  name: 'fix-small',
  description: 'Implement a single-PR fix for an issue in an isolated worktree (TDD, lint, /simplify, semantic commits), verify with fresh eyes, push the branch — no PR',
  whenToUse: 'After issue-triage decided fix-small; or alone for any small, well-understood change',
  phases: [
    { title: 'Implement', detail: 'one agent, isolated worktree' },
    { title: 'Verify', detail: 'fresh-eyes check, one repair round' },
  ],
}

// args: { repoDir?, number, repo, base, issue: {title, kind, expected, claims[]}, premise?: {reproduced, testPath, worktree, testCommand}, plan?: fix-plan output, branch?, fleetBrief, maxLines?, implementModel? }
const { number, repo, base, issue, premise, fleetBrief } = args
if (!number || !repo || !base || !issue || !fleetBrief) throw new Error('args.number, repo, base, issue and fleetBrief are required — invoke via /issue-run, which supplies them from issue-triage')
const branch = args.branch || `fix/${number}-${issue.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40)}`
const AT = args.repoDir ? `Work in the repository checkout at ${args.repoDir} (cd there first; git and CLI commands run against that repo). ` : ''
const THINK = args?.thinkModel ?? 'opus'   // judgment: decide, review, refute, critique
const WORK = args?.workModel ?? 'sonnet'    // mechanical: fetch, search, implement, verify, CI
const MAX = args.maxLines ?? 500
const BUDGET_FLOOR = 40_000   // one verify call plus its report
if (issue.kind === 'bug' && premise && premise.reproduced === 'no') {
  return { branch, base, impl: null, verify: null, ok: false, refused: 'the bug did not reproduce at HEAD; fixing an unreproduced bug is guesswork — re-triage or ask for a repro' }
}
const plan = args.plan ? `Follow this approved plan; deviate only if the code proves it wrong, and say so in notes:\n${JSON.stringify(args.plan)}\n` : ''

const IMPL = {
  type: 'object',
  properties: {
    commits: { type: 'array', items: { type: 'string' } },
    diffLines: { type: 'integer' },
    testsRun: { type: 'string' },
    filesTouched: { type: 'array', items: { type: 'string' } },
    blocked: { type: 'string', description: 'why you stopped, empty if you finished' },
    problem: { type: 'string', description: 'one paragraph: what was wrong, for the PR body' },
    approach: { type: 'string', description: 'one paragraph: what the fix does and why this way, for the PR body' },
    notes: { type: 'string', description: 'trades made, anything unverified' },
  },
  required: ['commits', 'diffLines', 'testsRun', 'filesTouched', 'blocked', 'problem', 'approach', 'notes'],
}

const VERIFY = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' },
    problems: { type: 'array', items: { type: 'string' } },
    testsRun: { type: 'string' },
    independentTest: { type: 'string', description: 'path of the extra test you wrote from the issue text alone, and whether it passed' },
    gaming: { type: 'string', description: 'evidence the change targets the test rather than the behaviour (special-cased inputs, weakened or deleted assertions, skipped tests); empty if none' },
  },
  required: ['ok', 'problems', 'testsRun', 'independentTest', 'gaming'],
}

const repro = premise?.testPath
  ? `A reproducing test already exists at ${premise.worktree}/${premise.testPath} (run with: ${premise.testCommand}). Copy it into your worktree first; it must go red before your fix and green after.`
  : 'Start with a failing test that pins the reported behaviour.'

const implementPrompt = (feedback) => `${AT}Read ${fleetBrief} first and follow it.
You are in an isolated worktree. Run \`git fetch origin\` and create branch ${branch} from origin/${base}.
Fix issue ${repo}#${number}: "${issue.title}".
Expected: ${issue.expected}
Claims: ${issue.claims.map((c) => `- ${c}`).join('\n')}
${repro}
${plan}${feedback ? `A verifier rejected the previous attempt on branch ${branch}; fix these and push again:\n${feedback}` : ''}
Rules: minimal change for this issue only; TDD; run the project's lint/format; apply the simplify pass; semantic commit messages in proper grammar; never mention Claude in commits. Stop and report blocked if the diff would exceed ${MAX} lines or the fix needs a design decision.
Push the branch to origin when done.`

phase('Implement')
let impl = await agent(implementPrompt(''), { label: 'implement', phase: 'Implement', schema: IMPL, isolation: 'worktree', model: args.implementModel ?? WORK })
if (!impl || impl.blocked) return { branch, base, impl, verify: null, ok: false, refused: impl?.blocked || 'implementer returned nothing' }

if (budget.total && budget.remaining() < BUDGET_FLOOR) return { branch, base, impl, verify: null, ok: false, refused: 'budget exhausted before verification' }

phase('Verify')
const verifyPrompt = () => `${AT}Fresh eyes. In an isolated worktree, \`git fetch origin && git checkout ${branch}\`.
Check, with commands, not by reading the report: the tests named below pass; every commit message is semantic and mentions no AI; the diff against origin/${base} is under ${MAX} lines; no files outside ${JSON.stringify(impl.filesTouched)} changed; the project's lint/format is clean.
Then, WITHOUT reading the implementer's tests first, write one additional test from the issue text alone ("${issue.expected}") and run it — a fix that only satisfies the tests its author wrote is the most common way agent patches are wrong. Keep the test in the worktree (do not commit) and report its path and result.
Finally look for test-gaming: inputs special-cased to match the test, assertions weakened or removed, tests skipped or marked expected-failure. Any of these is a problem regardless of green tests.
Implementer's report: ${JSON.stringify(impl)}`
let verify = await agent(verifyPrompt(), { label: 'verify', phase: 'Verify', schema: VERIFY, isolation: 'worktree', model: WORK })

if (verify && !verify.ok) {
  log(`verifier found ${verify.problems.length} problem(s); one repair round`)
  const repaired = await agent(implementPrompt(verify.problems.map((p) => `- ${p}`).join('\n')),
    { label: 'repair', phase: 'Implement', schema: IMPL, isolation: 'worktree', model: args.implementModel ?? WORK })
  if (repaired && !repaired.blocked) {
    impl = repaired
    verify = await agent(verifyPrompt(), { label: 'verify#2', phase: 'Verify', schema: VERIFY, isolation: 'worktree', model: WORK })
  }
}

return { branch, base, impl, verify, ok: Boolean(verify?.ok), refused: null }
