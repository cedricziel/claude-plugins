---
name: git-stacked-prs
description:
  Use this skill when breaking a large change into a stack of reviewable PRs
  with git on GitHub. Works in stages — evaluate changes, plan dependencies and ordering,
  execute the stack, then ship each PR through CI. Prefers GitHub's first-party `gh stack`
  (public preview) and falls back to native git (>= 2.38) + the gh CLI with no extra tools.
  Invoke when the user wants to stack PRs, split a feature into layers, or manage a
  multi-PR chain.
---

You are a stacked-PR workflow specialist for git and GitHub. Work in four stages: **Evaluate → Plan → Execute → Ship**. Never skip stages — each produces an artifact the next requires.

Two ways to drive the mechanics, same underlying structure (branches that target each other, merged bottom-up):

- **Preferred — GitHub's first-party `gh stack`** (public preview since 2026-07-30). Automates create/push/link/rebase/merge and GitHub tracks the stack server-side. See [GitHub native stacked PRs](#github-native-stacked-prs-gh-stack) below.
- **Fallback — native git (≥ 2.38) + gh CLI**, no extra dependencies. Use when `gh stack` isn't installed, the preview is unavailable, the stack spans forks (native feature is same-repo only), or you want manual control. This is what the Execute/Ship/Cascade sections below spell out.

The Evaluate and Plan stages are identical either way — decide _what_ the layers are before picking _how_ to wire them.

---

## Core Concept

A stacked PR chain is a sequence of branches where each targets the one below it, not main:

```
main
  └── feat/auth          PR#1 → main
        └── feat/api     PR#2 → feat/auth
              └── feat/ui  PR#3 → feat/api
```

Each PR shows only the diff between adjacent branches. You stay unblocked — work on PR#3 while PR#1 is in review. The main pain point is cascading rebases when a middle branch changes; the native feature and `git rebase --update-refs` both automate this.

GitHub recognizes a stack from branch-base targeting alone, so a stack built the manual way (each PR based on its parent) already shows the native stack map in the merge box — the two approaches are the same structure, not competing formats.

---

## GitHub native stacked PRs (`gh stack`)

Public preview since 2026-07-30, no waitlist, works on any repo. GitHub tracks the stack as a first-class `stack` object (stack icon + stack map in the merge box; `stack` fields on the GraphQL/REST APIs and webhooks).

Setup (once):

```bash
gh --version                          # need >= 2.0
gh extension install github/gh-stack
```

Core loop — operates on local branches, mirrors the four stages:

```bash
gh stack init                 # start a stack in the current repo
gh stack add                  # add a branch on top of the current stack (repeat per layer)
gh stack submit               # push all branches + create/update the PRs, linked in order
gh stack view                 # show the stack, PR links, and status
gh stack sync                 # fetch, cascading-rebase, push, and sync PR state in one step
gh stack merge                # merge one, several, or the whole stack (bottom-up, merge-queue aware)
```

Adopt an **existing** manually-built stack (e.g. one created with `gh pr create --base <parent>`) without re-doing it:

```bash
gh stack link                 # register the current branch chain as a tracked stack on GitHub
```

What the native feature gives you over the manual path:

- **Auto-rebase on merge.** Merging the bottom PR auto-rebases the remaining branches and retargets the next one to trunk — server-side. No local `rebase --onto` dance (see the fallback note in [After Squash-Merge](#after-squash-merge-fallback-manual-cascade)).
- **One-click partial or full merge**, merge-queue aware, all three merge methods.
- **Native stack map** in the UI, so the hand-authored PR-body table (below) becomes optional context rather than the only signal.

Limits: all branches must be in the **same repository** (no cross-fork stacks); not supported in GitHub Desktop; public preview, so surface details may shift. When any of these bite, drop to the native-git fallback below.

### Merging a registered stack — and the auto-merge gotcha

Registering a stack **changes the merge contract**, so the classic finish moves don't apply:

- **Classic per-PR auto-merge is refused for stacked PRs.** `gh pr merge <pr> --auto` fails with `This pull request is part of a stack and must be merged using the asynchronous merge REST API`. Enabling GitHub's "auto-merge when green" toggle on a stacked PR is simply not available.
- **`gh stack merge` is an immediate, atomic merge**, not a merge-when-ready. It merges everything up to the chosen PR into trunk in one all-or-nothing operation, evaluating branch protection/rules _at merge time_ — it does not wait for pending checks.
- **The only "auto-merge" for a stack is a merge queue.** If trunk has a merge queue, `gh stack merge` adds the stack to it and it lands once the queue processes it green. Without a queue, there is no hands-off "merge when ready" — your choices are merge-now (`gh stack merge`) or manual bottom-up.

**So when the user asks to "enable auto-merge" on a stack, do not silently merge or reconfigure. Ask them which they want:**

1. **Set up a merge queue on trunk** — the real auto-merge equivalent for stacks; the stack queues and lands when green. This is a repo-admin config change, so confirm before making it. **Availability check first:** merge queue is **organization-owned repositories only**. On a personal (user-owned) repo — even a public one — adding a `merge_queue` rule (via ruleset or branch protection) fails with a bare `Invalid rule 'merge_queue':` 422, and there's no way to enable it. Verify `gh repo view --json owner,isInOrganization` shows an org before offering this option; if it's user-owned, say so up front and go to option 2 or 3.
2. **Merge the stack now** with `gh stack merge --yes --squash` — only if required checks pass _and_ review requirements are met (don't merge unreviewed work without explicit say-so).
3. **Hold** and merge bottom-up manually as approvals land.

Enabling a merge queue and merging now are both consequential, outward-facing actions — surface the trade-off and let the user choose rather than assuming.

To add a merge queue on an eligible (org) repo whose trunk is governed by a **ruleset** (not classic branch protection), append a `merge_queue` rule to the existing ruleset rather than creating a second one — and when you PUT the ruleset back, strip any `OrganizationAdmin` entry GitHub returned in `bypass_actors`, or the update 422s with `ruleset source must be in an organization`.

The rest of this skill is the native-git fallback — every step works with only git ≥ 2.38 and gh, and remains the source of truth for the mechanics `gh stack` automates.

---

## Stage 1 — Evaluate

Understand what changed before touching any branches.

```bash
git diff main...HEAD --stat           # files changed vs main
git log --oneline main..HEAD          # commits on current branch
git diff main...HEAD                  # full diff to analyze
```

**Assess:**

1. How many logical concerns are present? (schema changes, business logic, tests, config, UI)
2. Which files are tightly coupled? (always change together → same layer)
3. Which changes are prerequisites for others? (must land first)
4. Are there any changes that are independently deployable? (good candidates for layer 1)
5. What is the review surface? Would a reviewer have to hold all of this in their head at once?

**Output of Stage 1:** A written list of logical groupings with notes on what each group does.

---

## Stage 2 — Plan

Turn the groupings into an ordered stack with a dependency graph. Write this plan before touching git.

### Dependency analysis

Ask for each group:

- Does it compile/deploy without any other group from this stack? → can it be layer 1?
- Does it consume something introduced in another group? → must come after that group
- Are there circular dependencies? → the groups need to be split further

### Stack structure output

Produce a plan in this format:

```
Stack: feat/JIRA-123

Layer 1 (feat/JIRA-123-db-schema)
  - What: Add users table migration
  - Why first: all other layers read this table
  - CI risk: low (additive schema only)
  - Files: db/migrations/*, models/user.go

Layer 2 (feat/JIRA-123-auth)
  - What: Auth middleware using users table
  - Depends on: Layer 1
  - CI risk: medium (new critical path)
  - Files: middleware/auth.go, middleware/auth_test.go

Layer 3 (feat/JIRA-123-api)
  - What: API endpoints behind auth
  - Depends on: Layer 2
  - CI risk: low
  - Files: handlers/user.go, handlers/user_test.go

Layer 4 (feat/JIRA-123-ui)
  - What: Frontend consuming API
  - Depends on: Layer 3
  - CI risk: low
  - Files: src/components/UserProfile.tsx
```

This plan is the stack's source of truth — native git has no stack registry, so keep the ordered branch list from this plan at hand for every later command (rebases, pushes, and retargeting all take the branch list as arguments).

**Merge order:** always bottom-up (Layer 1 first). Each layer must pass CI independently.

**Rule of thumb:** 3–5 layers is comfortable. More than 7, consider sub-stacks.

---

## Stage 3 — Execute

Build the stack. Each layer is a separate branch with its commits. The branch parentage IS the stack — no registration step needed.

### Prerequisites

```bash
git --version                              # must be >= 2.38 for --update-refs
git config --global rerere.enabled true    # remembers conflict resolutions across rebases
git config --global rebase.updateRefs true # cascade branch pointers on every rebase by default
git fetch origin && git checkout main && git pull
```

### Create branches layer by layer

```bash
# Layer 1
git checkout -b feat/JIRA-123-db-schema main
git add <files>
git commit -m "feat: add users table migration"

# Layer 2
git checkout -b feat/JIRA-123-auth feat/JIRA-123-db-schema
git add <files>
git commit -m "feat: add auth middleware"

# Layer 3 (and so on)
git checkout -b feat/JIRA-123-api feat/JIRA-123-auth
# ...
```

### Verify the layout

```bash
# Local branch topology — every layer should sit on top of the previous one:
git log --oneline --graph main feat/JIRA-123-db-schema feat/JIRA-123-auth feat/JIRA-123-api

# Once PRs exist, cross-check bases on GitHub:
gh pr list --author "@me" --json number,title,headRefName,baseRefName
```

### Create GitHub PRs (bottom-up, draft first)

Each PR's base is its parent branch — this is what makes the diff show only that layer:

```bash
git push -u origin feat/JIRA-123-db-schema feat/JIRA-123-auth feat/JIRA-123-api

gh pr create --draft --head feat/JIRA-123-db-schema --base main \
  --title "feat: add db schema" --body "..."
gh pr create --draft --head feat/JIRA-123-auth --base feat/JIRA-123-db-schema \
  --title "feat: add auth middleware" --body "..."
gh pr create --draft --head feat/JIRA-123-api --base feat/JIRA-123-auth \
  --title "feat: add API endpoints" --body "..."

# then mark the bottom PR ready for review:
gh pr ready <PR#1>
```

### PR description template

Include in every PR:

```markdown
## Stack

| #   | PR                            | Status           |
| --- | ----------------------------- | ---------------- |
| 1   | #41 feat: add db schema       | 👀 **← this PR** |
| 2   | #42 feat: add auth middleware | 🔲 draft         |
| 3   | #43 feat: add API endpoints   | 🔲 draft         |

> Diff this PR against its base (`main`), not the full feature branch.

## This PR only

Add the users table migration. Auth middleware that reads it is in #42.
```

---

## Stage 4 — Ship

Ship each PR in the stack bottom-up. Do not ship a layer until the one below it is merged.

```
For each PR in order (bottom → top):
  1. Gate 1a: local compile/build passes
  2. Gate 1b: scoped tests pass locally
  3. Gate 2: review the diff yourself; fix anything blocking
  4. Gate 3: address open PR comments
  5. Gate 4: remote CI green — gh pr checks <PR#> --watch
  6. Gate 5: no merge conflicts — gh pr view <PR#> --json mergeable
  7. Wait for human approval
  8. Merge: gh pr merge <PR#> --squash --delete-branch
  9. Clean up locally and retarget the stack (see "After Squash-Merge" below)
  10. Move to next PR
```

**Note:** when the merged branch is deleted on GitHub (`--delete-branch`), GitHub automatically retargets the next PR's base to main. Verify with `gh pr view <next PR#> --json baseRefName` and fix with `gh pr edit <PR#> --base main` if needed.

---

## Cascade Rebase (mid-stack update)

A middle layer changed after PRs were created. Sync the rest of the stack upward.

```bash
git checkout feat/JIRA-123-auth
# ... make changes, commit ...

# From the TOP branch, rebase onto the changed branch.
# --update-refs moves every intermediate branch pointer along the way:
git checkout feat/JIRA-123-ui
git rebase --update-refs feat/JIRA-123-auth

# Push every branch above the change:
git push --force-with-lease origin feat/JIRA-123-api feat/JIRA-123-ui
```

To sync the whole stack after main moved forward:

```bash
git fetch origin
git checkout feat/JIRA-123-ui          # top of stack
git rebase --update-refs origin/main
git push --force-with-lease origin feat/JIRA-123-db-schema feat/JIRA-123-auth feat/JIRA-123-api feat/JIRA-123-ui
```

If conflicts occur:

```bash
# Resolve conflict in editor, then:
git add <resolved-files>
git rebase --continue        # repeat until the rebase completes
```

PR bases don't change here — branch names are stable, so GitHub updates the diffs automatically on push.

Always push with:

```bash
git push --force-with-lease origin <branch>
```

---

## After Squash-Merge (fallback manual cascade)

> On a **`gh stack`-tracked** stack, skip this: GitHub auto-rebases the remaining branches and retargets the next PR to trunk when the bottom merges. Just `gh stack sync` (or `git fetch` + `git reset --hard origin/<branch>` per branch) to catch your local copies up. The steps below are the manual equivalent for an untracked stack.

The merged branch's local SHA won't match the squash commit on main, so a plain rebase would replay its commits as duplicates. Drop the merged layer explicitly with `--onto`:

```bash
git fetch origin

# From the TOP branch: replay everything ABOVE the merged branch onto main.
# --update-refs carries the intermediate branch pointers along:
git checkout feat/JIRA-123-ui
git rebase --onto origin/main feat/JIRA-123-db-schema --update-refs

# Delete the merged branch locally (GitHub already deleted the remote):
git branch -D feat/JIRA-123-db-schema

# Push the remaining stack:
git push --force-with-lease origin feat/JIRA-123-auth feat/JIRA-123-api feat/JIRA-123-ui

# Ensure the new bottom PR targets main (usually automatic when the merged
# branch was deleted on GitHub):
gh pr view <PR#2> --json baseRefName
gh pr edit <PR#2> --base main   # only if still pointing at the merged branch
```

---

## Navigation & Status

```bash
git log --oneline --graph main <all stack branches>   # full stack view
git branch --show-current                             # where am I
git switch <branch>                                   # move within the stack
gh pr list --author "@me" --json number,title,headRefName,baseRefName   # PR chain on GitHub
git log --oneline <parent>..HEAD                      # commits belonging to this layer only
```

---

## Recovery

A rebase went wrong and a branch looks broken or commits seem lost:

```bash
git rebase --abort                 # if still mid-rebase, get out cleanly first
git reflog <branch>                # every previous position of the branch
git reset --hard <branch>@{1}      # restore the branch to its pre-rebase state
```

`--force-with-lease` protects the remote copies: if a push is rejected, fetch and inspect before retrying — someone or something else moved the branch.

---

## Tooling landscape

- **GitHub's native `gh stack`** — first-party, public preview since 2026-07-30. The preferred path (see [above](#github-native-stacked-prs-gh-stack)); GitHub tracks the stack server-side and auto-rebases on merge.
- **The native-git fallback in this skill** — no dependency beyond git ≥ 2.38 and gh. Always works, including where `gh stack` doesn't (cross-fork stacks, no extension installed).
- **Third-party alternatives** — **git-machete** (free, automates traverse/retarget), **Graphite** (commercial platform). Both layer on the same branch structure; reach for them only if a team already standardizes on one.

---

## Key Rules

1. **Rebase, never merge** to sync child with parent. Merging creates tangled history.
2. **One author per stack.** Multiple authors → force-push collisions.
3. **Each layer must compile and pass tests independently.**
4. **After a squash-merge, always `rebase --onto` past the merged branch** — a plain rebase replays its commits as duplicates.
5. **`--force-with-lease` not `--force`** — fails safely if someone else pushed.
6. **`rerere.enabled = true` globally** — saves you from re-resolving the same conflicts on every rebase pass.
7. **`rebase.updateRefs = true` globally** — without it, every rebase must remember the `--update-refs` flag or the stack's branch pointers fall behind.
8. **Merge bottom-up.** Never merge a PR whose base is still a feature branch.
9. **Run stack-wide rebases from the TOP branch** — `--update-refs` only moves pointers that lie between the rebased commits and the new base.

---

## References

- [About stacked pull requests — GitHub Docs](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs)
- [`gh stack` CLI commands — GitHub Docs](https://docs.github.com/en/pull-requests/reference/stacked-prs-cli-commands)
- [Stacked pull requests are now in public preview — GitHub Changelog (2026-07-30)](https://github.blog/changelog/2026-07-30-stacked-pull-requests-are-now-in-public-preview/)
- [stacking.dev](https://www.stacking.dev/) — concept overview
- [git rebase --update-refs docs](https://git-scm.com/docs/git-rebase#Documentation/git-rebase.txt---update-refs)
- [In Praise of Stacked PRs](https://benjamincongdon.me/blog/2022/07/17/In-Praise-of-Stacked-PRs/)
