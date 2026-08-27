---
name: issue-run
description: End-to-end issue workflow composed of separate workflows with human gates between them — issue-triage (verify the premise) → decision gate → fix-small → optional adversarial-review → PR gate → pr-open → report. TRIGGER ONLY when the user types /issue-run, or literally says "run the issue workflow" / "issue-run" for a specific issue. DO NOT trigger for "fix issue 12", "look at this issue", "what does issue 12 say" — handle those directly. ~10 agents per run (~40 with --review).
---

# /issue-run

```
/issue-run 123                       # issue in the current repo's origin
/issue-run owner/repo#123
/issue-run https://github.com/owner/repo/issues/123   # GitHub or Forgejo URL
/issue-run 123 --review              # adversarial-review before the PR
/issue-run 123 --yes                 # skip both gates (headless / routine use)
```

Invoking this skill is the user's explicit opt-in to the workflows below. Each stage is its own top-level workflow; never nest them.

Call workflows as `Workflow({ name: "toolkit:<name>", args })` (plugin workflows are namespaced and registered at plugin load); if that reports "not found" the plugin was loaded before the workflow existed — fall back to `Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/<name>.js", args })`. If the session did not start inside the repository, pass `repoDir: "<absolute path to the checkout>"` in every args object.

## Steps

1. **Resolve the reference**
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/issue-ref.sh" "<ref>"      # → forge= host= repo= number= cli=
   ```
   Non-zero exit: show the error and stop. Confirm the resolved `cli` is authenticated against `host`. Resolve the base branch once:
   ```bash
   BASE=$("${CLAUDE_PLUGIN_ROOT}/scripts/default-branch.sh")
   ```

2. **Triage** — `Workflow({ name: "toolkit:issue-triage", args: { number, repo, cli } })`.
   Show: decision, reasons, size, premise result (did the repro fail?), duplicates. Then

   **GATE 1** (skip with `--yes`): ask the user to confirm the decision or override it.
   - `close-fixed` / `close-invalid` / `duplicate` / `needs-info`: `Workflow({ name: "toolkit:issue-resolve", args: { number, repo, cli, decision, proposedComment, proposedLabels, duplicateOf } })`. Report and stop.
   - `fix-stack`: stop here and hand off — the change needs a proposal first (OpenSpec `openspec-propose` skill where the repo has `openspec/`, otherwise the git-stacked-prs skill Stage 1–2), then `/stack-execute`. Do not implement in this run.
   - `fix-small`: continue.

3. **Fix** — `Workflow({ name: "toolkit:fix-small", args: { number, repo, base: BASE, issue: result.issue, premise: result.evidence.premise, fleetBrief: "${CLAUDE_PLUGIN_ROOT}/instructions/fleet-brief.md" } })`.
   If `ok` is false or `impl.blocked` is set: report why and stop. No PR for an unverified fix.

4. **Review** (only with `--review`) — `Workflow({ name: "toolkit:adversarial-review", args: { target: "branch <branch>", diffPath, maxFindings: 6 } })` after producing `diffPath` with `scripts/review-target.sh <branch> <scratchpad>/review.patch`. Critical/high confirmed findings: feed them back through one more `fix-small` run with `branch` set and the findings appended to `issue.claims`; otherwise carry them into the PR checklist.

5. **GATE 2** (skip with `--yes`): show the branch, diff size, tests run, verifier result, and confirmed findings. Ask: open the PR?

6. **PR** — `Workflow({ name: "toolkit:pr-open", args: { branch, base: BASE, number, repo, cli, summary: { problem: impl.problem, approach: impl.approach, tests: verify.testsRun }, findings } })` — the summary comes from the fix-small result, not from memory.

7. **Report** in the fleet-brief format: PR number and its real CI state, what was skipped and why, issue closed or not, anything not verified, trades made.

## What this skill never does on its own

Comment, close, label, open a PR, or merge without passing a gate (unless `--yes` was given). Merging is never part of this skill.
