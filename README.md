# claude-plugins

Cedric Ziel's [Claude Code](https://docs.claude.com/en/docs/claude-code) plugin marketplace.

## Install

```
/plugin marketplace add cedricziel/claude-plugins
/plugin install toolkit@cedricziel
```

## Plugins

### toolkit

Everything I use day to day, in one plugin — including my global working rules, so a fresh machine only needs the plugin, not a synced `~/.claude/CLAUDE.md`. `instructions/fleet-brief.md` is the checklist handed to code-committing subagents.

**Skills** (loaded automatically when relevant)

| Skill | Purpose |
|---|---|
| `commit-discipline` | Atomic semantic commits, small always-shippable PRs |
| `git-stacked-prs` | Split large changes into a stack of reviewable PRs |
| `writing-tests` | Test-writing principles from the TDD canon |
| `adversarial-review` | `/adversarial-review [PR\|branch]` — runs the multi-agent workflow below |
| `issue-run` | `/issue-run <ref> [--review] [--yes]` — sequences issue-triage → (issue-resolve \| fix-small → (adversarial-review) → pr-open) with human gates between them |
| `coderabbit` | Working with CodeRabbit reviews on PRs |
| `forgejo-cli` | Using `fj` against Forgejo/Codeberg instances |
| `signaldb-observe` | Instrument an app with OpenTelemetry and ship to SignalDB |
| `dashboarding` | Designing and reviewing operational dashboards |

**Hooks**

| Event | What it does |
|---|---|
| `SessionStart` | Injects `instructions/global.md` (working rules + Caveman Compression) as context; re-injected after compaction. Disable with `TOOLKIT_INSTRUCTIONS_DISABLE=1` |
| `PostToolUse` (Edit/Write) | Auto-formats the edited file (cargo fmt/rustfmt, goimports/gofmt, swiftformat/swift-format, dart, ruff/black, prettier) — fail-open |
| `PostToolUse` (Edit/Write) | Nudges when source changes come without test changes |
| `Stop` | Blocks finishing while the project's test suite is red (fails open on environment errors) |
| `UserPromptSubmit` | Reminds to rebase when the branch has fallen behind the default branch |

Knobs and off-switches are documented in the headers of `plugins/toolkit/scripts/*.sh`.
Disable per repo with `.no-rebase-nudge` / `.no-format-hook`; override the test command with `.tdd-test-cmd`.

**Workflows**

| Workflow | What it does |
|---|---|
| `adversarial-review` | 5 review lenses in parallel → each finding faces 3 refuters with distinct angles, survives on majority → critic names what was missed. Reviewers default to `sonnet`. |
| `issue-triage` | Fetch an issue, verify its claims against HEAD (code, history, tracker, repro test in a worktree), size it, propose a decision + comment. No outward actions. |
| `fix-small` | One-PR fix in an isolated worktree (TDD from the repro test, lint, simplify, semantic commits), fresh-eyes verification with one repair round, push. No PR. |
| `pr-open` | Draft PR with problem/approach/tests/`Closes #N`, watch the newest CI run, fix a lint/format red once. |
| `issue-resolve` | Apply a non-fix triage decision: comment, label, close / mark duplicate. |

Workflows are composable: leaves never call other workflows; skills sequence them and stop for approval between runs (see `CLAUDE.md`).

**Commands**

`/issue-create <context>`, `/pr-review <number>`. (`/issue` was replaced by `/issue-run`.)

## Development

```
python3 -m unittest discover -s tests
python3 scripts/validate.py
claude --plugin-dir plugins/toolkit   # local smoke test
```

## License

MIT
