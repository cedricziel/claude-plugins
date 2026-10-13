---
name: skill-maintenance
description: "What makes an agent-skill change worth keeping, and how a skill is laid out: when to add, edit, or delete a skill, which scope it belongs in, how to write the description, and where references and scripts live and how SKILL.md links them. Use whenever you are about to create, edit, or remove a skill (project, user, or plugin), or review a diff that touches one. Not for writing the skill's subject matter itself (use the relevant domain skill)."
---

# Skill maintenance

A skill is context an agent loads on purpose. Every line costs attention on each load,
and a wrong line is worse than a missing one. Change a skill only when the change will
make the next run better.

## When to change one

**Add or edit when** a lesson will recur: the user corrected the same thing twice, a
mistake cost real time, or a procedure had to be rediscovered. Prefer a focused edit to
an existing skill. Add a new skill only for a distinct, repeatable job.

**Delete when** content is wrong, stale, unused, or now covered by the tool itself or an
always-on rule. Check callers first (`grep -r '<skill-name>'` across skills, workflows,
and instructions).

**Leave it alone when** the lesson happened once, is specific to one conversation or PR,
or only restates the tool's own docs or `--help`.

## Scope

Pick the narrowest scope that helps:

| Scope   | Holds                                         | Lives in                                                                                              |
| ------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| project | this repo's procedures, commands, quirks      | `.claude/skills/` (Claude Code) or `.agents/skills/` (Codex) in the repo, shipped in the same PR as the code it describes |
| user    | one person's preferences across their repos   | `~/.claude/skills/` or `~/.agents/skills/`; local only, no PR                                                                |
| plugin  | reusable behavior for everyone using a plugin | the plugin's `skills/` directory, in its own PR                                                       |

Never put secrets, hostnames, IPs, or personal details in a project or plugin skill.

## Good and bad content

Good:

- Commands and paths that were run in this session, not recalled.
- One job per skill. Short imperative steps, with the reason when it is not obvious.
- Checkable rules: "each task names its failing test", not "write good tests".
- Calm wording: "use X when…". Shouting ("CRITICAL", "MUST") makes models overreact.

Bad:

- Anecdotes ("in PR 42 we…"), one-off fixes, conversation-specific detail.
- Restating always-on instructions or another skill. Link to it instead.
- Vague advice ("be careful with X") that no one can act on.
- Silent changes. Name every skill you touched in the report or PR.
- Several agents editing skills at once. Workers report what they learned; the
  orchestrator applies the changes once.

## The description

The description decides whether the skill loads, so write it for that:

- Put the main use case first. Claude Code truncates `description` plus `when_to_use`
  at 1,536 characters in the skill listing.
- Say when to trigger and, when misfires are likely, when not to.
- Describe the job, not the file ("Plan a stacked PR series", not "Notes on git").

## Layout

```text
my-skill/
├── SKILL.md          # required: purpose, steps, links to everything below
├── references/       # detail loaded only when a step needs it
│   └── api.md
├── scripts/          # code the agent runs, not reads
│   └── check.sh
└── assets/           # templates and files the skill copies or fills in
```

- Keep `SKILL.md` under 500 lines; move detail out before it grows past that.
- **References** hold material only some runs need: API payloads, long tables, edge
  cases. Link each one from the step that needs it with a relative Markdown link and
  say when to read it: "For error codes, read [references/api.md](references/api.md)."
  A reference no step links to is never loaded; delete it or link it.
- **Scripts** hold deterministic work that would otherwise be retyped each run:
  parsing, validation, multi-step CLI calls. Make them executable, give them a usage
  line, and have them fail with a clear message. The agent runs them, so their source
  costs no context.
- Call scripts by absolute path so they work from any working directory. In Claude Code,
  use `${CLAUDE_SKILL_DIR}/scripts/check.sh` (substituted in the skill body and in
  `allowed-tools` rules, e.g. `Bash(${CLAUDE_SKILL_DIR}/scripts/check.sh *)`). Codex does
  not substitute variables; there, give the path relative to `SKILL.md` and resolve it
  against the skill's directory.
- A script shared by several skills in one plugin goes in the plugin's own `scripts/`
  directory, called as `${CLAUDE_PLUGIN_ROOT}/scripts/<name>`. Keep a script inside the
  skill when only that skill uses it.

## Before you finish

- Every command in the skill ran in this session, or is marked as unverified.
- Every reference and script is linked from `SKILL.md`, and every link resolves.
- The repo's validator and tests pass (for example `python3 scripts/validate.py`).
- The report or PR names each skill added, changed, or deleted, and why.
