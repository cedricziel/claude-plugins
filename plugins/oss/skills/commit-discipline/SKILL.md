---
name: commit-discipline
description: >
  Enforces atomic commit discipline and fast PR cycles to keep the main branch always
  shippable. Use proactively when planning a feature, breaking work into tasks, making
  any code changes, staging files, writing commit messages, or discussing what to ship.
  Triggers on: "let's add X", "I'm working on Y", "commit this", "open a PR", breaking
  down a feature, or any discussion of code changes or git operations.
---

# Commit Discipline

## Core Rule

Main is always shippable. Every commit compiles, passes tests, and represents a single
coherent intent. Never commit broken or half-finished work to a shared branch.

## Atomic Commits

One logical reason to change → one commit. Before staging, ask: _"Can I describe this
in one sentence without 'and'?"_ If not, split it.

**Split if you see:**

- The message needs "and", "also", or "plus"
- Files from unrelated concerns are staged together
- A reviewer would need to context-switch within the diff

**Workflow:**

1. Stage only files that belong to one logical change
2. Commit it
3. Repeat for the next change

Resist the urge to batch unrelated fixes into one commit just because they happened
to be worked on at the same time.

## Semantic Commit Format

```
type(scope): short imperative description

Optional body explaining WHY, not what. Wrap at 72 chars.
```

| Type       | Use for                                    |
| ---------- | ------------------------------------------ |
| `feat`     | New capability visible to users or callers |
| `fix`      | Correcting a defect                        |
| `refactor` | Restructure without behavior change        |
| `test`     | Adding or fixing tests                     |
| `chore`    | Tooling, deps, config, CI                  |
| `docs`     | Documentation only                         |
| `perf`     | Measurable performance improvement         |
| `style`    | Formatting, no logic change                |

**Rules:**

- `scope` = affected crate, module, or area in parens: `feat(runtime): …`
- Description: imperative mood ("add", not "adds"/"added"), no trailing period, ≤72 chars
- No `WIP`, `misc`, `updates`, `stuff`, or vague messages
- Breaking changes: append `!` after type/scope and explain in body

## PR Strategy

A PR represents **one complete, meaningful unit of work** — something a reviewer can
fully understand in a single sitting and that ships value independently.

**Meaningful** means:

- It delivers a complete concept (full feature, complete fix, coherent refactor)
- A reviewer understands the intent without other open PRs as context
- Merging it alone doesn't break anything

**When breaking down large features:**

1. Identify independently-mergeable slices (e.g. data layer → API → UI)
2. Each slice = its own PR, merged in sequence
3. Stack PRs off each other when slices depend on unmerged changes
4. Never gate a small self-contained slice behind a large unrelated one

**Anti-patterns to avoid:**

- Week-long branches that accumulate unrelated changes
- "Drive-by" changes mixed into unrelated PRs
- Blocking a reviewable unit because the full feature isn't done yet

## Staying Shippable

- Feature flags over long-lived feature branches
- If it can't ship today, it shouldn't be on main
- Every merge to main = potentially in production
- Prefer more, smaller PRs over fewer, larger ones — velocity comes from fast merge cycles
