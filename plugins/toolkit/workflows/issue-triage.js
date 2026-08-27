export const meta = {
  name: 'issue-triage',
  description: 'Is this issue real? Fetch it, verify its claims against HEAD, size it, and propose a decision — no outward actions',
  whenToUse: 'First step of /issue-run, or alone to check whether an issue is still valid',
  phases: [
    { title: 'Fetch', detail: 'issue, comments, linked PRs' },
    { title: 'Investigate', detail: 'code, history, tracker, premise — in parallel' },
    { title: 'Decide', detail: 'decision + evidence + proposed comment' },
  ],
}

// args: { number, repo, cli: 'gh'|'fj' }   (from scripts/issue-ref.sh)
const { number, repo, cli } = args
if (!number || !repo || !cli) throw new Error('args.number, args.repo and args.cli are required (see scripts/issue-ref.sh)')
const ISSUE_REF = `${repo}#${number}`
const forgeHint = `Use the \`${cli}\` CLI for the tracker.`

const ISSUE = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    kind: { type: 'string', enum: ['bug', 'feature', 'chore', 'docs', 'question'] },
    claims: { type: 'array', items: { type: 'string' }, description: 'each factual claim the issue makes, one per entry' },
    expected: { type: 'string' },
    labels: { type: 'array', items: { type: 'string' } },
    linkedPRs: { type: 'array', items: { type: 'object', properties: { number: { type: 'integer' }, state: { type: 'string' }, title: { type: 'string' } }, required: ['number', 'state', 'title'] } },
    commentsSummary: { type: 'string' },
  },
  required: ['title', 'kind', 'claims', 'expected', 'labels', 'linkedPRs', 'commentsSummary'],
}

const EVIDENCE = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    references: { type: 'array', items: { type: 'string' }, description: 'file:line, commit sha, PR/issue number' },
    verdict: { type: 'string', enum: ['supports', 'contradicts', 'inconclusive'] },
  },
  required: ['summary', 'references', 'verdict'],
}

const PREMISE = {
  type: 'object',
  properties: {
    reproduced: { type: 'string', enum: ['yes', 'no', 'not-applicable'] },
    testPath: { type: 'string', description: 'repo-relative path of the reproducing test, empty if none' },
    worktree: { type: 'string', description: 'absolute path of the worktree holding the test, empty if none' },
    testCommand: { type: 'string' },
    detail: { type: 'string' },
  },
  required: ['reproduced', 'testPath', 'worktree', 'testCommand', 'detail'],
}

const TRIAGE = {
  type: 'object',
  properties: {
    decision: { type: 'string', enum: ['fix-small', 'fix-stack', 'close-fixed', 'close-invalid', 'needs-info', 'duplicate'] },
    duplicateOf: { type: 'integer' },
    reasons: { type: 'array', items: { type: 'string' } },
    size: { type: 'object', properties: { files: { type: 'integer' }, lines: { type: 'integer' }, blastRadius: { type: 'string' } }, required: ['files', 'lines', 'blastRadius'] },
    proposedComment: { type: 'string', description: 'comment to post on the issue, proper grammar, with evidence; empty if none' },
    proposedLabels: { type: 'array', items: { type: 'string' } },
  },
  required: ['decision', 'reasons', 'size', 'proposedComment', 'proposedLabels'],
}

phase('Fetch')
const issue = await agent(
  `Fetch issue ${ISSUE_REF} with its labels, comments and any linked or referencing PRs. ${forgeHint}
Extract every factual claim separately (what happens, where, since when, under which conditions). Do not judge them yet.`,
  { label: 'fetch', phase: 'Fetch', schema: ISSUE, effort: 'low' },
)
if (!issue) throw new Error('could not fetch the issue')

phase('Investigate')
const claims = issue.claims.map((c, i) => `${i + 1}. ${c}`).join('\n')
const HDR = `Issue ${ISSUE_REF} "${issue.title}" (${issue.kind})`
const [code, history, tracker, premise] = await parallel([
  () => agent(
    `${HDR} claims:\n${claims}\n
Search the code at HEAD for everything these claims touch. For each claim say whether the code as written supports or contradicts it, with file:line references.`,
    { label: 'code', phase: 'Investigate', schema: EVIDENCE }),
  () => agent(
    `${HDR} claims:\n${claims}\n
Search git history (\`git log -S\`, \`git log --grep\`, blame on the relevant lines) for changes that already addressed or introduced this since the issue was filed. Report commits and whether they landed on the default branch.`,
    { label: 'history', phase: 'Investigate', schema: EVIDENCE }),
  () => agent(
    `${HDR}. ${forgeHint}
Search the tracker for duplicates and related items: same symptom, same file, same feature — open and closed issues, and PRs (merged or not). Linked PRs already known: ${JSON.stringify(issue.linkedPRs)}.`,
    { label: 'tracker', phase: 'Investigate', schema: EVIDENCE, effort: 'low' }),
  () => agent(
    issue.kind === 'bug'
      ? `${HDR} reports a bug. Claims:\n${claims}\nExpected: ${issue.expected}
You are in an isolated worktree at HEAD. Write the smallest test that reproduces the claimed behaviour, in the project's test style, and run it. Report honestly whether it fails for the stated reason. Leave the test file in the worktree (do not commit) and return its path and the worktree path.`
      : `${HDR} requests: ${issue.expected}
Check whether this behaviour already exists (feature flag, undocumented option, partial implementation). Report what exists and what is missing. Return reproduced='not-applicable'.`,
    { label: 'premise', phase: 'Investigate', schema: PREMISE, isolation: issue.kind === 'bug' ? 'worktree' : undefined }),
])

phase('Decide')
const triage = await agent(
  `Decide what to do with ${HDR}.

Claims:\n${claims}\n
Existing labels: ${issue.labels.join(', ') || 'none'}
Discussion so far: ${issue.commentsSummary}

Evidence:
- code: ${JSON.stringify(code)}
- history: ${JSON.stringify(history)}
- tracker: ${JSON.stringify(tracker)}
- premise: ${JSON.stringify(premise)}

Decision rules:
- close-fixed: history or premise shows it is already resolved on the default branch — cite the commit/PR.
- close-invalid: the claims are contradicted by code AND the repro does not fail.
- duplicate: tracker found an open issue covering the same defect — set duplicateOf.
- needs-info: the claims cannot be verified and a repro was not possible; say exactly what is missing.
- fix-small: real, and the fix is one PR under 500 lines.
- fix-stack: real, but larger than one PR or touching several subsystems.
Write proposedComment in proper grammar: what was checked, what was found, what happens next. Do NOT post anything.`,
  { label: 'decide', phase: 'Decide', schema: TRIAGE },
)

return { issue: { ref: ISSUE_REF, number, repo, ...issue }, evidence: { code, history, tracker, premise }, triage }
