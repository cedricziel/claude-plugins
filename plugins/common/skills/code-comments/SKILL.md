---
name: code-comments
description: >
  Rules for when a code comment earns its place. Use whenever writing new code,
  reviewing a diff, or deciding whether to keep, cut, or rewrite a comment —
  including docstrings and doc comments. Triggers on writing functions, reviewing
  PRs, "should I comment this", "add a docstring", or any comment already present
  in a diff under review.
---

# Code Comments

Default: no comment. Add one only if deleting it would cost a future reader
something the code itself can't say.

## Write a comment only for

- **Why, never what.** Code shows what; comment only hidden reasoning: a
  non-obvious constraint, a workaround for a specific bug/platform quirk, a
  rejected-simpler-alternative, an invariant the types don't express.
- **Public API surface** (exported fn, library entry point): doc comment states
  the contract for callers — params, return, error/panic conditions. Not for
  private/internal code; name it clearly instead.

## Never

- Restate the next line (`// increment i` above `i++`).
- Reference the current task/ticket/PR/"added for X flow" — commit message's job,
  and it rots the moment the code changes for a different reason.
- Leave commented-out code. Delete it; git has the history.
- Write a comment that can go stale silently. If it must track behavior, ask
  whether an assertion/test would catch drift instead — a comment can't.
- Decorative banners, emoji, restating the file/class/function name.

## Litmus test

Delete the comment. Would a competent reader, seeing only the code, misunderstand
or need to re-derive something non-obvious? No → leave it deleted. Yes → the
comment earns its place; keep it to one line if that's enough.

## Reviewing someone else's comments

Flag: what-comments (redundant with code), task-referencing comments, stale
comments contradicting the code next to them, commented-out code. Don't flag a
terse comment that documents a genuine why.
