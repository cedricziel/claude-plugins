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

## Usage

```
/deep-review                 # working tree (staged + unstaged + untracked)
/deep-review 123             # GitHub PR #123 diff (read-only — nothing is posted)
/deep-review feature/x       # branch vs its merge-base with main
/deep-review 123 --max 12    # verify up to 12 findings (default 8)
```

## Steps

1. **PR and branch targets: check the code out into an isolated worktree first, and run everything below from there.**

   `review-target.sh` only produces diff _text_ — `gh pr diff` never moves the working
   tree. Every agent underneath reads files from whatever is checked out: the nitpick
   lens, the suggestion writers, and `adversarial-review`'s own reviewers and refuters
   all "open surrounding files in the repository". Run `/deep-review 123` from a `main`
   checkout without this step and they review `main` instead of the PR. So make the
   ambient checkout _be_ the code under review — in a scratch worktree, never by moving
   the user's own checkout:

   ```bash
   git worktree add --detach "<scratchpad>/review-wt"          # PR target
   cd "<scratchpad>/review-wt" && gh pr checkout 123 --detach

   git worktree add --detach "<scratchpad>/review-wt" feature/x   # branch target
   cd "<scratchpad>/review-wt"
   ```

   If this session has a native worktree tool (`EnterWorktree`, `/worktree`), use it
   instead — see the `using-git-worktrees` skill. Remove the worktree once the report is
   rendered (`git worktree remove --force "<scratchpad>/review-wt"`): the report holds
   everything, so nothing is lost by cleaning up.

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

4. Render the result:
   - **Decision** — APPROVE / COMMENT / REQUEST_CHANGES, shown first.
   - **Findings by severity** — the counts line from the result's `summary`.
   - **Confirmed findings** — table: `file:line`, severity, title, and the suggestion diff if one exists.
   - **Nitpicks** — listed separately, never counted toward the decision.
   - **Risks not verified** — the critic's gaps, marked unconfirmed.
     Every `file:line` must be a clickable reference.

## Cost

Inherits `adversarial-review`'s `1 + 5 + 3N + 1`, plus 1 nitpick call, plus up to `N + nitpicks` suggestion calls, plus 1 summary call. At the default `N=8` that's roughly 35-40 agent calls.
