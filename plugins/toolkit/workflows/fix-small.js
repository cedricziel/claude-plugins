export const meta = {
  name: 'fix-small',
  description: 'Implement a single-PR fix for an issue in an isolated worktree (TDD, lint, /simplify, semantic commits), verify with fresh eyes, push the branch — no PR',
  whenToUse: 'After issue-triage decided fix-small; or alone for any small, well-understood change',
  phases: [
    { title: 'Implement', detail: 'one agent, isolated worktree' },
    { title: 'Verify', detail: 'fresh-eyes check, one repair round' },
  ],
}

// args: { repoDir?, number, repo, base, issue: {title, expected, claims[]}, premise?: {testPath, worktree, testCommand}, branch?, fleetBrief, maxLines?, implementModel? }
const { number, repo, base, issue, premise, fleetBrief } = args
if (!number || !repo || !base || !issue || !fleetBrief) throw new Error('args.number, repo, base, issue and fleetBrief are required')
const branch = args.branch || `fix/${number}-${issue.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40)}`
const AT = args.repoDir ? `Work in the repository checkout at ${args.repoDir} (cd there first; git and CLI commands run against that repo). ` : ''
const MAX = args.maxLines ?? 500

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
  },
  required: ['ok', 'problems', 'testsRun'],
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
${feedback ? `A verifier rejected the previous attempt on branch ${branch}; fix these and push again:\n${feedback}` : ''}
Rules: minimal change for this issue only; TDD; run the project's lint/format; apply the simplify pass; semantic commit messages in proper grammar; never mention Claude in commits. Stop and report blocked if the diff would exceed ${MAX} lines or the fix needs a design decision.
Push the branch to origin when done.`

phase('Implement')
let impl = await agent(implementPrompt(''), { label: 'implement', phase: 'Implement', schema: IMPL, isolation: 'worktree', model: args.implementModel })
if (!impl || impl.blocked) return { branch, impl, verify: null, ok: false }

phase('Verify')
const verifyPrompt = () => `${AT}Fresh eyes. In an isolated worktree, \`git fetch origin && git checkout ${branch}\`.
Check, with commands, not by reading the report: the tests named below pass; the fix actually addresses ${repo}#${number} "${issue.title}"; every commit message is semantic and mentions no AI; the diff against origin/${base} is under ${MAX} lines; no files outside ${JSON.stringify(impl.filesTouched)} changed; the project's lint/format is clean.
Implementer's report: ${JSON.stringify(impl)}`
let verify = await agent(verifyPrompt(), { label: 'verify', phase: 'Verify', schema: VERIFY, isolation: 'worktree', model: 'sonnet' })

if (verify && !verify.ok) {
  log(`verifier found ${verify.problems.length} problem(s); one repair round`)
  const repaired = await agent(implementPrompt(verify.problems.map((p) => `- ${p}`).join('\n')),
    { label: 'repair', phase: 'Implement', schema: IMPL, isolation: 'worktree', model: args.implementModel })
  if (repaired && !repaired.blocked) {
    impl = repaired
    verify = await agent(verifyPrompt(), { label: 'verify#2', phase: 'Verify', schema: VERIFY, isolation: 'worktree', model: 'sonnet' })
  }
}

return { branch, base, impl, verify, ok: Boolean(verify?.ok) }
