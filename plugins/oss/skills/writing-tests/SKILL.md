---
name: writing-tests
description: Principles for writing good tests, distilled from the TDD canon (Beck, Fowler, Meszaros, Freeman & Pryce, Cooper). Use whenever writing new tests, reviewing test code, doing TDD red-green-refactor, or deciding what and how to test — unit, integration, or end-to-end, in any language.
---

# Writing Tests

The goal, in one line: **a good test fails when — and only when — the behavior it documents is broken, tells you exactly what broke, runs fast enough that you actually run it, and reads like a specification.** Everything below is a tactic in service of that.

## TDD discipline

1. **Write the failing test first, and watch it fail.** A test you never saw red might assert nothing. Red proves the test _can_ fail for the right reason; green proves the code fixes exactly that.
2. **Timely**: write the test just before the code it drives, not as an afterthought batch.
3. **Listen to test pain.** If a test is hard to write — huge setup, deep mock chains, reaching into internals — that's a design smell in the production code, not a testing problem. Fix the design, don't power through.

## Behavior, not implementation

Deciding *whether* something deserves a test is the test-strategy skill's job. Once it does:

- **Test behavior, not implementation.** The unit of isolation is the behavior, not the class or function. Test through the public API of the module. A test-per-class with mocks for every collaborator locks in the current design and makes refactoring painful.
- **Structure-insensitive**: refactoring internals without changing behavior must not break any test. If it does, the test is coupled to implementation — rewrite it.
- **Behavioral sensitivity**: if behavior breaks, some test must fail. Cover the contract: happy path, error paths, boundary values.

## Test doubles

- **Prefer, in order: real implementation → fake → stub → interaction check** (Google). A fake is a working lightweight version (in-memory repo); a stub returns canned answers; an interaction check asserts which calls were made.
- **Assert on state, not calls.** Check the returned value or the resulting state. Asserting that a method was called proves only that it was called, not that the system works.
- **Use the real thing for dependencies only your app touches** — your own database, your filesystem — and check final state. **Mock only external dependencies other systems can observe**: third-party APIs, message buses, email (Khorikov). Even then, wrap the client in an adapter you own and mock the adapter.
- **Watch for change-detector tests**: a test that fails on any edit to the production code, even when behavior stays the same. It's almost always overused stubs and call assertions — replace them with state checks against reals or fakes.

## How to structure each test

- **Arrange–Act–Assert** (Given–When–Then): one setup, one action, one logical assertion block. Multiple act/assert cycles = several tests wearing a trenchcoat; split them.
- **One reason to fail.** Verify one condition per test — not literally one assert, but one logical concept, so a red test points at exactly one defect.
- **Name tests as specifications.** `parse_duration_returns_error_for_negative_values`, not `test_parse`. The failing test's name alone should say what's broken.
- **No logic in tests.** No conditionals, loops, or clever computation inside a test — test logic can itself be wrong, and there's no test for the test. Prefer dumb, obvious, slightly repetitive tests over DRY-ed abstract ones. Test code should be obvious; production code can be clever.
- **Self-validating**: pass/fail without human inspection of output. Never "run it and eyeball the logs."

## Suite properties

- **Isolated & order-independent**: tests must not affect each other — no shared mutable fixtures, run in any order, any subset, in parallel.
- **Deterministic**: same code, same result, every time. No reliance on wall-clock time, sleeps, network, randomness without a seed, or leftover state. Flaky tests destroy trust in the whole suite — fix or delete them immediately.
- **Fast**: slow suites don't get run, and the TDD feedback loop dies. Keep unit tests in milliseconds; push slow, real-dependency tests into a separately runnable integration tier.
- **Specific failures**: when a test fails, the name + assertion message should localize the problem without a debugger. Use assertion messages and matchers that show expected vs actual.

## Trade-offs

These properties tension against each other (Beck's test desiderata): e.g. predictive end-to-end tests are slower and less specific; fast isolated unit tests are less predictive of production. Choose deliberately per layer — don't pretend one kind of test does everything.

## Checklist before committing a test

- [ ] Saw it fail for the right reason before making it pass
- [ ] Name states the scenario and expected outcome
- [ ] Tests behavior through the public API; survives refactoring of internals
- [ ] Uses reals or fakes where it can; asserts on state, not on calls made
- [ ] One logical assertion; no conditionals or loops in the test body
- [ ] Deterministic: no time, network, ordering, or shared-state dependence
- [ ] Fails with a message that localizes the defect
