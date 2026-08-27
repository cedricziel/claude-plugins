# Fleet brief — paste into every code-committing subagent prompt

Subagents already inherit the global instructions, the project CLAUDE.md and the
memory index, so do not restate those. This file exists because a checklist in a
task prompt _overrides_ inherited rules: anything a step-by-step list omits reads
as permission to skip. Keep each list below complete, or drop the list entirely.

## Setup

- Branch off `origin/main`; work only inside your own worktree.
- Submodules: some repos need `git submodule update --init <name>` before they build.
- A fresh worktree has no `node_modules`, so any codegen step with a JS half
  (e.g. an OpenAPI TypeScript client) fails with a confusing "command not found"
  until you run the project's install (`pnpm install --frozen-lockfile`). Costs
  no meaningful disk.
- Never share a `CARGO_TARGET_DIR` between concurrent worktree agents — cargo
  silently serves cross-branch artifacts (stale binaries, "my new field vanished").
  Export a per-worktree target dir plus `CARGO_INCREMENTAL=0`, and a warm shared
  compiler cache (sccache) to keep rebuilds tolerable.

## Orchestrator: cleaning up after a merge

Never delete an agent's worktree until that agent has actually stopped, and
re-check after resuming it — a completion report is not the same as a dead
agent, and resuming one puts it straight back into the directory you were about
to remove. Deleting it mid-run leaves the agent with no cwd, so every shell call
fails and it cannot read, diff, or recover on its own. Recovery is
`git worktree add <path> -b <branch> origin/main`, then tell the agent the path,
that it must rebase (the new worktree starts at whatever origin/main was) and
that it must init submodules itself.

But prefer never needing that: a running agent cannot relocate itself. Moving an
agent's worktree mid-session wedges it structurally — the move changes its cwd
while its shell guard stays pinned to the old path, the two then disagree, and
every shell command is refused; the exit mechanism refuses too and points back at
the shell that just failed. Reads still work, which makes it look survivable when
it is not. So pin an agent to the worktree it will finish in AT LAUNCH, and if it
must move, spawn a successor with a written handover instead. Time the handover
between PRs, when nothing is uncommitted — a wedge only costs reading time if
there is nothing to strand, and that should be by design rather than by luck.

## Disk (fleet work is disk-bound before it is CPU-bound)

- `df -h /` before any build. Below ~8 GB free: stop building, rely on CI.
- Targeted builds only (`-p <crate> <filter>`), never a full workspace run.
- Drop your target dir the moment you are waiting on CI, not after the first result.
- On ENOSPC or a linker `errno=28`: stop, drop the target dir, report. Do not retry.

## Verify the premise first

Check the issue's claim against current HEAD before writing code — and check the
_infrastructure_ claims too, not only the code ones. A pinned fork, a carried
patch, a workaround comment: these break nothing when they go stale, so nothing
ever surfaces them. (Real case: a fork's entire carried delta had merged upstream
months earlier and we were pinned to it for no reason.) Where a pin names the
upstream PRs it carries, assert those are still open and that the pinned rev
descends from upstream's default branch.

Check the issue's claim against current HEAD before writing code. Much of a
backlog is already fixed. If it is, comment with evidence, close it, and report —
no empty PR.

## Before every commit

1. Lint/format per the project (`cargo fmt`, targeted clippy) — pre-commit hooks
   may do a full build, so `--no-verify` after running them manually is fine.
   Two traps that cost a CI round each: re-run `cargo fmt` after your LAST edit,
   not once early (a formatting diff fails the job in ~45s, _before_ clippy or
   the tests run at all, so nothing else gets checked); and remember CI lints
   `--workspace --all-targets`, so a per-crate `--lib` clippy never compiles
   test, bench or example targets where the lint may fire.
2. **`/simplify` on the changed code** (the `simplify` skill): reuse,
   simplification, efficiency, altitude. Quality only, not bug-hunting. If it
   proposes a _behaviour_ change rather than a shape change, stop and ask.
3. TDD: the failing test comes first, and prove it fails for the stated reason.
4. Semantic commit messages, proper grammar. Split messages that need "and".

## Before pushing

- Regenerate anything generated (OpenAPI spec, SDKs/clients) — usually a separate
  CI check, and generated files are never hand-edited.
- Run the docs-freshness gate _after_ committing (it diffs committed history) and
  again after fixing, because it cascades code → doc → skill. If no doc change is
  genuinely owed, apply the project's opt-out label. Re-run it after a rebase too:
  when another merge edited the same doc, a rebase can leave the gate satisfied
  for the wrong commit.
- Rebase onto the base branch before pushing, and expect it to invalidate an
  almost-finished CI run. Pay that cost deliberately — worth it when another agent
  is blocked on the same files, not worth it to chase a moving base for its own
  sake.

## PR

- Body: problem, approach, tests, `Closes #N`. No angle brackets in the title.
- Arm auto-merge if the orchestrator says so; never on a PR still under review.
- Do NOT `--delete-branch` a stack base — it closes the dependent PR irrecoverably.
  Retarget the child first, then merge, then rebase the child with `--onto`.
- Superseded CI runs keep displaying their failures next to the live run. Judge
  only the newest run before concluding anything is red.

## Reporting back

State PR numbers and their real state, what you skipped and why, issues closed,
and anything you could not verify. Distinguish "tests passed" from "I believe it
works". Report trades you made honestly — an orchestrator can act on a named
trade and cannot act on a silent one.
