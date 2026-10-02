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

## Does it earn a test?

Score a test on four properties (Khorikov):

1. **Protection against regressions** — how likely it catches a real bug;
   grows with the complexity and business weight of the code it covers.
2. **Resistance to refactoring** — stays green when internals change but
   behavior doesn't.
3. **Fast feedback** — how quickly it runs.
4. **Maintainability** — how easy it is to read and keep working.

Value is the product, not the sum: a zero anywhere makes the test worthless.
Resistance to refactoring is all-or-nothing — a test that breaks on
refactors raises false alarms until nobody trusts the suite. Maintainability
isn't negotiable either. The one real trade-off is regression protection vs.
speed, which is the unit-vs-end-to-end choice.

Litmus: would a real change — a bug, not a refactor — make this test fail?
If no plausible bug flips it red, it tests nothing; delete it or don't write
it.

## Where tests pay off

Sort code by complexity/business weight and by number of collaborators:

| | Few collaborators | Many collaborators |
|---|---|---|
| **Complex / critical** | Domain logic, algorithms: unit test thoroughly | Overcomplicated: split into logic + glue first |
| **Simple** | Trivial code: don't test | Controllers, glue: a few integration tests |

Always test:

- Business logic, branching, edge cases.
- Previously-fixed bugs — the regression test is the fix's proof; never delete
  it once green.
- Public contracts/API boundaries other code depends on.
- Anything you rely on that isn't plain correctness — performance, security,
  failure handling — if it matters, it needs a test (Google's "Beyoncé rule").

Don't test:

- Trivial pass-throughs, generated code, framework/library internals, a getter
  with no logic.
- A test whose only failure mode is "the mock returned what I told it to" —
  see writing-tests on test doubles.

## What kind: scope and size

Two independent axes (Google). **Scope** is how much code a test covers:
**unit** (narrow), **integration** (a few components together), **end-to-end**
(the whole system). **Size** is what resources it may use: **small** = single
process, no network/disk/sleep; **medium** = single machine, may hit
localhost, a real DB, the filesystem; **large** = multi-machine, real
external services. Aim for small size at every scope you can — a broad test
that still runs in one process is cheap and predictive.

Push each test as far down as it can go (Fowler): if a higher-level test
catches a bug and no lower-level test failed, write the lower-level test.
Don't check the same behavior at several levels.

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

Put most tests where most of the complexity lives:

- **Logic-heavy code** → pyramid: Google's mix by scope is 80% unit, 15%
  integration, 5% end-to-end.
- **Thin services that mostly move data between systems** → honeycomb
  (Spotify): mostly integration tests at the service boundary, few tests of
  internals, and almost none that pass or fail based on another live system.
- **UI apps** → trophy (Kent C. Dodds): static checks, then mostly
  integration tests through the UI's real usage.

All three agree: end-to-end tests cover a handful of critical journeys,
nothing more. Two shapes are always wrong — the **ice-cream cone** (mostly
end-to-end; slow, flaky, hard to debug) and the **hourglass** (lots of unit
and end-to-end tests, few integration tests, so integration bugs surface
late). Percentages are a sanity check, not a target.

## Coverage

Coverage shows what's definitely untested, nothing about whether covered code
is tested well. Google's rough guide: 60% acceptable, 75% commendable, 90%
exemplary; going from 30% to 70% removes real risk, past that returns shrink
fast. Read it on the diff — new and changed lines. If you gate on coverage,
gate the diff, not a project-wide number, which teams treat as a ceiling. An untested critical path
is the actual risk, not a missing percent.

Mutation testing checks test quality where coverage can't: inject small bugs
and see which survive. At Google, surviving mutants matched real faults and
developers shown them wrote better tests. Use it on critical code or per diff.

## Flaky tests

A flaky test is worse than none: it trains people to ignore red. Google sees
tests lose value as flakiness approaches 1%. Fix or quarantine a flaky test
the day it's found — never just retry it into green.

## Cross-reference

Once something has earned a test, see the writing-tests skill for how to
structure it (AAA, test doubles, isolation, determinism, naming).
