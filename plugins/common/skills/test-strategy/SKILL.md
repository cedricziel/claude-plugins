---
name: test-strategy
description: >
  Deciding what deserves a test, what kind (unit/integration/e2e), and when to
  write it — as distinct from how to write a good test (see writing-tests).
  Use when planning test coverage for new code, reviewing a PR for missing or
  excessive tests, or choosing between a unit, integration, or end-to-end test.
  Triggers on: "does this need a test", "what should I test here", "unit or
  integration test", "test coverage", "add tests for this PR", sizing a test
  suite, or a PR that changes behavior without a corresponding test.
---

# Test Strategy

Companion to the writing-tests skill: that skill covers how to write a good
test once you've decided to write one. This is what earns a test, what kind,
and when.

## What to test

- Business logic, branching, edge cases.
- Previously-fixed bugs — the regression test is the fix's proof; never delete
  it once green.
- Public contracts/API boundaries other code depends on.
- Anything a reviewer would ask "did you check X?" about.

## What not to test

- Trivial pass-throughs, generated code, framework/library internals, a getter
  with no logic.
- A test whose only failure mode is "the mock returned what I told it to" —
  see writing-tests' "test behavior, not implementation."

## Litmus test

Would a real change — a bug, a bad refactor — make this test fail? If no
plausible change flips it red, it tests nothing; delete it or don't write it.

## What kind (size, not folder name)

Classify by scope/resources, not layer label (Google's test-size model):
**small** = single process, no network/disk/sleep; **medium** = single
machine, may hit localhost/a real DB/filesystem; **large** = multi-machine,
real external services. Default to the smallest size that can prove the
behavior. Business logic → small. Real integration points (DB queries, an
HTTP client's actual behavior) → medium. A handful of critical user journeys
→ large.

## When to test

- **New behavior**: write the test with or before the code (TDD where
  practical).
- **Bug fix**: reproduce with a failing test first; that test is the
  regression guard.
- **Refactor**: no new tests needed if existing ones already pin the
  behavior — needing new tests to pass means it's not just a refactor.
- **PR with no behavior change**: no test owed. A PR that changes behavior
  with no test change is the one to push back on.

## Suite shape

70-80% small, 15-20% medium, 5-10% large is the well-established range
(Google's internal ratio, the industry test pyramid) — a sanity check, not a
mandate. An inverted pyramid (few unit tests, mostly e2e/UI — the
"ice-cream cone") means slow, flaky feedback; flatten it. "Just say no to
more end-to-end tests" (Google Testing Blog): if a smaller test at the layer
that owns the logic can prove it, write that instead.

## Coverage

Coverage % is a lagging diagnostic, not a target — it shows what's definitely
untested, nothing about whether what's covered is tested well. A ratchet
(never regress) beats a fixed target nobody revisits. 100% is not the goal;
an untested critical path is the actual risk.

## Cross-reference

Once something has earned a test, see the writing-tests skill for how to
structure it (AAA, isolation, determinism, naming).
