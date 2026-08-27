# Claude plugin marketplace bootstrap — design

Date: 2026-08-27

## Goal

Publish the personal Claude Code configuration living in `~/.claude`
(skills, slash commands, hooks) as a single installable plugin through a
self-owned marketplace on GitHub, so it can be installed on any machine
with `/plugin marketplace add cedricziel/claude-plugins`.

## Scope

- Repository: `github.com/cedricziel/claude-plugins`, public, MIT.
- Marketplace name: `cedricziel`.
- One plugin: `toolkit` (`toolkit@cedricziel`), containing everything.
- Follow-up (separate task, after install is verified): remove the
  duplicated skills, commands and hook wiring from `~/.claude`.

Out of scope: `herdr-agent-state.sh` (managed by an external tool),
the `opentelemetry-instrumentation` plugin (stays in its own repo).

## Repository layout

```
.claude-plugin/marketplace.json
plugins/toolkit/
  .claude-plugin/plugin.json
  skills/<name>/SKILL.md [+ references/]
  commands/<name>.md
  hooks/hooks.json
  scripts/tdd-hook.sh
  scripts/rebase-hook.sh
scripts/validate.py          # structural validation of marketplace + plugin
.github/workflows/validate.yml
README.md
LICENSE
docs/superpowers/specs/
```

## Plugin contents

Skills (from `~/.claude/skills`): coderabbit, commit-discipline,
dashboarding, forgejo-cli, git-stacked-prs, signaldb-observe,
writing-tests.

Commands (from `~/.claude/commands`), renamed where the local name was
namespaced:

| local file | plugin command |
|---|---|
| `project:issue.md` | `issue.md` |
| `project:issue:create.md` | `issue-create.md` |
| `project:pull-request:review.md` | `pr-review.md` |
| all others | same basename |

Hooks (`hooks/hooks.json`), commands referenced via
`${CLAUDE_PLUGIN_ROOT}/scripts/…`:

| event | matcher | script | timeout |
|---|---|---|---|
| PostToolUse | `Edit\|Write` | `tdd-hook.sh edit-check` | 15 s |
| Stop | — | `tdd-hook.sh stop-check` | 300 s |
| UserPromptSubmit | — | `rebase-hook.sh` | 30 s |

Hook state directories stay under `~/.claude/hooks/.tdd-state` and
`~/.claude/hooks/.rebase-state` (the plugin cache directory is replaced
on update, so it is not a stable home for state). Existing env-var knobs
and off-switch files are unchanged.

## Portability rules

The repository is public. Before copying, scrub personal references from
skills: concrete hostnames (`*.58lab.org`), 1Password item names, local
usernames and absolute `/Users/…` paths. Replace with generic
placeholders (`<host>`, `<owner>/<repo>`); keep the guidance intact.

## Validation

- `scripts/validate.py` checks: `marketplace.json` schema (name, owner,
  plugins[] with name/source/description/version), each plugin's
  `plugin.json`, every `SKILL.md` has frontmatter with `name` and
  `description`, every command file is non-empty Markdown, `hooks.json`
  parses and every referenced script exists and is executable.
- CI runs the validator on push and pull request.
- Local smoke test: `claude --plugin-dir plugins/toolkit` lists the
  skills, commands and hooks.
- End-to-end: `/plugin marketplace add cedricziel/claude-plugins`,
  `/plugin install toolkit@cedricziel`.

## Error handling

Validator exits non-zero with one line per problem. Hook scripts keep
their existing fail-open behaviour (no-op outside git repos or on
environment errors).
