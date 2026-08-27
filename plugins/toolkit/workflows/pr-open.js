export const meta = {
  name: 'pr-open',
  description: 'Open a draft PR for a pushed branch and watch its CI to a verdict — the only outward-facing step',
  whenToUse: 'After fix-small (and optionally adversarial-review) once a human has approved opening the PR',
  phases: [
    { title: 'PR', detail: 'draft PR with problem/approach/tests/Closes' },
    { title: 'CI', detail: 'watch newest run; fix lint/format red once' },
  ],
}

// args: { repoDir?, branch, base, number, repo, cli, title?, summary: {problem, approach, tests}, findings?: [{file,line,title}] }
const { branch, base, number, repo, cli, summary } = args
if (!branch || !base || !number || !repo || !cli || !summary) throw new Error('args.branch, base, number, repo, cli and summary are required — invoke via /issue-run, which supplies them from fix-small')
const AT = args.repoDir ? `Work in the repository checkout at ${args.repoDir} (cd there first; git and CLI commands run against that repo). ` : ''
const THINK = args?.thinkModel ?? 'opus'   // judgment: decide, review, refute, critique
const WORK = args?.workModel ?? 'sonnet'    // mechanical: fetch, search, implement, verify, CI
const findings = (args.findings || []).map((f) => `- [ ] ${f.file}:${f.line} — ${f.title}`).join('\n')

const PR = {
  type: 'object',
  properties: { number: { type: 'integer' }, url: { type: 'string' } },
  required: ['number', 'url'],
}
const CI = {
  type: 'object',
  properties: {
    state: { type: 'string', enum: ['green', 'red', 'pending', 'none'] },
    detail: { type: 'string' },
    lintOnly: { type: 'boolean', description: 'true when the only failures are formatting/lint' },
  },
  required: ['state', 'detail', 'lintOnly'],
}
const FIX = { type: 'object', properties: { pushed: { type: 'boolean' }, detail: { type: 'string' } }, required: ['pushed', 'detail'] }

phase('PR')
const pr = await agent(
  `${AT}Open a DRAFT pull request for branch ${branch} into ${base} on ${repo} using ${cli}.
Title: ${args.title || summary.problem} (no angle brackets, semantic-commit style).
Body, proper grammar:
## Problem
${summary.problem}
## Approach
${summary.approach}
## Tests
${summary.tests}
${findings ? `## Review findings to address\n${findings}\n` : ''}
Closes #${number}
Do not enable auto-merge. Return the PR number and URL.`,
  { label: 'open', phase: 'PR', schema: PR, model: WORK, effort: 'low' },
)
if (!pr) throw new Error('PR was not opened')

phase('CI')
const watch = (label) => agent(
  `${AT}${AT}Watch CI for PR #${pr.number} on ${repo} (${cli}) until the NEWEST run finishes; ignore superseded runs that still show red. Report the state and whether every failure is formatting/lint only.`,
  { label, phase: 'CI', schema: CI, model: WORK, effort: 'low' },
)
let ci = await watch('ci')
let lintFix = null
if (ci?.state === 'red' && ci.lintOnly) {
  lintFix = await agent(
    `${AT}CI on PR #${pr.number} is red only for formatting/lint: ${ci.detail}
In this isolated worktree: \`git fetch origin && git checkout ${branch}\`, run the project's formatter/linter, commit as "style: apply formatter", push.`,
    { label: 'lint-fix', phase: 'CI', schema: FIX, isolation: 'worktree', model: WORK, effort: 'low' },
  )
  if (lintFix?.pushed) ci = await watch('ci#2')
}

return { pr: pr.number, url: pr.url, ci, lintFix }
