# Issue workflow — research summary (2026-08-28)

What the evidence says, and how the toolkit workflows apply it.

| Finding | Evidence | Applied in |
|---|---|---|
| Reproduce before fixing | Devin: resolve rate 13.9% → 23% with tests supplied upfront; SWE-bench Verified exists because unreproducible issues poisoned results; "reproduction/verification failure" is a distinct late failure class (arXiv 2509.13941) | `issue-triage` premise agent; `fix-small` refuses unreproduced bugs |
| An explicit plan helps; skip it for one-sentence diffs | SWE-Debate ablation −6 pp without an edit plan (2507.23348); Jules' planning critic −9.5% failures; Anthropic: Opus lead + Sonnet workers beat solo Opus by 90%; Claude Code best practices: "if you could describe the diff in one sentence, skip the plan" | `fix-plan` (opus + critic), skipped under 50 lines |
| Reviewers report findings even when none exist; refute them, and skip review on small diffs | Adversarial Review (2608.18167) on the cost/quality Pareto front but wasted on easy tasks; LLM judges are position-biased (51% vs 24% win rate by slot, ACL 2024) and self-preferring | `adversarial-review`: refuted-if-uncertain, findings order rotated per refuter, skipped under 100 lines |
| Passing tests ≠ correct | 21–33% of "passing" SWE-bench patches overfit visible tests (2511.16858); 1 in 5 top-agent patches wrong under strengthened tests (SWE-ABS); refinement rounds increase overfitting | `fix-small` verifier writes an independent test from the issue text and checks for test-gaming; one repair round only |
| Long trajectories predict failure | Failed issues take ~3.5× more rounds; diminishing returns past ~25 (2509.13941); SWE-agent resolved runs cost half of unresolved | Budget guards in every leaf; `blocked` stops the run; `pr-watch` ≤3 rounds |
| Agent PRs die in review | 46% of agent fixes rejected (2606.13468); 56% of CodeRabbit comments rejected, mostly invalid/out of scope (2607.03316); threads ending with an agent reply are rejected more | `pr-watch`: classify apply / push back once with evidence / escalate; never resolve without acting; re-request review explicitly |
| Guardrails belong in infra | Draft-first PRs (Copilot, Claude Action); human merges; never force-push/delete; auto-merge only under real checks; retry only known-flaky CI; 200–400 LOC review sweet spot (Cisco/SmartBear), ~100 typical (Google) | `pr-open` draft + label; `pr-watch` never merges; plan targets 200 lines, 500 hard cap |
| Reward hacking rises with "don't cheat" prompts | METR: hacking 30% → 70–95% after anti-hack instructions; Cursor: 57% of SWE-bench Pro solves were upstream lookups | Verifier *checks* for gaming instead of prompting against it |

Sources: Anthropic engineering (building effective agents; multi-agent research system; Claude Code best practices), OpenAI (SWE-bench Verified audits), Cognition, Google (Jules critic; eng-practices small CLs), GitHub docs, CodeRabbit docs, arXiv 2507.23348, 2608.18167, 2511.16858, 2603.00520, 2509.13941, 2606.13468, 2607.03316, 2305.17926.
