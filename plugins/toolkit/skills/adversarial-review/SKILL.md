---
name: adversarial-review
description: Multi-agent adversarial code review of a PR, branch, or the working tree — five review lenses in parallel, then every finding must survive three independent refutation attempts, then a critic asks what was missed. Use when the user invokes /adversarial-review, asks for an "adversarial", "thorough", "multi-agent" or "paranoid" review before merging, or wants review findings verified rather than just listed.
---

# Adversarial review

Runs the `adversarial-review` workflow shipped with this plugin. Invoking this skill is the user's explicit opt-in to multi-agent orchestration — do not ask again.

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
   Workflow({ name: "adversarial-review",
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
