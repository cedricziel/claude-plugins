---
name: deep-review
description: Thorough multi-agent code review — 5 lenses, refuters, critic, plus style nitpicks and committable suggestions — for a diff, branch, or PR. Produces a categorized report only; never touches GitHub. TRIGGER ONLY on /deep-review, or an explicit ask naming "deep review" / "thorough categorized review" for a specific target. DO NOT trigger for bare "review this" / "code review" (the official code-review plugin handles that), for "adversarially review" (that's /adversarial-review directly), or for CodeRabbit follow-ups (the coderabbit skill).
---

# Deep review

Runs the `code-review` workflow (which nests `adversarial-review`) shipped with this plugin. ~35-40 agent calls per run.

## When this fires

| Ask                                            | Action                                                 |
| ---------------------------------------------- | ------------------------------------------------------ |
| `/deep-review [target]`                        | run it                                                 |
| "deep review PR 12 / this branch / my changes" | run it                                                 |
| "review this", "code review"                   | **not this skill** — the official `code-review` plugin |
| "adversarially review ..."                     | **not this skill** — `/adversarial-review` directly    |
| "address the CodeRabbit comments"              | **not this skill** — `coderabbit` skill                |

Invoking this skill is the user's explicit opt-in to multi-agent orchestration — do not ask again once triggered.

## Only run this against code from a trusted source

A PR or branch target gets checked out (step 1). From that moment the target's own
`CLAUDE.md` and `.claude/**` are this session's project configuration — a PR from a
fork or an external contributor can therefore ship instructions, hooks and settings
that try to steer everything the session does next. Reading a diff is safe; checking
it out is not, and nothing here sandboxes that.

So run `/deep-review` only on targets the user already trusts: same-repo branches,
known contributors. For anything else, say plainly that reviewing it would load that
code's configuration into the session, and let the user decide before checking it
out.

## Usage

```
/deep-review                 # working tree (staged + unstaged + untracked)
/deep-review 123             # GitHub PR #123 diff (read-only — nothing is posted)
/deep-review feature/x       # branch vs its merge-base with main
/deep-review 123 --max 12    # verify up to 12 findings (default 8)
```

## Steps

**Leave the worktree on every path out.** Once step 1 has entered one, call
`ExitWorktree()` before you finish — on every ending, not just the one where a report
gets rendered: an empty diff, a `refused` result from step 3, an error anywhere. The
report holds everything worth keeping, so nothing is lost by leaving.

1. **PR and branch targets: switch the session into an isolated worktree before running anything below — a bare `cd` does not do this.**

   `review-target.sh` only produces diff _text_ — `gh pr diff` never moves the working
   tree. Every agent underneath reads files from whatever is checked out: the nitpick
   lens, the suggestion writers, and `adversarial-review`'s own reviewers and refuters
   all "open surrounding files in the repository". `Workflow()` spawns those agents as
   separate processes — they inherit the session's actual working directory, not a `cd`
   run inside one Bash call, which only changes that one shell and is invisible to
   anything spawned afterward. Run `/deep-review 123` from a `main` checkout using `cd`
   for this and the spawned agents still review `main`, not the PR.

   The native worktree-switching tool (`EnterWorktree`, or `/worktree` — see the
   `using-git-worktrees` skill) is the primary, required mechanism: only a
   session-level switch actually relocates what spawned agents see. Let it create the
   worktree by passing a `name` — that puts it under `.claude/worktrees/` and switches
   the session into it in one step:

   ```
   EnterWorktree({ name: "review-123-<timestamp>" })          # PR target
   EnterWorktree({ name: "review-feature-x-<timestamp>" })    # branch target
   ```

   Generate `<timestamp>` yourself with `date +%s` and put it in the name. A fixed
   name collides on a second review of the same PR or branch, because the worktree
   and its backing branch may still exist from a run that ended early (a `refused`
   result, a crash). A per-run name means each run gets its own worktree, so
   interrupted runs leave ones behind; `git worktree list` shows them and
   `git worktree remove --force <path>` clears an actual leftover worktree still on
   disk whenever the user wants to tidy up (`git worktree prune` only clears stale
   administrative records for a worktree directory that was already deleted by hand
   — it does not remove one that still exists).

   Then check the target out from inside it:

   ```bash
   gh pr checkout 123 --detach   # PR target
   git checkout feature/x        # branch target
   ```

   Do not hand-run `git worktree add` into a scratchpad path and enter it by `path`
   instead: a location outside `.claude/worktrees/` prompts to relocate the session's
   permission root, and entering a worktree the tool did not create is its own
   documented fragile case — it will not clean that one up for you either.

   If this session has no native worktree-switching tool, there is no way to guarantee
   the spawned agents see the right code — say so plainly to the user rather than
   running a `git worktree add` / `cd` recipe alone and assuming it worked.

   A working-tree target skips this — the code under review is already checked out.

2. Resolve the diff (from the worktree, if you made one):

   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/review-target.sh" "<target>" "<scratchpad>/review.patch"
   ```

   It prints `kind=… base=… lines=…`. If it exits non-zero the diff is empty — tell the user and stop.

3. Run the workflow, passing the absolute diff path:

   ```
   Workflow({ name: "toolkit:code-review",
              args: { diffPath: "<abs path>", target: "<PR #123 | branch x | working tree>",
                      maxFindings: <n> } })
   ```

4. If the result's `refused` is non-null, report that reason to the user and stop — the
   nested `adversarial-review` bailed out (its own budget floor, an empty diff) and
   there is nothing to render. Every workflow in this plugin returns `refused: null`
   on success or a reason string on any early exit.

5. `ExitWorktree()` if step 1 entered one, then render the result:
   - **Decision** — APPROVE / COMMENT / REQUEST_CHANGES, shown first.
   - **Findings by severity** — the counts line from the result's `summary`.
   - **Confirmed findings** — table: `file:line`, severity, title, and the suggestion diff if one exists.
   - **Nitpicks** — listed separately, never counted toward the decision.
   - **Risks not verified** — the critic's gaps, marked unconfirmed.
     Every `file:line` must be a clickable reference.

## Cost

Inherits `adversarial-review`'s `1 + 5 + 3N + 1`, plus 1 nitpick call, plus up to `N + nitpicks` suggestion calls, plus 1 summary call. At the default `N=8` that's roughly 35-40 agent calls.
