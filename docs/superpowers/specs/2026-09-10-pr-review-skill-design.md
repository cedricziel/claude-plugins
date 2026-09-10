# PR review skill — design

Date: 2026-09-10

## Goal

Give the toolkit plugin its own thorough, multi-agent code review capability
that can be pointed at a GitHub PR, review it the way a careful human
reviewer (or CodeRabbit) would, and submit a real GitHub review — a
decision (approve / request changes / comment), a summary, and inline line
comments with committable suggestions where the fix is safe and mechanical.

Distilled from a survey of CodeRabbit's actual behaviour across this user's
repositories (signaldb, truenas-mcp, trueapp) — see "Format, informed by
the CodeRabbit survey" below — taking the parts worth copying and
explicitly avoiding the parts that turned out to be noise.

## Scope

- New workflow `toolkit:code-review` — the review engine. Works on any
  target `scripts/review-target.sh` already supports (working tree,
  branch, PR). Never touches GitHub.
- New workflow `toolkit:pr-review-submit` — the outward gate. Takes a
  review payload and a PR reference, submits one atomic GitHub review.
- New skill `code-review` — fronts the engine workflow only. Slash
  command `/deep-review` (the name `/code-review` is already used by the
  official `code-review` plugin; picking a distinct name avoids trigger
  ambiguity between the two).
- New skill `pull-request-review` — fronts engine + submit. Replaces the
  current `commands/pr-review.md` (a crude, freeform prompt with no
  structure, no verification, no real review submission) and its
  `/pr-review` slash command.
- `toolkit:adversarial-review` is unchanged and reused as-is, nested one
  level inside `code-review` as its defect-finding leaf.
- Out of scope for v1: Forgejo/Codeberg support (GitHub only, via `gh`);
  incremental "review only what changed since last review" mode (each
  explicit run reviews the full current diff and posts a fresh review);
  restricting which repos this can submit reviews to (any PR the user
  points it at, since submission always follows a real review run, not a
  standing subscription).

## Components

### `toolkit:code-review` (orchestrator workflow)

Nests `adversarial-review` as its one permitted leaf; everything else is
additional agent-call phases in this same file (no further nesting).

1. **Resolve** — `scripts/review-target.sh <target>` produces the diff.
   When the target is an explicit PR or branch (not opportunistic working-
   tree review), override adversarial-review's `minLines` floor to 0 — an
   explicit ask should not get skipped for being small.
2. **Review** — call `adversarial-review` with that diff: 5 lenses → 3
   refuters per finding → critic. Produces `confirmed`, `rejected`,
   `gaps`.
3. **Nitpicks** — one parallel, unrefuted lens pass over the same diff for
   style/maintainability opinions (naming, structure, minor
   inefficiencies) that don't rise to a provable defect. Kept in a
   separate bucket from `confirmed` throughout — never merged into one
   blunt count, and never alone enough to justify requesting changes.
4. **Suggest** — for each `confirmed` finding and each nitpick, one
   mechanical agent call proposes a committable suggestion only when the
   fix is a concrete, low-risk, line-local edit; otherwise the finding
   stays comment-only. Mirrors CodeRabbit only attaching suggestions when
   it's confident, rather than forcing one for every finding.
5. **Decide** — plain deterministic logic, no LLM call: any `confirmed`
   finding with severity `critical` or `high` → `REQUEST_CHANGES`;
   otherwise, if anything is left to say (`confirmed` medium/low,
   nitpicks, or gaps) → `COMMENT`; nothing at all → `APPROVE`. A decision
   this mechanical doesn't need judgment, and being deterministic makes it
   auditable.
6. **Summarize** — one short agent call writes the human-readable summary:
   a severity breakdown up front (counts by critical/high/medium/low and
   nitpick — the single blunt count CodeRabbit uses is explicitly a noise
   pattern to avoid), a one-paragraph walkthrough of what the diff does,
   and the critic's `gaps` listed as "risks not verified" so they're
   visible without being treated as confirmed defects.

Returns `{ refused, decision, summary, comments: [{file, line, severity,
category, title, body, suggestion?, nitpick}], gaps }`. Never calls `gh`
for anything mutating.

### `toolkit:pr-review-submit` (leaf workflow)

Takes the payload above plus `{ number, repo, cli }`. One agent call
resolves owner/repo if needed and submits a single
`gh api repos/{owner}/{repo}/pulls/{n}/reviews` POST bundling:

- `event`: the decision, mapped to `APPROVE` / `REQUEST_CHANGES` /
  `COMMENT`.
- `body`: the summary.
- `comments[]`: one entry per finding, `path`/`line`/`side: RIGHT`/`body`;
  a suggestion is embedded as a single ` ```suggestion ` fence appended to
  the body (no extra `diff` fence or nested `<details>` wrapping — one
  clean fence renders GitHub's native "commit suggestion" button, and the
  extra wrapping CodeRabbit uses added nothing but noise).

A clean diff (nothing in `comments`, decision `APPROVE`) posts a short
"no issues found" body with an empty `comments[]`.

This is a separate workflow, not a flag inside `code-review`, per this
repo's "gates live at the seams" rule — even though both new skills call
it immediately without pausing (see Posting policy below), keeping it
separate means a future confirm-before-post mode is a one-line change at
the skill layer, not a rewrite of the engine.

### Skills

- **`code-review`** (`/deep-review [target]`) — runs `code-review` only,
  renders the report (decision, severity breakdown, findings,
  suggestions, gaps). No GitHub side effects regardless of target.
- **`pull-request-review`** (`/pr-review <PR>`) — requires a PR number or
  URL. Runs `code-review`, then immediately `pr-review-submit`. Renders
  what was posted (comment count, decision, link to the review) afterward.

Both are explicit-trigger-only per this repo's convention: fire on their
slash command or an unambiguous literal ask ("review PR 123", "deep
review this branch"), never on bare "review this" / "code review" (that
stays the official `code-review` plugin) and never on CodeRabbit-comment
follow-ups (that's the existing `coderabbit` skill). Each SKILL.md states
its agent cost up front, matching `adversarial-review`'s doc shape.

## Format, informed by the CodeRabbit survey

What's worth keeping: a severity/category tag per finding (mapping our
existing lens names — correctness, security, concurrency, tests,
docs-drift, nitpick — to a short category label, plus adversarial-review's
existing critical/high/medium/low severity), and the
`REQUEST_CHANGES` → `APPROVE` lifecycle across re-reviews (which falls out
naturally here: a later explicit re-run that finds no confirmed findings
posts `APPROVE`, no special-casing required — this is exactly what
signaldb's `request_changes_workflow: true` config produces).

What's deliberately not copied, because the survey showed it as noise
rather than signal:

- 4-5 levels of nested `<details>` — our comments and summary use at most
  one collapsible level, if any.
- A single undifferentiated "Actionable comments posted: N" count with no
  severity breakdown — our summary leads with counts by severity instead.
- Internal bookkeeping HTML comments (fingerprint/indicator markers) —
  pure tooling noise with no reader value; omitted entirely.
- Repeating the same prompt-injection disclaimer boilerplate on every
  single comment — stated once in the summary if at all, not per-finding.
- No separate nitpick bucket in CodeRabbit's own UI (everything actionable
  is one number) — ours keeps nitpicks visibly separate throughout, as
  described in the Decide/Summarize steps above.

## Edge cases

- Empty/clean diff → `APPROVE`, short body, no inline comments.
- Draft PRs are still reviewed when explicitly asked; the summary notes
  draft status.
- Re-running `/pr-review` on the same PR posts a new review each time —
  matches how GitHub (and CodeRabbit) already stack multiple reviews on
  one PR; no incremental/diff-since-last-review mode for v1.
- A target with an empty PR diff (e.g. already-merged or closed PR) fails
  the same way `adversarial-review`'s existing target resolution already
  fails — surfaced, not swallowed.

## Cost

`code-review` inherits `adversarial-review`'s `1 + 5 + 3N + 1` agent calls,
plus one nitpick-lens call, plus up to `N + nitpicks` suggestion calls,
plus one summarize call. `pr-review-submit` adds one more. At the default
`maxFindings = 8` this is on the order of ~35-40 agent calls for
`pull-request-review`, roughly in line with `adversarial-review`'s
existing ~31.

## Posting policy

Submission is automatic on invocation — pointing `/pr-review` at a PR is
itself the go-ahead, the same trust model `/adversarial-review --comment`
already uses. No confirmation prompt between review and submission. This
was an explicit choice (not a default): the returned transcript always
shows exactly what got posted, and keeping `pr-review-submit` as its own
workflow (see above) means a future `--dry-run` or confirm-first mode
needs no engine changes.

## Validation

- `python3 -m unittest discover -s tests && python3 scripts/validate.py`
  must pass (existing repo-wide check: both new SKILL.md files need valid
  frontmatter, both new workflow files need to parse and their `meta`
  blocks need to satisfy the validator).
- Manual smoke test: run `/deep-review` against a small local branch with
  a deliberately introduced bug, confirm it's caught and categorized
  correctly, and that a clean second run reports no findings.
- Manual smoke test: run `/pr-review` against a real open PR (one of this
  user's own, low-stakes) and confirm the posted review's decision, body,
  and inline comments/suggestions render correctly on GitHub, then verify
  a re-run after pushing a fix flips the decision to `APPROVE`.
- Bump `version` in `plugins/toolkit/.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json` per this repo's convention.
