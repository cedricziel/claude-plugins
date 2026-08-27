# claude-plugins

Marketplace `cedricziel`; single plugin `plugins/toolkit`.

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
- **Explicit-only triggers.** A skill that launches a workflow fires only on its
  slash command or a literal ask, states its agent cost, and lists what it does
  NOT trigger on.

## Conventions

- Bump `version` in both `plugins/toolkit/.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json` on every change; breaking removals bump minor.
- `python3 -m unittest discover -s tests && python3 scripts/validate.py` before commit.
- Public repo: no hostnames, IPs, or secret-manager item names.
- Hook scripts fail open and keep state under `~/.claude/hooks/`, never in the plugin dir.
- Ship it: push, then `claude plugin marketplace update cedricziel && claude plugin update toolkit@cedricziel`.
