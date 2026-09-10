---
name: pr-review
description: Review a GitHub PR with the same multi-agent engine as deep-review, then submit a real GitHub review — a decision (approve/request changes/comment), a summary, and inline line comments with committable suggestions. TRIGGER ONLY on /pr-review <PR>, or an explicit ask naming a specific PR to review and submit a verdict on. DO NOT trigger for bare "review this" / "code review" without a PR, for "adversarially review" (use /adversarial-review directly, which never posts a formal review), for a report-only request (use deep-review), or for CodeRabbit follow-ups (the coderabbit skill).
---

# PR review

Runs `toolkit:code-review` then `toolkit:pr-review-submit` — posts one real GitHub review per invocation. ~35-40 agent calls.

## When this fires

| Ask                                            | Action                                  |
| ---------------------------------------------- | --------------------------------------- |
| `/pr-review <PR#\|URL>`                        | run it                                  |
| "review PR 123 and leave your verdict"         | run it                                  |
| "review this", "code review" (no PR named)     | **not this skill**                      |
| "deep review PR 123" (report only, no posting) | **not this skill** — `deep-review`      |
| "address the CodeRabbit comments"              | **not this skill** — `coderabbit` skill |

Invoking this skill submits a real, visible GitHub review — including possibly "Request changes" — under the user's account, immediately, with no confirmation step. This is the user's explicit opt-in to that; do not ask again once triggered, but do surface exactly what was posted afterward.

## Usage

```
/pr-review 123
/pr-review https://github.com/owner/repo/pull/123
```

## Steps

1. Resolve the PR number and `owner/repo` (from the arg, or `gh pr view --json number,url` in the current checkout), then resolve its diff:

   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/review-target.sh" "<PR#>" "<scratchpad>/review.patch"
   ```

2. Run the review engine:

   ```
   Workflow({ name: "toolkit:code-review",
              args: { diffPath: "<abs path>", target: "PR #<n>" } })
   ```

3. Submit it:

   ```
   Workflow({ name: "toolkit:pr-review-submit",
              args: { number: <n>, repo: "<owner>/<repo>", cli: "gh",
                      decision: <decision from step 2>, summary: <summary from step 2>,
                      comments: <comments from step 2> } })
   ```

4. Report what was posted: decision, comment count, and the review URL. If `posted` is false, surface the failure — do not retry silently.

## Re-running

Re-running on the same PR posts a new review reflecting the current diff — this is how a PR that had `REQUEST_CHANGES` flips to `APPROVE` once fixes land, matching CodeRabbit's own `request_changes_workflow` behavior. There is no incremental "what changed since last review" mode.

## Cost

Same engine as `deep-review` (~35-40 agent calls) plus 1 for posting.
