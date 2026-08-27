export const meta = {
  name: 'issue-resolve',
  description: 'Apply a triage decision to the tracker: comment, label, close or mark duplicate — the outward-facing step for non-fix decisions',
  whenToUse: 'After issue-triage returned close-fixed, close-invalid, duplicate or needs-info and a human approved it',
  phases: [{ title: 'Resolve', detail: 'comment, label, close' }],
}

// args: { repoDir?, number, repo, cli, decision, proposedComment, proposedLabels?: [], duplicateOf? }
const { number, repo, cli, decision, proposedComment } = args
if (!number || !repo || !cli || !decision || !proposedComment) throw new Error('args.number, repo, cli, decision and proposedComment are required')
const AT = args.repoDir ? `Work in the repository checkout at ${args.repoDir} (cd there first; git and CLI commands run against that repo). ` : ''
const CLOSES = { 'close-fixed': 'completed', 'close-invalid': 'not planned', duplicate: 'not planned' }
const closeAs = CLOSES[decision]
if (!closeAs && decision !== 'needs-info') throw new Error(`issue-resolve does not handle decision '${decision}'`)

const RESULT = {
  type: 'object',
  properties: {
    commented: { type: 'boolean' },
    labelsApplied: { type: 'array', items: { type: 'string' } },
    closed: { type: 'boolean' },
    detail: { type: 'string' },
  },
  required: ['commented', 'labelsApplied', 'closed', 'detail'],
}

phase('Resolve')
const result = await agent(
  `${AT}On issue ${repo}#${number}, using the \`${cli}\` CLI:
1. Post this comment verbatim:\n---\n${proposedComment}\n---
2. Apply labels ${JSON.stringify(args.proposedLabels || [])} — only those that already exist in the repo; skip the rest and say which.
${closeAs ? `3. Close the issue as "${closeAs}"${args.duplicateOf ? ` (duplicate of #${args.duplicateOf})` : ''}.` : '3. Leave the issue open.'}
Report exactly what happened.`,
  { label: `resolve:${decision}`, phase: 'Resolve', schema: RESULT, effort: 'low' },
)
return { decision, ...result }
