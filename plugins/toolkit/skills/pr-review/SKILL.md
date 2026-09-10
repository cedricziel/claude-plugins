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
repository the current checkout belongs to, while step 5 posts to the repo named in
the args — so a PR reference pointing somewhere else reviews one PR and posts the
verdict onto a different, unrelated one. To review a PR in another repository, run
this from a checkout of that repository. (`adversarial-review` takes PR numbers only
for the same reason.)

## Steps

1. **Resolve the PR, then switch the session into an isolated worktree — a bare `cd` does not do this.**

   `gh pr view --json number,url` gives the number when no argument was passed;
   `gh repo view --json nameWithOwner` gives `owner/repo`; and
   `gh pr view <n> --json headRefOid -q .headRefOid` gives the head commit SHA.

   Capture that SHA now, before the review runs, and pass it to step 5 as
   `commitSha`. The review takes minutes; the author can force-push in that time.
   The SHA pins the posted verdict to the code that was actually read, and step 5
   refuses to post at all if the PR's head has moved since.

   `gh pr diff` fetches diff _text_ and nothing else — the working tree never moves,
   while every agent underneath reads files from whatever is checked out. `Workflow()`
   spawns those agents as separate processes: they inherit the session's actual working
   directory, not a `cd` run inside one Bash call, which only changes that shell and is
   invisible to anything spawned afterward. Skip a real switch and a review launched
   from `main` reviews `main`, and the committable suggestions it posts — one click to
   apply, with no confirmation gate — can propose reverting the author's real changes.

   The native worktree-switching tool (`EnterWorktree`, or `/worktree` — see the
   `using-git-worktrees` skill) is the primary, required mechanism, because only a
   session-level switch actually relocates what spawned agents see. Create the worktree
   and check the PR out into it:

   ```bash
   git worktree add --detach "<scratchpad>/review-wt"
   cd "<scratchpad>/review-wt" && gh pr checkout <n> --detach
   ```

   then switch the session into it:

   ```
   EnterWorktree({ path: "<scratchpad>/review-wt" })
   ```

   (`EnterWorktree` requires the path to already appear in `git worktree list`, which
   is why `git worktree add` runs first — it switches the session, it doesn't create
   the worktree.) Run every step below from that worktree. If this session has no
   native worktree-switching tool, there is no way to guarantee the spawned agents see
   the PR's code rather than `main` — say so plainly to the user before proceeding,
   rather than running the `git worktree add` / `cd` recipe alone and assuming it
   worked.

   Remove the worktree once the review is posted — `ExitWorktree({ action: "keep" })`
   to return to the original directory (it will not delete a worktree entered via
   `path`), then `git worktree remove --force "<scratchpad>/review-wt"`.

2. Resolve the diff, from the worktree:

   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/review-target.sh" "<PR#>" "<scratchpad>/review.patch"
   ```

3. Run the review engine:

   ```
   Workflow({ name: "toolkit:code-review",
              args: { diffPath: "<abs path>", target: "PR #<n>" } })
   ```

4. If step 3's `refused` is non-null, report that reason to the user and stop. Do not
   call `pr-review-submit`: a refused run carries `decision: null`, which it rejects,
   and there is no verdict to post. Every workflow in this plugin returns
   `refused: null` on success or a reason string on any early exit.

5. Submit it:

   ```
   Workflow({ name: "toolkit:pr-review-submit",
              args: { number: <n>, repo: "<owner>/<repo>", cli: "gh",
                      commitSha: "<head SHA from step 1>",
                      decision: <decision from step 3>, summary: <summary from step 3>,
                      comments: <comments from step 3> } })
   ```

   A non-null `refused` here means nothing was posted — most often because the PR's
   head moved while the review ran. Report the reason and stop; re-running the whole
   review against the new head is the fix, not re-posting this one.

6. Report what was posted: decision, comment count, and the review URL. If
   `droppedComments` is non-empty, GitHub rejected the inline comments and only the
   verdict and summary were posted — show that text so the user knows which findings
   never reached the PR. If `posted` is false, surface the failure — do not retry
   silently.

## Re-running

Re-running on the same PR posts a new review reflecting the current diff — this is how a PR that had `REQUEST_CHANGES` flips to `APPROVE` once fixes land, matching CodeRabbit's own `request_changes_workflow` behavior. There is no incremental "what changed since last review" mode.

## Cost

Same engine as `deep-review` (~35-40 agent calls) plus 1 for posting.
