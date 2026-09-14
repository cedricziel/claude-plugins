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
```

Add `Closes #<issue>` when the PR closes a tracked issue.

**Rules:**

- Every section stays short — a sentence or two, not a paragraph. If a section needs
  more, the change likely needs splitting instead (see `commit-discipline`'s PR
  Strategy).
- Don't restate the diff or narrate file-by-file changes — the diff already shows that.
- Skip a section only when it is genuinely inapplicable (e.g. no security-relevant
  surface touched) — never leave it out just to save space.
