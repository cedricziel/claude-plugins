---
name: pr-review
description: Review a GitHub PR with the same multi-agent engine as deep-review, then submit a real GitHub review — a decision (approve/request changes/comment), a summary, and inline line comments with committable suggestions. TRIGGER ONLY on /pr-review <PR>, or an explicit ask naming a specific PR to review and submit a verdict on. DO NOT trigger for bare "review this" / "code review" without a PR, for "adversarially review" (use /adversarial-review directly, which never posts a formal review), for a report-only request (use deep-review), or for CodeRabbit follow-ups (the coderabbit skill).
---

# PR review

Runs `toolkit:code-review` then `toolkit:pr-review-submit` — posts one real GitHub review per invocation. ~35-40 agent calls.

## When this fires

| Ask                                            | Action                                  |
| ---------------------------------------------- | --------------------------------------- |
| `/pr-review <PR#>`                             | run it                                  |
| "review PR 123 and leave your verdict"         | run it                                  |
| "review this", "code review" (no PR named)     | **not this skill**                      |
| "deep review PR 123" (report only, no posting) | **not this skill** — `deep-review`      |
| "address the CodeRabbit comments"              | **not this skill** — `coderabbit` skill |

Invoking this skill submits a real, visible GitHub review — including possibly "Request changes" — under the user's account, immediately, with no confirmation step. This is the user's explicit opt-in to that; do not ask again once triggered, but do surface exactly what was posted afterward.

## Usage

```
/pr-review 123      # a PR in the current checkout's repository
/pr-review          # the current branch's own PR
```

A bare PR number only. `review-target.sh` resolves `gh pr diff <n>` against whatever
repository the current checkout belongs to, while step 4 posts to the repo named in
the args — so a PR reference pointing somewhere else reviews one PR and posts the
verdict onto a different, unrelated one. To review a PR in another repository, run
this from a checkout of that repository. (`adversarial-review` takes PR numbers only
for the same reason.)

## Steps

1. **Resolve the PR, then check it out into an isolated worktree.**

   `gh pr view --json number,url` gives the number when no argument was passed;
   `gh repo view --json nameWithOwner` gives `owner/repo`.

   `gh pr diff` fetches diff _text_ and nothing else — the working tree never moves,
   while every agent underneath reads files from whatever is checked out. Skip this and
   a review launched from `main` reviews `main`, and the committable suggestions it
   posts — one click to apply, with no confirmation gate — can propose reverting the
   author's real changes. So make the ambient checkout _be_ the PR's head, in a scratch
   worktree, never by moving the user's own checkout:

   ```bash
   git worktree add --detach "<scratchpad>/review-wt"
   cd "<scratchpad>/review-wt" && gh pr checkout <n> --detach
   ```

   If this session has a native worktree tool (`EnterWorktree`, `/worktree`), use it
   instead — see the `using-git-worktrees` skill. Run every step below from that
   directory, and remove it once the review is posted:
   `git worktree remove --force "<scratchpad>/review-wt"`.

2. Resolve the diff, from the worktree:

   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/review-target.sh" "<PR#>" "<scratchpad>/review.patch"
   ```

3. Run the review engine:

   ```
   Workflow({ name: "toolkit:code-review",
              args: { diffPath: "<abs path>", target: "PR #<n>" } })
   ```

4. Submit it:

   ```
   Workflow({ name: "toolkit:pr-review-submit",
              args: { number: <n>, repo: "<owner>/<repo>", cli: "gh",
                      decision: <decision from step 3>, summary: <summary from step 3>,
                      comments: <comments from step 3> } })
   ```

5. Report what was posted: decision, comment count, and the review URL. If `posted` is false, surface the failure — do not retry silently.

## Re-running

Re-running on the same PR posts a new review reflecting the current diff — this is how a PR that had `REQUEST_CHANGES` flips to `APPROVE` once fixes land, matching CodeRabbit's own `request_changes_workflow` behavior. There is no incremental "what changed since last review" mode.

## Cost

Same engine as `deep-review` (~35-40 agent calls) plus 1 for posting.
