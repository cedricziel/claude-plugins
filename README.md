# claude-plugins

Cedric Ziel's [Claude Code](https://docs.claude.com/en/docs/claude-code) plugin marketplace.

## Install

```
/plugin marketplace add cedricziel/claude-plugins
/plugin install toolkit@cedricziel
```

## Plugins

### toolkit

Everything I use day to day, in one plugin.

**Skills** (loaded automatically when relevant)

| Skill | Purpose |
|---|---|
| `commit-discipline` | Atomic semantic commits, small always-shippable PRs |
| `git-stacked-prs` | Split large changes into a stack of reviewable PRs |
| `writing-tests` | Test-writing principles from the TDD canon |
| `coderabbit` | Working with CodeRabbit reviews on PRs |
| `forgejo-cli` | Using `fj` against Forgejo/Codeberg instances |
| `signaldb-observe` | Instrument an app with OpenTelemetry and ship to SignalDB |
| `dashboarding` | Designing and reviewing operational dashboards |

**Hooks**

| Event | What it does |
|---|---|
| `PostToolUse` (Edit/Write) | Nudges when source changes come without test changes |
| `Stop` | Blocks finishing while the project's test suite is red (fails open on environment errors) |
| `UserPromptSubmit` | Reminds to rebase when the branch has fallen behind the default branch |

Knobs and off-switches are documented in the headers of `plugins/toolkit/scripts/*.sh`.
Disable per repo with `.no-rebase-nudge`; override the test command with `.tdd-test-cmd`.

**Commands**

`/issue <number>` (analyze and fix a GitHub issue), `/issue-create <context>`, `/pr-review <number>`.

## Development

```
python3 -m unittest discover -s tests
python3 scripts/validate.py
claude --plugin-dir plugins/toolkit   # local smoke test
```

## License

MIT
