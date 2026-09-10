# PR Review Skill Implementation Plan

> **Executed — see PR #7 (branch `feat/pr-review-skill`).** Every step below is
> done; this file is kept as a record of the intent, not as instructions to run.
> Do not re-apply it verbatim: the code blocks in Task 1 and Task 3 are the
> pre-review versions, and pasting them back would undo the fixes that landed on
> top of them (commit pinning, fence escaping, the all-lenses-failed guard, and
> the worktree mechanism the skills actually use). Read the shipped files, and
> the spec at `docs/superpowers/specs/2026-09-10-pr-review-skill-design.md`,
> for what is true now.

**Goal:** Give the toolkit plugin a thorough, multi-agent PR review capability — point it at a PR and it reviews the diff (reusing `adversarial-review`), categorizes and scores every finding, writes committable suggestions where safe, and submits one real GitHub review (approve/request-changes/comment + inline comments).

**Architecture:** One new orchestrator workflow (`code-review`) nests the existing `adversarial-review` leaf and adds nitpicks, suggestions, a deterministic decision, and a summary. A second, separate leaf workflow (`pr-review-submit`) is the only thing that ever calls the GitHub API to post — kept apart from the engine per this repo's "gates live at the seams" rule. Two skills front these: `deep-review` (engine only, any target, never posts) and `pr-review` (PR-only, posts automatically).

**Tech Stack:** Plain JavaScript workflow scripts (no imports, no filesystem/Node API access — everything happens through `agent()`/`workflow()`/`parallel()`), Markdown SKILL.md files, `gh` CLI (invoked from inside agent prompts, never from the workflow script itself), Python `unittest` + `scripts/validate.py` for structural checks.

**Spec:** `docs/superpowers/specs/2026-09-10-pr-review-skill-design.md`

## Global Constraints

- Every `agent()` call names its model explicitly: `THINK` (`opus`) for judgment, `WORK` (`sonnet`) for mechanical steps — never omit it, never inherit the session model.
- Every leaf workflow returns `refused: null` on success or a reason string on any early exit; its budget guard is named `BUDGET_FLOOR` with a comment saying what it protects.
- Workflow files: `export const meta = {...}` must be a pure literal; `meta.name` must equal the filename stem (checked by `scripts/validate.py`); `meta.phases` titles must match `phase()` call titles exactly.
- SKILL.md files need YAML frontmatter with `name` and `description` (checked by `scripts/validate.py`); both new skills are explicit-trigger-only (slash command or an unambiguous literal ask) — never fire on bare "review this" / "code review".
- `nesting is one level only` — `code-review.js` may call `workflow('toolkit:adversarial-review', …)`, but nothing it calls may itself call `workflow()`.
- Before every commit: `python3 -m unittest discover -s tests && python3 scripts/validate.py` must pass.
- Bump `version` in both `plugins/toolkit/.claude-plugin/plugin.json` and the `toolkit` entry in `.claude-plugin/marketplace.json` — this removes/replaces the existing `/pr-review` command's behavior, which counts as a breaking removal, so bump the minor version (`1.10.0` → `1.11.0`).
- This repo has no `.prettierrc`, and existing workflow files (e.g. `adversarial-review.js`) use single quotes and no semicolons, but the project's PostToolUse format hook runs plain `prettier --write` on any `.js`/`.md` file touched via Write/Edit — it may reformat the code exactly as shown below to prettier's defaults (double quotes, semicolons). That's fine and pre-existing (not something to fix as part of this plan): it doesn't affect `node --check` or `scripts/validate.py`, so don't fight the hook or hand-revert its formatting.

Note on testing approach: these are LLM-orchestration scripts, not deterministic business logic, so there is no meaningful unit-level red/green cycle for _behavior_. The real automated gates this repo has are structural: `tests/test_workflows.py` (every `workflows/*.js` file must `node --check` as valid syntax — it discovers files by glob, so it automatically covers each new file the moment it exists) and `scripts/validate.py` (frontmatter/meta shape). Each task below still follows red→green where it's real (a deliberately broken file first proves the check catches problems), then finishes with a manual smoke test, since agent _behavior_ can only be verified by actually running it.

## File Structure

```
plugins/toolkit/
  workflows/
    code-review.js          # NEW — orchestrator: nests adversarial-review + nitpicks/suggest/decide/summarize
    pr-review-submit.js     # NEW — leaf: the one place that posts to GitHub
  skills/
    deep-review/SKILL.md    # NEW — fronts code-review only, no GitHub side effects
    pr-review/SKILL.md      # NEW — fronts code-review + pr-review-submit, posts automatically
  commands/
    pr-review.md            # DELETE — superseded by skills/pr-review/SKILL.md
  .claude-plugin/plugin.json      # MODIFY — version bump
.claude-plugin/marketplace.json   # MODIFY — version bump (toolkit entry)
```

---

### Task 1: `workflows/code-review.js` — the review engine

**Files:**

- Create: `plugins/toolkit/workflows/code-review.js`
- Test: `tests/test_workflows.py` (existing, discovers this file automatically) + `scripts/validate.py`

**Interfaces:**

- Consumes: `toolkit:adversarial-review` workflow, called as `workflow('toolkit:adversarial-review', { diffPath, target, maxFindings, minLines, reviewModel })` → returns `{ refused, confirmed: [{file, line, title, claim, failure_scenario, severity, evidence}], rejected, gaps: string[], dropped }` (existing shape, unchanged — see `plugins/toolkit/workflows/adversarial-review.js`).
- Produces: `{ refused: string|null, target: string, decision: 'APPROVE'|'COMMENT'|'REQUEST_CHANGES', summary: string, comments: [{file, line, severity: 'critical'|'high'|'medium'|'low'|'nitpick', nitpick: boolean, title, body, suggestion: string}], gaps: string[], counts: {critical, high, medium, low, nitpick} }` — consumed by Task 4's `pr-review` skill and directly rendered by Task 2's `deep-review` skill.

- [x] **Step 1: Write the file with a deliberate syntax error, to prove the syntax check catches it**

Create `plugins/toolkit/workflows/code-review.js` with this content (note the intentionally missing closing brace on `meta`):

```js
export const meta = {
  name: 'code-review',
  description: 'Categorized multi-agent code review with committable suggestions and a decision (approve/comment/request-changes) — no GitHub side effects',
```

- [x] **Step 2: Run the test to verify it fails**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 -m unittest tests.test_workflows -v`
Expected: FAIL — `code-review.js` reports a syntax error from `node --check`.

- [x] **Step 3: Write the complete, correct implementation**

Replace the full file content with:

```js
export const meta = {
  name: "code-review",
  description:
    "Categorized multi-agent code review with committable suggestions and a decision (approve/comment/request-changes) — no GitHub side effects",
  whenToUse:
    "Point at a diff, branch, or PR for a thorough categorized report with suggested fixes but nothing posted anywhere. The pr-review-submit workflow builds on this to post a real GitHub review.",
  phases: [
    {
      title: "Review",
      detail: "nests adversarial-review: 5 lenses, 3 refuters/finding, critic",
    },
    { title: "Nitpicks", detail: "style/maintainability opinions, unrefuted" },
    {
      title: "Suggest",
      detail: "committable suggestion per finding where the fix is mechanical",
    },
    { title: "Summarize", detail: "walkthrough paragraph for the review body" },
  ],
};

// args: { diffPath: string, target: string, maxFindings?: number, minLines?: number, reviewModel?: string, workModel?: string }
const diffPath = args?.diffPath;
if (!diffPath)
  throw new Error(
    "args.diffPath is required — invoke via /deep-review or /pr-review, which produce it with scripts/review-target.sh",
  );
const target = args?.target || "working tree";
const MAX = args?.maxFindings ?? 8;
const THINK = args?.reviewModel ?? "opus"; // nitpicks: judgment, same tier as adversarial-review's lenses
const WORK = args?.workModel ?? "sonnet"; // suggestion + summary: mechanical
const BUDGET_FLOOR = 40_000; // enough for suggestions + summary once nitpicks are in hand

phase("Review");
const review = await workflow("toolkit:adversarial-review", {
  diffPath,
  target,
  maxFindings: MAX,
  minLines: args?.minLines ?? 0, // both callers of this workflow are explicit-only skills — never skip for size
  reviewModel: args?.reviewModel,
});
if (!review || review.refused) {
  return {
    refused: review?.refused ?? "adversarial-review produced no result",
    target,
    decision: null,
    summary: "",
    comments: [],
    gaps: [],
    counts: {},
  };
}

const NITPICKS = {
  type: "object",
  properties: {
    nitpicks: {
      type: "array",
      items: {
        type: "object",
        properties: {
          file: { type: "string" },
          line: { type: "integer" },
          title: {
            type: "string",
            description: "one line, the suggestion alone",
          },
          note: {
            type: "string",
            description:
              "why this would improve the code — an opinion, not a defect",
          },
        },
        required: ["file", "line", "title", "note"],
      },
    },
  },
  required: ["nitpicks"],
};

phase("Nitpicks");
const nitpickResult = await agent(
  `Review a code change (${target}) for style and maintainability opinions ONLY: naming, structure, duplication, minor inefficiencies. Read the unified diff at ${diffPath}. Open surrounding files when needed.
Do NOT report anything with a concrete failure scenario — those are defects, handled elsewhere. Report opinions a reviewer might leave as a "nitpick", nothing that blocks merging.
Line numbers must refer to the NEW side of the diff. Return at most 10 nitpicks; prefer the most valuable ones.`,
  { label: "nitpicks", phase: "Nitpicks", schema: NITPICKS, model: THINK },
);
const nitpicks = (nitpickResult?.nitpicks ?? []).slice(0, 10);
const counts = countSeverities(review.confirmed, nitpicks);
const decision = decide(review.confirmed, nitpicks, review.gaps);

if (budget.total && budget.remaining() < BUDGET_FLOOR) {
  log("budget low; skipping suggestions and the prose summary");
  return {
    refused: null,
    target,
    decision,
    summary: renderSummary(counts, review.gaps, null),
    comments: toComments(review.confirmed, nitpicks, []),
    gaps: review.gaps,
    counts,
  };
}

const candidates = [
  ...review.confirmed.map((f) => ({ ...f, nitpick: false })),
  ...nitpicks.map((n) => ({ ...n, severity: "nitpick", nitpick: true })),
];

const SUGGESTION = {
  type: "object",
  properties: {
    suggestion: {
      type: "string",
      description:
        "replacement text for the flagged line(s), empty string if no safe mechanical fix exists",
    },
  },
  required: ["suggestion"],
};

phase("Suggest");
const suggestions = await parallel(
  candidates.map(
    (f, i) => () =>
      agent(
        `A reviewer flagged ${f.file}:${f.line} (change: ${target}): "${f.title}".
${f.claim || f.note}
Read the actual file. If there is a concrete, low-risk, line-local fix, return the exact replacement text for that line (or small line range) as it should read after the fix — this becomes a GitHub committable suggestion, so it must be a drop-in replacement for those exact lines, nothing else. If the fix requires judgment, touches multiple places, or you are not confident, return an empty string.`,
        {
          label: `suggest:${f.file.split("/").pop()}#${i + 1}`,
          phase: "Suggest",
          schema: SUGGESTION,
          model: WORK,
          effort: "low",
        },
      ).then((r) => r?.suggestion || ""),
  ),
);
const withSuggestions = candidates.map((f, i) => ({
  ...f,
  suggestion: suggestions[i] || "",
}));

phase("Summarize");
const walkthrough = await agent(
  `Write a one-paragraph plain-prose walkthrough of what this change (${target}) does, for a PR review summary. Read the diff at ${diffPath}. No headers, no bullet points, just the paragraph. Do not mention findings or issues — those are added separately.`,
  { label: "walkthrough", phase: "Summarize", model: WORK, effort: "low" },
);

return {
  refused: null,
  target,
  decision,
  summary: renderSummary(counts, review.gaps, walkthrough),
  comments: toComments(review.confirmed, nitpicks, withSuggestions),
  gaps: review.gaps,
  counts,
};

// ---- plain helpers below, no agent calls; hoisted so they can be used above ----

function countSeverities(confirmed, nitpicks) {
  const counts = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    nitpick: nitpicks.length,
  };
  for (const f of confirmed) counts[f.severity] = (counts[f.severity] || 0) + 1;
  return counts;
}

function decide(confirmed, nitpicks, gaps) {
  if (confirmed.some((f) => f.severity === "critical" || f.severity === "high"))
    return "REQUEST_CHANGES";
  if (confirmed.length || nitpicks.length || gaps.length) return "COMMENT";
  return "APPROVE";
}

function toComments(confirmed, nitpicks, withSuggestions) {
  const key = (f) => `${f.file}:${f.line}:${f.title}`;
  const bySuggestion = new Map(
    withSuggestions.map((f) => [key(f), f.suggestion]),
  );
  return [
    ...confirmed.map((f) => ({
      file: f.file,
      line: f.line,
      severity: f.severity,
      nitpick: false,
      title: f.title,
      body: `${f.claim}\n\nFailure scenario: ${f.failure_scenario}`,
      suggestion: bySuggestion.get(key(f)) || "",
    })),
    ...nitpicks.map((n) => ({
      file: n.file,
      line: n.line,
      severity: "nitpick",
      nitpick: true,
      title: n.title,
      body: n.note,
      suggestion: bySuggestion.get(key(n)) || "",
    })),
  ];
}

function renderSummary(counts, gaps, walkthrough) {
  const parts = [
    `**Findings by severity** — critical: ${counts.critical}, high: ${counts.high}, medium: ${counts.medium}, low: ${counts.low}, nitpick: ${counts.nitpick}`,
  ];
  if (walkthrough) parts.push(walkthrough);
  if (gaps.length)
    parts.push(
      `**Risks not verified** (unconfirmed, not counted above):\n${gaps.map((g) => `- ${g}`).join("\n")}`,
    );
  return parts.join("\n\n");
}
```

- [x] **Step 4: Run the test to verify it passes**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 -m unittest tests.test_workflows -v && python3 scripts/validate.py`
Expected: both PASS.

- [x] **Step 5: Commit**

```bash
git add plugins/toolkit/workflows/code-review.js
git commit -m "feat(toolkit): add code-review workflow nesting adversarial-review"
```

---

### Task 2: `skills/deep-review/SKILL.md` — front door with no GitHub side effects

**Files:**

- Create: `plugins/toolkit/skills/deep-review/SKILL.md`
- Test: `scripts/validate.py` (frontmatter shape)

**Interfaces:**

- Consumes: `toolkit:code-review` workflow from Task 1 (`Workflow({ name: "toolkit:code-review", args: {...} })`), `plugins/toolkit/scripts/review-target.sh` (existing, unchanged).
- Produces: the `/deep-review` slash command (skill name doubles as the slash command, matching how `adversarial-review`'s skill works today — see `plugins/toolkit/skills/adversarial-review/SKILL.md`).

- [x] **Step 1: Write the file with missing frontmatter, to prove the validator catches it**

Create `plugins/toolkit/skills/deep-review/SKILL.md` with only:

```markdown
# Deep review

placeholder
```

- [x] **Step 2: Run the validator to verify it fails**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 scripts/validate.py`
Expected: FAIL — reports `deep-review/SKILL.md: no YAML frontmatter`.

- [x] **Step 3: Write the complete file**

````markdown
---
name: deep-review
description: Thorough multi-agent code review — 5 lenses, refuters, critic, plus style nitpicks and committable suggestions — for a diff, branch, or PR. Produces a categorized report only; never touches GitHub. TRIGGER ONLY on /deep-review, or an explicit ask naming "deep review" / "thorough categorized review" for a specific target. DO NOT trigger for bare "review this" / "code review" (the official code-review plugin handles that), for "adversarially review" (that's /adversarial-review directly), or for CodeRabbit follow-ups (the coderabbit skill).
---

# Deep review

Runs the `code-review` workflow (which nests `adversarial-review`) shipped with this plugin. ~35-40 agent calls per run.

## When this fires

| Ask                                            | Action                                                 |
| ---------------------------------------------- | ------------------------------------------------------ |
| `/deep-review [target]`                        | run it                                                 |
| "deep review PR 12 / this branch / my changes" | run it                                                 |
| "review this", "code review"                   | **not this skill** — the official `code-review` plugin |
| "adversarially review ..."                     | **not this skill** — `/adversarial-review` directly    |
| "address the CodeRabbit comments"              | **not this skill** — `coderabbit` skill                |

Invoking this skill is the user's explicit opt-in to multi-agent orchestration — do not ask again once triggered.

## Usage

```
/deep-review                 # working tree (staged + unstaged + untracked)
/deep-review 123             # GitHub PR #123 diff (read-only — nothing is posted)
/deep-review feature/x       # branch vs its merge-base with main
/deep-review 123 --max 12    # verify up to 12 findings (default 8)
```

## Steps

1. Resolve the diff:

   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/review-target.sh" "<target>" "<scratchpad>/review.patch"
   ```

   It prints `kind=… base=… lines=…`. If it exits non-zero the diff is empty — tell the user and stop.

2. Run the workflow, passing the absolute diff path:

   ```
   Workflow({ name: "toolkit:code-review",
              args: { diffPath: "<abs path>", target: "<PR #123 | branch x | working tree>",
                      maxFindings: <n> } })
   ```

3. Render the result:
   - **Decision** — APPROVE / COMMENT / REQUEST_CHANGES, shown first.
   - **Findings by severity** — the counts line from the result's `summary`.
   - **Confirmed findings** — table: `file:line`, severity, title, and the suggestion diff if one exists.
   - **Nitpicks** — listed separately, never counted toward the decision.
   - **Risks not verified** — the critic's gaps, marked unconfirmed.
     Every `file:line` must be a clickable reference.

## Cost

Inherits `adversarial-review`'s `1 + 5 + 3N + 1`, plus 1 nitpick call, plus up to `N + nitpicks` suggestion calls, plus 1 summary call. At the default `N=8` that's roughly 35-40 agent calls.
````

- [x] **Step 4: Run the validator to verify it passes**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 scripts/validate.py`
Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add plugins/toolkit/skills/deep-review/SKILL.md
git commit -m "feat(toolkit): add deep-review skill fronting the code-review workflow"
```

---

### Task 3: `workflows/pr-review-submit.js` — the posting gate

**Files:**

- Create: `plugins/toolkit/workflows/pr-review-submit.js`
- Test: `tests/test_workflows.py` + `scripts/validate.py`

**Interfaces:**

- Consumes: the payload shape produced by Task 1's `code-review` workflow (`decision`, `summary`, `comments`), plus `{ number, repo, cli, repoDir? }`.
- Produces: `{ refused: string|null, posted: boolean, reviewUrl: string|null, decision: string, commentCount: number }` — consumed by Task 4's `pr-review` skill.

- [x] **Step 1: Write the file with a deliberate syntax error**

Create `plugins/toolkit/workflows/pr-review-submit.js` with:

```js
export const meta = {
  name: 'pr-review-submit',
  description: 'Submit a code-review payload as one atomic GitHub PR review'
```

- [x] **Step 2: Run the test to verify it fails**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 -m unittest tests.test_workflows -v`
Expected: FAIL — syntax error in `pr-review-submit.js`.

- [x] **Step 3: Write the complete, correct implementation**

```js
export const meta = {
  name: "pr-review-submit",
  description:
    "Submit a code-review payload (decision, summary, line comments with suggestions) as one atomic GitHub PR review",
  whenToUse:
    "After toolkit:code-review, when the caller has decided to post — the outward, hard-to-reverse step kept separate from the review engine",
  phases: [
    {
      title: "Post",
      detail: "one gh api call: decision + summary + inline comments",
    },
  ],
};

// args: { number, repo, cli, repoDir?, decision, summary, comments: [{file, line, title, body, suggestion}] }
const { number, repo, cli, decision, summary } = args;
if (!number || !repo || !cli || !decision || typeof summary !== "string")
  throw new Error(
    "args.number, repo, cli, decision and summary are required — invoke after toolkit:code-review via the pr-review skill",
  );
const comments = args.comments || [];
const AT = args.repoDir
  ? `Work in the repository checkout at ${args.repoDir} (cd there first; git and CLI commands run against that repo). `
  : "";
const WORK = args?.workModel ?? "sonnet"; // mechanical: build and submit one API payload
const BUDGET_FLOOR = 15_000; // one agent call

if (budget.total && budget.remaining() < BUDGET_FLOOR) {
  return {
    refused: "budget exhausted before posting",
    posted: false,
    reviewUrl: null,
    decision,
    commentCount: 0,
  };
}

const payloadComments = comments.map(
  ({ file, line, title, body, suggestion }) => ({
    path: file,
    line,
    side: "RIGHT",
    body: suggestion
      ? `${title}\n\n${body}\n\n\`\`\`suggestion\n${suggestion}\n\`\`\``
      : `${title}\n\n${body}`,
  }),
);

const POSTED = {
  type: "object",
  properties: {
    posted: { type: "boolean" },
    reviewUrl: { type: "string" },
    commentCount: { type: "integer" },
  },
  required: ["posted", "reviewUrl", "commentCount"],
};

phase("Post");
const posted = await agent(
  `${AT}Submit ONE GitHub review on PR #${number} (${repo}) using ${cli}.

Event: exactly "${decision}" (one of APPROVE, REQUEST_CHANGES, COMMENT).
Body:
${summary}

Comments, each already formatted — use verbatim, do not reword:
${JSON.stringify(payloadComments, null, 1)}

Steps:
1. Get the PR's head commit SHA (\`gh pr view ${number} --repo ${repo} --json headRefOid\`).
2. Write the JSON payload to a temp file: { "commit_id": <sha>, "event": "${decision}", "body": <the body above>, "comments": <the comments array above, verbatim> }.
3. Submit it: \`gh api repos/${repo}/pulls/${number}/reviews --method POST --input <path-to-temp-file>\`.
4. Return whether it posted, the response's html_url, and how many comments were included. If the API call fails, report posted=false and leave reviewUrl empty — do not retry with a different event or fewer comments.`,
  { label: "post", phase: "Post", schema: POSTED, model: WORK, effort: "low" },
);

return {
  refused: posted?.posted
    ? null
    : "gh api call did not confirm the review was posted",
  posted: Boolean(posted?.posted),
  reviewUrl: posted?.reviewUrl || null,
  decision,
  commentCount: posted?.commentCount ?? comments.length,
};
```

- [x] **Step 4: Run the test to verify it passes**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 -m unittest tests.test_workflows -v && python3 scripts/validate.py`
Expected: both PASS.

- [x] **Step 5: Commit**

```bash
git add plugins/toolkit/workflows/pr-review-submit.js
git commit -m "feat(toolkit): add pr-review-submit workflow to post one atomic GitHub review"
```

---

### Task 4: `skills/pr-review/SKILL.md` — front door that posts, replacing the old command

**Files:**

- Create: `plugins/toolkit/skills/pr-review/SKILL.md`
- Delete: `plugins/toolkit/commands/pr-review.md`
- Test: `scripts/validate.py`

**Interfaces:**

- Consumes: `toolkit:code-review` (Task 1) then `toolkit:pr-review-submit` (Task 3) — chained via the skill's own steps, not nested in a script (this is deliberately at the skill layer, not a third workflow, since chaining two already-separate workflows is exactly what "orchestrator calling another orchestrator" would forbid at the script level, and the repo's own convention is to "sequence them from a skill instead").
- Produces: the `/pr-review` slash command.

- [x] **Step 1: Delete the old command and write the new skill file with missing frontmatter, to prove the validator catches it**

```bash
git rm plugins/toolkit/commands/pr-review.md
```

Create `plugins/toolkit/skills/pr-review/SKILL.md` with only:

```markdown
# PR review

placeholder
```

- [x] **Step 2: Run the validator to verify it fails**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 scripts/validate.py`
Expected: FAIL — reports `pr-review/SKILL.md: no YAML frontmatter`.

- [x] **Step 3: Write the complete file**

````markdown
---
name: pr-review
description: Review a GitHub PR with the same multi-agent engine as deep-review, then submit a real GitHub review — a decision (approve/request changes/comment), a summary, and inline line comments with committable suggestions. TRIGGER ONLY on /pr-review <PR>, or an explicit ask naming a specific PR to review and submit a verdict on. DO NOT trigger for bare "review this" / "code review" without a PR, for "adversarially review" (use /adversarial-review directly, which never posts a formal review), for a report-only request (use deep-review), or for CodeRabbit follow-ups (the coderabbit skill).
---

# PR review

Runs `toolkit:code-review` then `toolkit:pr-review-submit` — posts one real GitHub review per invocation. ~35-40 agent calls.

## When this fires

| Ask                                            | Action                                  |
| ---------------------------------------------- | --------------------------------------- |
| `/pr-review <PR#\|URL>`                        | run it                                  |
| "review PR 123 and leave your verdict"         | run it                                  |
| "review this", "code review" (no PR named)     | **not this skill**                      |
| "deep review PR 123" (report only, no posting) | **not this skill** — `deep-review`      |
| "address the CodeRabbit comments"              | **not this skill** — `coderabbit` skill |

Invoking this skill submits a real, visible GitHub review — including possibly "Request changes" — under the user's account, immediately, with no confirmation step. This is the user's explicit opt-in to that; do not ask again once triggered, but do surface exactly what was posted afterward.

## Usage

```
/pr-review 123
/pr-review https://github.com/owner/repo/pull/123
```

## Steps

1. Resolve the PR number and `owner/repo` (from the arg, or `gh pr view --json number,url` in the current checkout), then resolve its diff:

   ```bash
   "${CLAUDE_PLUGIN_ROOT}/scripts/review-target.sh" "<PR#>" "<scratchpad>/review.patch"
   ```

2. Run the review engine:

   ```
   Workflow({ name: "toolkit:code-review",
              args: { diffPath: "<abs path>", target: "PR #<n>" } })
   ```

3. Submit it:

   ```
   Workflow({ name: "toolkit:pr-review-submit",
              args: { number: <n>, repo: "<owner>/<repo>", cli: "gh",
                      decision: <decision from step 2>, summary: <summary from step 2>,
                      comments: <comments from step 2> } })
   ```

4. Report what was posted: decision, comment count, and the review URL. If `posted` is false, surface the failure — do not retry silently.

## Re-running

Re-running on the same PR posts a new review reflecting the current diff — this is how a PR that had `REQUEST_CHANGES` flips to `APPROVE` once fixes land, matching CodeRabbit's own `request_changes_workflow` behavior. There is no incremental "what changed since last review" mode.

## Cost

Same engine as `deep-review` (~35-40 agent calls) plus 1 for posting.
````

- [x] **Step 4: Run the validator to verify it passes**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 scripts/validate.py`
Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add plugins/toolkit/skills/pr-review/SKILL.md plugins/toolkit/commands/pr-review.md
git commit -m "feat(toolkit): replace freeform pr-review command with the pr-review skill"
```

(The `git rm` from Step 1 and the new SKILL.md are committed together — this is one atomic replacement.)

---

### Task 5: Version bump and full validation

**Files:**

- Modify: `plugins/toolkit/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:** none — this task only updates version metadata.

- [x] **Step 1: Bump `plugins/toolkit/.claude-plugin/plugin.json`**

Change:

```json
  "version": "1.10.0",
```

to:

```json
  "version": "1.11.0",
```

- [x] **Step 2: Bump the `toolkit` entry in `.claude-plugin/marketplace.json`**

In the `toolkit` plugin object (not the top-level `metadata.version`, which is a separate release counter), change:

```json
      "version": "1.10.0",
```

to:

```json
      "version": "1.11.0",
```

- [x] **Step 3: Run the full validation suite**

Run: `cd /Users/cedricziel/code/claude-plugins && python3 -m unittest discover -s tests && python3 scripts/validate.py`
Expected: both PASS (this also re-confirms Tasks 1-4's files together, including the version match check between `plugin.json` and `marketplace.json`).

- [x] **Step 4: Commit**

```bash
git add plugins/toolkit/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore(toolkit): bump version to 1.11.0 for code-review and pr-review skills"
```

- [x] **Step 5: Manual smoke test (not automatable — requires a real diff and, for the second check, a real PR)**

1. On a small local branch with a deliberately introduced one-line bug, run `/deep-review <branch>`. Confirm the bug is caught, categorized with a severity, and that re-running after fixing it reports no confirmed findings.
2. Pick one of the user's own low-stakes open PRs and run `/pr-review <PR#>`. Confirm on GitHub that the posted review shows the right decision, a summary with a severity breakdown, and that any inline comments/suggestions render correctly (a suggestion should show GitHub's native "commit suggestion" button). Push a fix and re-run `/pr-review <PR#>`; confirm the new review's decision reflects the fix (flips to `APPROVE` if nothing critical/high remains).
