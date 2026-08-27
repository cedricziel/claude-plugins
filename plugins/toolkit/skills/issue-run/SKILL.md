---
name: issue-run
description: End-to-end issue workflow composed of separate workflows with human gates between them — issue-triage (verify the premise) → decision gate → fix-plan (opus) → plan gate → fix-small → optional adversarial-review → PR gate → pr-open → pr-watch (review loop) → report. TRIGGER ONLY when the user types /issue-run, or literally says "run the issue workflow" / "issue-run" for a specific issue. DO NOT trigger for "fix issue 12", "look at this issue", "what does issue 12 say" — handle those directly. ~15 agents per run (~45 with --review).
---

# /issue-run

```
/issue-run 123                       # issue in the current repo's origin
/issue-run owner/repo#123
/issue-run https://github.com/owner/repo/issues/123   # GitHub or Forgejo URL
/issue-run 123 --review              # adversarial-review before the PR (skipped automatically under 100 diff lines)
/issue-run 123 --no-watch            # stop after pr-open; do not babysit reviews
/issue-run 123 --yes                 # skip all gates (headless / routine use)
```

Invoking this skill is the user's explicit opt-in to the workflows below. Each stage is its own top-level workflow; never nest them.

Call workflows as `Workflow({ name: "toolkit:<name>", args })` (plugin workflows are namespaced and registered at plugin load); if that reports "not found" the plugin was loaded before the workflow existed — fall back to `Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/<name>.js", args })`. If the session did not start inside the repository, pass `repoDir: "<absolute path to the checkout>"` in every args object.

## Steps

1. **Resolve the reference**
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/issue-ref.sh" "<ref>"      # → forge= host= repo= number= cli=
   BASE=$("${CLAUDE_PLUGIN_ROOT}/scripts/default-branch.sh")
   ```
   Non-zero exit: show the error and stop. Confirm the resolved `cli` is authenticated against `host`.

2. **Triage** — `Workflow({ name: "toolkit:issue-triage", args: { number, repo, cli } })`.
   Show: decision, reasons, size, premise result (did the repro fail?), duplicates.

   **GATE 1** (skip with `--yes`): confirm or override the decision.
   - `close-fixed` / `close-invalid` / `duplicate` / `needs-info` → `Workflow({ name: "toolkit:issue-resolve", args: { number, repo, cli, decision, proposedComment, proposedLabels, duplicateOf } })`. Report and stop.
   - `fix-stack` → stop and hand off: the change needs a proposal first (OpenSpec `openspec-propose` where the repo has `openspec/`, otherwise git-stacked-prs Stage 1–2), then `/stack-execute`.
   - `fix-small` → continue. If the issue is a bug and `premise.reproduced` is `no`, say so: fix-small will refuse; the user can override by editing the claims or supplying a repro.

3. **Plan** — `Workflow({ name: "toolkit:fix-plan", args: { number, repo, issue: result.issue, evidence: result.evidence, sizeLines: triage.size.lines } })`.
   It refuses itself under 50 estimated lines (a diff you can describe in one sentence needs no plan) — then skip Gate 2. Otherwise show the plan (files, failing test, steps, risks, out of scope, estimated lines) and the critic's objections.

   **GATE 2** (skip with `--yes`): approve, edit, or stop. `tooBig` → treat as `fix-stack`.

4. **Fix** — `Workflow({ name: "toolkit:fix-small", args: { number, repo, base: BASE, issue: result.issue, premise: result.evidence.premise, plan, fleetBrief: "${CLAUDE_PLUGIN_ROOT}/instructions/fleet-brief.md" } })`.
   `refused` (every leaf returns `refused: null` on success, or a reason) or `ok: false` → report why and stop. No PR for an unverified fix. Report the verifier's independent test and any `gaming` evidence verbatim.

5. **Review** (only with `--review`) — produce the diff with `scripts/review-target.sh <branch> <scratchpad>/review.patch` (it prints `lines=`), then
   `Workflow({ name: "toolkit:adversarial-review", args: { target: "branch <branch>", diffPath, diffLines, maxFindings: 6 } })`.
   Critical/high confirmed findings → one more `fix-small` run with `branch` set and the findings appended to `issue.claims`; the rest go into the PR checklist.

6. **GATE 3** (skip with `--yes`): branch, diff size, tests, verifier result, confirmed findings. Open the PR and let pr-watch babysit it? Approval here covers everything pr-watch does on that PR (replies, resolving applied threads, re-requesting review, marking it ready once CI is green and nothing is escalated).

7. **PR** — `Workflow({ name: "toolkit:pr-open", args: { branch, base: BASE, number, repo, cli, summary: { problem: impl.problem, approach: impl.approach, tests: verify.testsRun, risk, focus }, findings } })` — the summary comes from the fix-small result, not from memory.

8. **Watch** (unless `--no-watch`) — `Workflow({ name: "toolkit:pr-watch", args: { number: pr, repo, cli, branch, base: BASE, maxRounds: 3 } })`.
   It applies valid review comments, pushes back once with evidence, escalates decisions, re-requests review, and marks the PR ready when nothing is left. It never merges.

9. **Report** in the fleet-brief format: PR number and its real CI/review state, escalations that need the user, what was skipped and why, issue closed or not, anything not verified, trades made.

## What this skill never does on its own

Comment, close, label, or open a PR without passing a gate (unless `--yes` was given); everything pr-watch does is covered by Gate 3. Merging is never part of this skill.
