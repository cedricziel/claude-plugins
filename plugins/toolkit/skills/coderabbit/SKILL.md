---
name: coderabbit
description: How to interact with CodeRabbit (the AI code reviewer, `@coderabbitai`) on pull requests — triggering and steering reviews, reading and replying to its comments, chatting with it, applying its committable suggestions, resolving review threads, and configuring it via `.coderabbit.yaml`. Use whenever a PR has CodeRabbit review comments to address, when you want to trigger or pause a CodeRabbit review, when a task mentions "coderabbit", "@coderabbitai", "rabbit", or an AI reviewer left comments on a GitHub PR.
---

# Interacting with CodeRabbit

CodeRabbit (`@coderabbitai` on GitHub, also GitLab) is an AI reviewer that posts a PR
**summary**, a **walkthrough**, inline **review comments** (often with committable
suggestions), and responds to slash-style commands you leave as PR/issue comments. You
steer it by leaving comments that start with `@coderabbitai`, and you address its findings
by editing code and resolving its review threads.

## Golden rules

- **Fix first, resolve second.** Never mark a thread resolved without a real code change
  (or an explicit, reasoned decision to skip). Resolving is a claim the concern is handled.
- **CodeRabbit findings are advice, not gospel.** It produces useful correctness/security
  catches *and* noisy nitpicks. Evaluate each on merit. Push back on wrong ones by replying
  in-thread; don't silently make a bad change to satisfy it.
- **Commands are PR/issue comments** whose body starts with `@coderabbitai`. They act on the
  PR the comment is on. One command per comment is most reliable.
- **Reply in the thread to chat.** Replying to a specific review comment gives CodeRabbit the
  file/line context; it will answer, refine, or generate a fix there.
- **Use `gh` for everything** — comments, GraphQL thread queries/mutations. Extract owner/repo
  with `gh repo view --json owner,name` and the PR with `gh pr view --json number,url`.

## Commands you can leave as `@coderabbitai` comments

Post with `gh pr comment <PR> --body "@coderabbitai <command>"`.

| Command | Effect |
|---|---|
| `@coderabbitai review` | Incremental review of new changes since the last review |
| `@coderabbitai full review` | Fresh review of the whole PR from scratch (ignores prior state) |
| `@coderabbitai summary` | Regenerate the PR summary / high-level walkthrough |
| `@coderabbitai resolve` | Resolve **all** CodeRabbit review comments on the PR |
| `@coderabbitai pause` / `resume` | Stop / restart automatic reviews on new pushes |
| `@coderabbitai ignore` | (in the **PR description**) opt this PR out of review entirely |
| `@coderabbitai configuration` | Print the effective config CodeRabbit is using |
| `@coderabbitai generate docstrings` | Generate docstrings for changed functions |
| `@coderabbitai plan` | Agentic planning for a requested change |
| `@coderabbitai help` | List available commands |
| `@coderabbitai <free-text question>` | Ask about the code, request a change, or discuss a finding |

Notes:
- `review` vs `full review`: reach for `full review` after a big rebase/force-push or when
  incremental review looks stale; otherwise `review`.
- To silence a single finding, reply to that thread rather than pausing the whole bot.

## Addressing review comments (the common task)

The repeatable loop — also packaged as the **`/coderabbit-resolve`** command:

1. **Identify the PR** — `gh pr view --json number,headRefName,url` (or take the passed number).
2. **Fetch unresolved CodeRabbit threads** via GraphQL (see snippet below): threads where
   `isResolved == false` **and** the first comment's `author.login == "coderabbitai"`.
3. **Per thread**: read the concern → open the file at `path`/`line` → decide (fix / reject
   with reason) → apply the change.
4. **Resolve** each genuinely-addressed thread with the `resolveReviewThread` mutation.
5. **Commit** with a semantic message (e.g. `fix(area): address CodeRabbit review comments`);
   run the repo's `make lint` / `make format` first; do **not** bypass pre-commit hooks.
6. **Verify** — re-fetch threads to confirm the previously-unresolved ones are now resolved.

If CodeRabbit attached a **committable suggestion** and it's correct, you can accept it in the
GitHub UI (Commit suggestion) or reproduce the diff locally — either way the thread should be
resolved afterward.

### Fetch unresolved CodeRabbit threads

```bash
gh api graphql -f query='
{
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: PR_NUMBER) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes { author { login } body path line startLine }
          }
        }
      }
    }
  }
}'
```

Filter to `isResolved == false` and `comments.nodes[0].author.login == "coderabbitai"`.

### Resolve a thread

```bash
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "THREAD_ID"}) {
    thread { id isResolved }
  }
}'
```

## Disagreeing with a finding

Reply in the thread (`gh api` to add a review-comment reply, or the UI) explaining why the
current code is correct, then resolve. For a nitpick/style point you disagree with, **ask the
user before skipping** rather than resolving unilaterally. Don't refactor beyond the flagged
issue just to appease the bot — preserve existing behaviour.

## Configuration — `.coderabbit.yaml`

Repo-root `.coderabbit.yaml` controls review behaviour. Common keys:

```yaml
reviews:
  profile: chill            # "chill" (fewer nits) or "assertive"
  request_changes_workflow: false
  auto_review:
    enabled: true
    drafts: false           # skip draft PRs
  path_filters:             # globs to include/exclude from review
    - "!**/*.generated.ts"
  path_instructions:
    - path: "**/*.rs"
      instructions: "Enforce our error-handling conventions."
language: en-US
```

- `profile: chill` is the go-to lever when reviews are too noisy.
- `path_filters` excludes vendored/generated code; `path_instructions` gives per-path guidance.
- After editing, `@coderabbitai configuration` confirms what's actually in effect.
- Validate against CodeRabbit's current schema (docs.coderabbit.ai) before relying on a key —
  options evolve.

## Does CodeRabbit's approval depend on resolving threads?

**Only if `request_changes_workflow` is enabled.** This governs whether thread resolution
gates approval:

- **`request_changes_workflow: false` (default):** CodeRabbit posts its review as plain
  **comments**. It never submits an "Approve" and does **not** block merging — so resolving
  its threads has no bearing on merge status. Resolve them for cleanliness/accuracy, not to
  unblock a merge.
- **`request_changes_workflow: true`:** CodeRabbit submits **"Request changes,"** then flips
  to **Approved** automatically once **all** its review comments are resolved **and** no
  pre-merge checks are in an error state. On **GitLab**, *all* discussions (not just
  CodeRabbit's) must be resolved. `@coderabbitai approve` force-approves without waiting, but
  works **only** when this workflow is enabled.

Teams turn it on for "CodeRabbit + one human" gating. When you see CodeRabbit blocking a PR
with "Request changes," that's this mode — driving every CodeRabbit thread to resolved (and
fixing failing pre-merge checks) is what clears it.
