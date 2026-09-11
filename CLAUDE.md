# claude-plugins

Marketplace `cedricziel`; four plugins layered by audience: `common` (universal
hygiene, no repo/tool assumptions) → `oss` (generic engineering practice, reusable
in any repo, OSS or not) and `skills` (generic tool-integration skills — CodeRabbit,
Forgejo, dashboards — reusable by anyone who uses that tool, not just Cedric) →
`toolkit` (Cedric's personal layer: instructions, SignalDB integration, the GitHub
issue/PR orchestration engine). `toolkit` depends on `common`, `oss`, and `skills`;
`oss` and `skills` each depend on `common` and `coderabbit@claude-plugins-official`.
A skill or workflow belongs in
`oss` or `skills`, not `toolkit`, unless it's personal-instruction content, tied to
Cedric's own infrastructure (SignalDB), or part of the orchestration engine
(`workflows/`, `issue-run`, `pr-review`, `deep-review`, `adversarial-review`,
`code-review`). Between `oss` and `skills`: `oss` is engineering practice with no
tool dependency; `skills` is a how-to-use-this-tool guide (CodeRabbit, Forgejo,
dashboards) that anyone using that tool could reuse.

## Workflows are composable

- **One question per workflow.** Each file in `workflows/` answers one question a
  person would ask anyway ("is this issue real?", "does this survive review?",
  "is CI green?") and must be worth running on its own.
- **Leaves and orchestrators.** A leaf never calls `workflow()`. An orchestrator
  may call leaves (nesting is limited to one level). Never make an orchestrator
  call another orchestrator — sequence them from a skill instead.
- **Gates live at the seams.** Anything outward-facing (comment, close, open a
  PR, merge) happens in a separate workflow, so the skill can stop for human
  approval between runs. `--yes` skips the gates; it never changes the leaves.
- **Decisions are proposed, not taken.** Triage returns a decision plus evidence
  and proposed text; posting is a later step.
- **Invoke by namespaced name.** Plugin workflows register as `toolkit:<name>`
  (also as a Skill entry, so they can be invoked with a raw string arg — accept
  one). Fall back to `scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/<name>.js"`
  when the session loaded the plugin before the workflow existed. Pass `repoDir`
  when the session cwd is not the target repo.
- **Explicit-only triggers.** A skill that launches a workflow fires only on its
  slash command or a literal ask, states its agent cost, and lists what it does
  NOT trigger on.

## Conventions

- Every leaf returns `refused: null` on success or a reason string on any early exit,
  and names its budget guard `BUDGET_FLOOR` with a comment saying what it protects.
- Every `agent()` call names its model: `WORK` (sonnet) for mechanical steps, `THINK`
  (opus) for judgment. Never inherit the session model — that silently means fable.

- Bump `version` in both the plugin's own `.claude-plugin/plugin.json` and its
  entry in `.claude-plugin/marketplace.json` on every change; breaking removals
  bump minor. Moving a skill between plugins changes its namespace (`toolkit:x`
  → `oss:x`), so bump minor on both the plugin losing it and the plugin gaining it.
- `python3 -m unittest discover -s tests && python3 scripts/validate.py` before commit.
- Public repo: no hostnames, IPs, or secret-manager item names.
- Hook scripts fail open and keep state under `~/.claude/hooks/`, never in the plugin dir.
- Ship it: push, then `claude plugin marketplace update cedricziel && claude plugin update toolkit@cedricziel`.
