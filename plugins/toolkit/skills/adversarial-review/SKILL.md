---
name: adversarial-review
description: Multi-agent adversarial code review (5 lenses, 3 refuters per finding, critic). TRIGGER ONLY on an explicit ask — the user types /adversarial-review, or says "adversarial review" / "adversarially review" / "run the adversarial review" naming a PR, branch, or the working tree. DO NOT trigger for "review this", "code review", "thorough review", "look over my changes", or CodeRabbit follow-ups — those are /code-review (or the coderabbit skill). Never self-trigger on PR size or risk; at most SUGGEST it in one line when a diff touches auth, migrations, concurrency, or exceeds 500 lines.
---

# Adversarial review

Runs the `adversarial-review` workflow shipped with this plugin. ~30 agent calls per run.

## When this fires

| Ask | Action |
|---|---|
| `/adversarial-review [target]` | run it |
| "adversarial(ly) review PR 12 / this branch / my changes" | run it |
| "review this", "code review", "thorough review" | **not this skill** — `/code-review` |
| "address the CodeRabbit comments" | **not this skill** — coderabbit skill |
| a large or risky diff you happen to be working on | do not run; you may suggest it in one line |

Invoking this skill is the user's explicit opt-in to multi-agent orchestration — do not ask again once triggered.

## Usage

```
/adversarial-review                 # working tree (staged + unstaged + untracked)
/adversarial-review 123             # GitHub PR #123 (needs gh)
/adversarial-review feature/x       # branch vs its merge-base with main
/adversarial-review 123 --max 12    # verify up to 12 findings (default 8)
/adversarial-review 123 --comment   # also post confirmed findings as inline PR comments
```

## Steps

1. Resolve the diff:
   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/review-target.sh" "<target>" "<scratchpad>/review.patch"
   ```
   It prints `kind=… base=… lines=…`. If it exits non-zero the diff is empty — tell the user and stop.
   If `lines` exceeds ~3000, warn that reviewers will read the diff in chunks and suggest splitting the PR (see the git-stacked-prs skill).

2. Run the workflow, passing the absolute diff path:
   ```
   Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/adversarial-review.js",
              args: { diffPath: "<abs path>", target: "<PR #123 | branch x | working tree>",
                      maxFindings: <n>, reviewModel: "sonnet" } })
   ```
   `reviewModel: "sonnet"` follows the default-delegation rule; omit it (inherit the session model) only if the user asks for maximum rigour.

3. Render the result:
   - **Confirmed** — table: `file:line`, severity, title, failure scenario, one line of refuter evidence. These are the findings.
   - **Refuted** — one line each: title and the strongest refutation. Keeps the filtering visible.
   - **Gaps** — the critic's list, verbatim, marked as unverified.
   - Mention `dropped` if non-zero.
   Every `file:line` must be a clickable reference.

4. With `--comment` on a PR target: post each confirmed finding as an inline review comment via `gh api repos/{owner}/{repo}/pulls/<n>/comments` (body = title + failure scenario + evidence; `line` on the new side, `side: RIGHT`). Never post refuted findings or gaps.

## Cost

1 + 5 + 3·N + 1 agents (N = verified findings). At the default N=8 that is ~31 calls; the reviewers and refuters are the bulk, which is why they default to `sonnet`.
