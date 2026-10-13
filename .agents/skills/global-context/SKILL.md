---
name: global-context
description: How to change the global rules this marketplace injects into every Claude Code and Codex session — the `instructions/*.md` files in `common`, `oss`, and `toolkit`. Use when the user wants to add, change, reword, move, or remove a global instruction or rule ("add a rule that…", "the agent should always…", "stop telling it to…", "change the global instructions").
---

# Global context

Each of `common`, `oss`, and `toolkit` has a SessionStart hook
(`scripts/session-start.sh`) that injects its instructions into every session as
`<GLOBAL_INSTRUCTIONS source="<plugin> plugin">`. Changing a rule means editing
those files.

## Where a rule goes

Pick the plugin by audience, using the layering in `CLAUDE.md`:

- `common`: universal working hygiene with no repo or tool assumptions.
- `oss`: generic engineering practice that applies to any repo.
- `toolkit`: Cedric's personal preferences and his orchestration engine.

Then pick the file inside `plugins/<plugin>/instructions/`:

- `shared.md`: holds for both hosts. Use it by default.
- `claude.md`: names Claude-only things, such as models (haiku, sonnet, opus),
  agent names, slash commands, `/simplify`, or workflows.
- `codex.md`: the Codex counterpart, using Codex models and tools.

A host-specific rule usually needs an equivalent in the other host's file, or a
deliberate decision that it has none. Do not put Claude agent or model names in
`shared.md`, because Codex sees that file too.

`toolkit/instructions/fleet-brief.md` is not injected. It is the checklist for
code-committing subagents, and `claude.md` points to it through the
`{{FLEET_BRIEF}}` placeholder. Change it when the rule concerns delegated
workers.

If the user means this repository's own conventions rather than the injected
rules, edit `CLAUDE.md` instead.

## How to write the rule

- One bullet per rule. Write it as an imperative and give the reason when it is
  not obvious.
- Before adding a rule, look for an existing bullet that already covers it, in
  this plugin and in the layers below it. Edit or move that bullet; do not add a
  near-duplicate.
- Write calmly: "use X when…", not "CRITICAL: you MUST". Newer models
  overreact to shouting.
- Every line costs context in every session. Keep rules short and remove the
  ones that no longer earn their place.
- The repo is public. Do not include hostnames, IPs, or secret names.

## Ship it

1. Run `python3 -m unittest discover -s tests && python3 scripts/validate.py`.
2. Preview what a host receives, for example
   `plugins/common/scripts/session-start.sh | jq -r .hookSpecificOutput.additionalContext`
   (pass `codex` as the first argument for the Codex output).
3. Commit with a semantic message scoped to the plugin, for example
   `feat(common): …` for a new rule or `fix(toolkit): …` for a correction. Do
   not edit `version`; release-please sets it.
4. If a README table describes the changed rule, update it in the same commit.
