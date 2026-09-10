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
if (!review || review.refused)
  return {
    refused: review?.refused ?? "adversarial-review produced no result",
    target,
    decision: null,
    summary: "",
    comments: [],
    gaps: [],
    counts: {},
  };

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
        "replacement text for the single flagged line, empty string if no safe single-line fix exists",
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
Read the actual file. If there is a concrete, low-risk fix that fits entirely on line ${f.line} alone, return the exact replacement text for that ONE line as it should read after the fix. This becomes a GitHub committable suggestion anchored to that single line: GitHub replaces exactly that line with what you return, so returning more than one line duplicates the surrounding code instead of fixing it.
Return an empty string — no suggestion — if the fix needs to touch any other line, spans a range, requires judgment, or you are not confident. A missing suggestion is fine; a wrong one is applied with one click.`,
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
