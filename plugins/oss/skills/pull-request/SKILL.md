---
name: pull-request
description: >
  Defines the required shape for a pull request's title and body. ALWAYS use this
  skill when opening a pull request, drafting a PR description, or writing a PR
  title — not optional. Triggers on: "open a PR", "draft the PR description",
  "write the PR title", "create a pull request", or any point where a branch is
  ready to go up for review.
---

# Pull Request

## Title

Same semantic format as commits — see the `commit-discipline` skill for the type
table:

```
type(scope): imperative summary
```

No angle brackets, no vague summaries. A PR spanning one commit can reuse that
commit's message. A PR spanning several picks the type/scope of the change as a
whole.

## Body

Small and concise — stay inside the template below, section by section. This is
reviewer-facing, in proper grammar, not caveman-compressed notes. A long PR body is
a sign the PR itself is too big, not a sign the description needs more detail.

```
## Problem
What was broken or missing, and why it matters. 1-3 sentences.

## Approach
What the change does, and why this shape over the alternatives. 1-3 sentences.

## Tests
Concrete commands run and their observed outcome — not "tests pass".

## Security Impact
`None`, or what changed and why it's safe. One line when possible.

## Risk
Blast radius if this is wrong. `Low` when scoped to the files named above.

## Screenshots
Before/after images of the changed UI. Only when the change is visible.
```

Add `Closes #<issue>` when the PR closes a tracked issue.

**Rules:**

- Every section stays short — a sentence or two, not a paragraph. If a section needs
  more, the change likely needs splitting instead (see `commit-discipline`'s PR
  Strategy).
- Don't restate the diff or narrate file-by-file changes — the diff already shows that.
- Skip a section only when it is genuinely inapplicable (e.g. no security-relevant
  surface touched) — never leave it out just to save space.

## Screenshots

Include them whenever the change alters something a person sees: a UI, rendered
docs, a chart, terminal output layout. Leave the section out for changes with no
visible surface; a screenshot of a diff or a test run adds nothing.

1. **Capture** against a running instance — the project's `verify` or `run` skill
   if it has one, otherwise Playwright (`page.screenshot({ path, fullPage: true })`).
   Take a before shot from the base branch when the difference is the point. Save
   to the scratchpad, never the repo, and crop to the part that changed.
2. **Upload** with `scripts/upload-screenshots.sh` from this skill's directory. Run
   it with the target checkout as the working directory; file names may use only
   letters, digits, `.`, `_` and `-`:

   ```bash
   <this-skill-dir>/scripts/upload-screenshots.sh <pr-branch> before.png after.png
   ```

   It commits the images to an orphan `pr-assets` branch on `origin` (its push URL) (working tree
   and index untouched, PR diff unchanged) and prints one Markdown image line per
   file, pinned to that commit's SHA. GitHub has no API for the drag-and-drop
   attachment upload, so this branch is the agent's way in. The links render in
   private repos for anyone with read access.
3. **Embed** the printed lines under `## Screenshots`, each with a one-line caption
   saying what to look at. For an existing PR, `gh pr edit <n> --body-file <file>`.

Never upload screenshots that show secrets, tokens, real customer data, or
internal hostnames — check the image before pushing it; a pushed blob stays in
history.
