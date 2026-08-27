export const meta = {
  name: 'pr-watch',
  description: 'Babysit an open PR: classify each new review comment (apply / push back once / needs human), apply fixes in one push per round, re-request review, flip draft→ready when nothing is left — bounded rounds, never merges',
  whenToUse: 'After pr-open once a human approved it; or alone on any PR the user owns. Args: { number: PR number, repo, cli, branch, base, repoDir?, maxRounds? }',
  phases: [
    { title: 'Collect', detail: 'new review threads + CI state' },
    { title: 'Classify', detail: 'apply / push back / escalate' },
    { title: 'Apply', detail: 'one push per round, reply, resolve, re-request' },
  ],
}

// args: { repoDir?, number (PR), repo, cli, branch, base, maxRounds?, issueNumber? }
const THINK = args?.thinkModel ?? 'opus'   // judgment: decide, review, refute, critique
const WORK = args?.workModel ?? 'sonnet'    // mechanical: fetch, search, implement, verify, CI
const { number, repo, cli, branch, base } = args
if (!number || !repo || !cli || !branch || !base) throw new Error('args.number (PR), repo, cli, branch and base are required — invoke via /issue-run, which supplies them from pr-open')
const AT = args.repoDir ? `Work in the repository checkout at ${args.repoDir} (cd there first; git and CLI commands run against that repo). ` : ''
const MAX_ROUNDS = args.maxRounds ?? 3
const BUDGET_FLOOR = 60_000   // one classify + one apply round

const THREADS = {
  type: 'object',
  properties: {
    threads: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          author: { type: 'string' },
          bot: { type: 'boolean' },
          file: { type: 'string' },
          line: { type: 'integer' },
          body: { type: 'string' },
          suggestion: { type: 'string', description: 'committable suggestion text if the reviewer offered one, else empty' },
        },
        required: ['id', 'author', 'bot', 'file', 'line', 'body', 'suggestion'],
      },
    },
    reviewState: { type: 'string', enum: ['approved', 'changes_requested', 'commented', 'none'] },
    ci: { type: 'string', enum: ['green', 'red', 'pending', 'none'] },
    isDraft: { type: 'boolean' },
    merged: { type: 'boolean' },
  },
  required: ['threads', 'reviewState', 'ci', 'isDraft', 'merged'],
}
const DECISIONS = {
  type: 'object',
  properties: {
    decisions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          action: { type: 'string', enum: ['apply', 'push-back', 'escalate'] },
          reason: { type: 'string', description: 'for push-back: the evidence (file:line); for escalate: the decision a human must make' },
          change: { type: 'string', description: 'for apply: what to change, concretely' },
        },
        required: ['id', 'action', 'reason', 'change'],
      },
    },
  },
  required: ['decisions'],
}
const APPLIED = {
  type: 'object',
  properties: {
    pushed: { type: 'boolean' },
    commits: { type: 'array', items: { type: 'string' } },
    replied: { type: 'array', items: { type: 'string' }, description: 'thread ids replied to' },
    resolved: { type: 'array', items: { type: 'string' } },
    detail: { type: 'string' },
  },
  required: ['pushed', 'commits', 'replied', 'resolved', 'detail'],
}

const seen = new Set()
const rounds = []
let final = null
let refused = null

for (let round = 1; round <= MAX_ROUNDS; round++) {
  if (budget.total && budget.remaining() < BUDGET_FLOOR) { refused = 'budget exhausted before the next round'; log(refused); break }

  phase('Collect')
  const state = await agent(
    `${AT}Using the \`${cli}\` CLI, collect the state of PR #${number} on ${repo}: every UNRESOLVED review thread (inline and top-level review comments, bots such as CodeRabbit included; for CodeRabbit prefer its structured output if the CLI/MCP is available), the latest review decision, the newest CI run's state, draft status, merged status. Include any committable suggestion text verbatim.`,
    { label: `collect#${round}`, phase: 'Collect', schema: THREADS, model: WORK, effort: 'low' },
  )
  if (!state) break
  final = state
  if (state.merged) { log('PR merged; done'); break }
  const fresh = state.threads.filter((t) => !seen.has(t.id))
  fresh.forEach((t) => seen.add(t.id))
  if (fresh.length === 0 && state.ci !== 'red') { log(`round ${round}: nothing new`); break }

  if (fresh.length === 0) {
    // Only CI is red: no judgment needed, just the cheap lint fix from pr-open.
    const fix = await agent(
      `${AT}In an isolated worktree: \`git fetch origin && git checkout ${branch}\`. CI on PR #${number} (${repo}) is red. If the newest run fails only on formatting/lint, run the project's formatter/linter, commit as "style: apply formatter", push. Any other red: do nothing and report.`,
      { label: `lint-fix#${round}`, phase: 'Apply', schema: APPLIED, model: WORK, isolation: 'worktree', effort: 'low' },
    )
    rounds.push({ round, fresh: 0, decisions: [], applied: fix })
    if (!fix?.pushed) break
    continue
  }

  phase('Classify')
  const { decisions } = (await agent(
    `${AT}PR #${number} on ${repo} (branch ${branch} → ${base}) has ${fresh.length} new review thread(s):
${JSON.stringify(fresh, null, 1)}
CI is ${state.ci}.

For each thread decide exactly one action:
- apply: the comment is right, or is a low-risk suggestion (style, naming, a committable suggestion) — describe the change.
- push-back: you can show with file:line evidence that the comment is wrong, out of scope for this PR, or already handled. Give the evidence; this reply is posted ONCE and never argued further.
- escalate: it asks for a design decision, changes scope, contradicts the issue, or you are not confident. Name the decision the human must make.
Reviewers reject more than half of bot suggestions for being invalid or out of scope; do not apply to please the reviewer. Read the code before deciding.`,
    { label: `classify#${round}`, phase: 'Classify', schema: DECISIONS, model: THINK },
  )) || { decisions: [] }

  phase('Apply')
  const applied = await agent(
    `${AT}In an isolated worktree: \`git fetch origin && git checkout ${branch}\`.
Decisions for PR #${number} (${cli}):
${JSON.stringify(decisions, null, 1)}
Thread locations: ${JSON.stringify(fresh.map(({ id, file, line }) => ({ id, file, line })))}
${state.ci === 'red' ? 'CI is red: if the newest run fails only on formatting/lint, fix that too.' : ''}

1. Make every 'apply' change; run the project's tests and lint/format; commit in semantic commits (proper grammar, no AI mention); push ONCE at the end.
2. For each 'apply' thread: reply "Applied in <sha>: <one line>" and resolve the thread.
3. For each 'push-back' thread: post the evidence as a reply, once. Do NOT resolve it — the reviewer decides.
4. For each 'escalate' thread: reply "Needs a maintainer decision: <the decision>". Do not resolve.
5. If anything was pushed, re-request review from every human reviewer who had requested changes.
Never force-push, never delete branches, never merge, never mark ready for review.`,
    { label: `apply#${round}`, phase: 'Apply', schema: APPLIED, model: WORK, isolation: 'worktree' },
  )
  rounds.push({ round, fresh: fresh.length, decisions, applied })
  if (!applied?.pushed) break   // nothing changed → a further round would only re-read the same state
}

const escalations = rounds.flatMap((r) => r.decisions.filter((d) => d.action === 'escalate'))
// final.threads was collected BEFORE the last apply round, so subtract what that round resolved.
const unresolvedThreads = final ? final.threads.filter((t) => !rounds.some((r) => r.applied?.resolved?.includes(t.id))).length : null
const readyForReview = Boolean(final && !final.merged && final.isDraft && final.ci === 'green' && escalations.length === 0 && unresolvedThreads === 0)

if (readyForReview) {
  await agent(`${AT}Mark PR #${number} on ${repo} ready for review using ${cli}, and re-request review from the assigned reviewers. Do nothing else.`,
    { label: 'ready', phase: 'Apply', schema: { type: 'object', properties: { done: { type: 'boolean' } }, required: ['done'] }, model: WORK, effort: 'low' })
}

return { pr: number, refused, rounds, escalations, ci: final?.ci ?? 'unknown', reviewState: final?.reviewState ?? 'unknown', merged: Boolean(final?.merged), readyForReview, unresolvedThreads }
