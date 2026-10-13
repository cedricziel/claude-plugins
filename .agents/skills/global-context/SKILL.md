---
name: global-context
description: Add, change, or evaluate the global rules this marketplace injects into every Claude Code and Codex session — the `instructions/*.md` files in `common`, `oss`, and `toolkit`. Use when the user wants to add, change, reword, move, or remove a global instruction or rule ("add a rule that…", "the agent should always…", "stop telling it to…"), or to review or evaluate the global context per plugin and host.
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

## Add a rule

1. State the rule in one sentence and the failure it prevents. If you cannot
   name a failure, the rule probably does not need to exist.
2. Choose the plugin and file as described above.
3. Search all nine `instructions/*.md` files for a bullet that already covers
   it. If one exists, edit or move that bullet instead of adding a new one.
4. Write the bullet in `shared.md` when it holds for both hosts. When it needs
   host-specific wording, keep the host-neutral part in `shared.md` and put
   only the host-specific detail in `claude.md` and `codex.md`.
5. Run the evaluation below on the plugin you changed, then ship.

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

## Evaluate the global context

Use this mini eval when asked to review the global context, and after any
change. It proposes changes; it does not apply them until the user approves.

1. Render what each host receives, for each plugin:

   ```sh
   for p in common oss toolkit; do for h in claude codex; do
     arg=; [ "$h" = codex ] && arg=codex
     echo "== $p / $h"
     plugins/$p/scripts/session-start.sh $arg | jq -r .hookSpecificOutput.additionalContext
   done; done
   ```

   Then render the stacks a session can load, since cross-plugin duplication
   and conflicts only show up there: `common + oss`, and
   `common + oss + toolkit` (which `toolkit` pulls in through its
   dependencies):

   ```sh
   render() { h=$1; shift; echo "== $* / $h"
     for p in "$@"; do
       plugins/$p/scripts/session-start.sh $([ "$h" = codex ] && echo codex) |
         jq -r .hookSpecificOutput.additionalContext
     done; }
   for h in claude codex; do
     render $h common oss
     render $h common oss toolkit
   done
   ```

2. Score each plugin and host against these checks. Record pass or fail with
   the offending line for each:
   - **Placement**: the rule fits the plugin's audience, and `shared.md` names
     no host-specific models, agents, tools, or commands.
   - **Parity**: each rule in `claude.md` has a `codex.md` equivalent, or has
     a clear reason not to have one (and the reverse).
   - **Duplication**: no rule repeats one in another file or layer.
   - **Conflict**: no two rules contradict each other, within a host or
     across layers.
   - **References**: every skill, agent, file, command, and model a rule names
     exists. Check skills under `plugins/*/skills/` and
     `plugins/toolkit/codex-skills/`, and check that model names are current
     for the host.
   - **Actionability**: an agent can tell when the rule applies and what to
     do. Vague advice ("be careful") fails.
   - **Tone**: no shouting, no all-caps "MUST".
   - **Cost**: report the word count per plugin and host
     (`wc -w`). Flag any rule whose length is out of proportion to what it
     prevents.
   - **Hygiene**: no hostnames, IPs, or secret names.
3. Report a table with one row per plugin and host, showing the failed checks
   and the word count. Under it, list each proposed change as a concrete edit
   (file, old text, new text) with the check it fixes.
4. Stop and ask which changes to apply. Then follow "Add a rule" and "Ship it".

## Ship it

1. Run `python3 -m unittest discover -s tests && python3 scripts/validate.py`.
2. Preview what a host receives, for example
   `plugins/common/scripts/session-start.sh | jq -r .hookSpecificOutput.additionalContext`
   (pass `codex` as the first argument for the Codex output).
3. Commit with a semantic message scoped to the plugin, for example
   `feat(common): …` for a new rule or `fix(toolkit): …` for a correction. Do
   not edit `version`; release-please sets it.
4. If a README table describes the changed rule, update it in the same commit.
