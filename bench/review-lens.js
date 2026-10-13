export const meta = {
  name: "review-lens",
  description:
    "Bench adversarial-review's correctness lens across model/effort cells against a seeded-bug fixture",
  phases: [
    { title: "Bench", detail: "one cell at a time, repeats in parallel" },
  ],
};

// args: { repoDir: string, cells?: [{ model, effort }], repeats?: number }
// repoDir is the absolute path of this repository; the fixture lives under bench/fixtures/review-lens.
// Returns { refused, cells: [{ cell, outputTokens, trials }], rows } — rows are upload_eval_results JSONL, one per case per trial.
if (!args?.repoDir) throw new Error("args.repoDir is required");
const FIXTURE = `${args.repoDir}/bench/fixtures/review-lens`;
const CELLS = args.cells ?? [
  { model: "opus", effort: "low" },
  { model: "opus", effort: "medium" },
  { model: "opus", effort: "high" },
];
const REPEATS = args.repeats ?? 3;
const BUDGET_FLOOR = 60_000; // one more cell of opus reviews; below this, stop rather than report a half-measured cell

// Kept verbatim from adversarial-review.js; tests/test_bench.py fails if they drift apart.
const LENS =
  "correctness (logic errors, off-by-one, wrong branch conditions, unhandled cases)";

// Each planted bug matches a finding in the same file whose line falls in [lo, hi].
const BUGS = [
  { id: "wait-time-negative", file: "quota/limiter.py", lo: 27, hi: 31 },
  { id: "shared-mutable-overrides", file: "quota/limiter.py", lo: 35, hi: 43 },
  { id: "page-count-floor", file: "quota/usage.py", lo: 1, hi: 4 },
  { id: "grace-multiplier", file: "quota/usage.py", lo: 16, hi: 18 },
];
const DECOY = { id: "decoy-deltas", file: "quota/usage.py", lo: 11, hi: 13 };

const FINDINGS = {
  type: "object",
  properties: {
    findings: {
      type: "array",
      items: {
        type: "object",
        properties: {
          file: { type: "string" },
          line: { type: "integer" },
          title: { type: "string", description: "one line, the claim alone" },
          claim: { type: "string", description: "what is wrong, precisely" },
          failure_scenario: {
            type: "string",
            description: "concrete input/state → wrong output or crash",
          },
          severity: {
            type: "string",
            enum: ["critical", "high", "medium", "low"],
          },
        },
        required: [
          "file",
          "line",
          "title",
          "claim",
          "failure_scenario",
          "severity",
        ],
      },
    },
  },
  required: ["findings"],
};

const prompt = `You are reviewing a code change through ONE lens only: ${LENS}.
The repository under review is ${FIXTURE}/src; read only files under that directory. Paths in the diff are relative to it.
Read the unified diff at ${FIXTURE}/change.diff. Open the surrounding files in the repository when the diff alone is not enough to judge.
Report only defects that have a concrete failure scenario. Do not report style, naming, or hypothetical concerns.
Line numbers must refer to the NEW side of the diff.
Write title/claim/failure_scenario like a very senior engineer: kind, not nice — direct and concrete, no hedging, no padding, no unearned praise.`;

const hits = (f, b) =>
  f.file.replace(/^(\.\/|b\/|src\/)/, "").endsWith(b.file) &&
  f.line >= b.lo &&
  f.line <= b.hi;

function score(findings) {
  const found = BUGS.map((b) => findings.some((f) => hits(f, b)));
  return {
    found,
    recall: found.filter(Boolean).length / BUGS.length,
    decoy: findings.some((f) => hits(f, DECOY)),
    unmatched: findings.filter(
      (f) => !BUGS.some((b) => hits(f, b)) && !hits(f, DECOY),
    ).length,
  };
}

phase("Bench");
const cells = [];
const rows = [];
for (const cell of CELLS) {
  if (budget.total && budget.remaining() < BUDGET_FLOOR) {
    log(
      `budget below ${BUDGET_FLOOR}; stopping before ${cell.model}@${cell.effort}`,
    );
    return { refused: "budget exhausted", cells, rows };
  }
  const name = `${cell.model}@${cell.effort}`;
  const before = budget.spent();
  // Cells run one at a time so the spent() delta is this cell's output tokens alone.
  const results = await parallel(
    Array.from(
      { length: REPEATS },
      (_, t) => () =>
        agent(prompt, {
          label: `${name}#${t + 1}`,
          phase: "Bench",
          schema: FINDINGS,
          model: cell.model,
          effort: cell.effort,
        }),
    ),
  );
  const trials = results.map((r, t) =>
    r
      ? { trial: t + 1, ...score(r.findings), findings: r.findings }
      : { trial: t + 1, error: "agent died" },
  );
  cells.push({ cell: name, outputTokens: budget.spent() - before, trials });
  for (const tr of trials) {
    if (tr.error) {
      rows.push({
        version: name,
        case_id: "run",
        name: "completed",
        error: tr.error,
        trial: tr.trial,
      });
      continue;
    }
    BUGS.forEach((b, i) =>
      rows.push({
        version: name,
        case_id: b.id,
        name: "found",
        score: tr.found[i] ? 1 : 0,
        label: tr.found[i] ? "pass" : "fail",
        trial: tr.trial,
      }),
    );
    rows.push({
      version: name,
      case_id: DECOY.id,
      name: "not-flagged",
      score: tr.decoy ? 0 : 1,
      label: tr.decoy ? "fail" : "pass",
      trial: tr.trial,
    });
    rows.push({
      version: name,
      case_id: "unmatched",
      name: "unmatched-findings",
      score: tr.unmatched,
      trial: tr.trial,
    });
  }
  log(
    `${name}: recall ${trials
      .filter((t) => !t.error)
      .map((t) => t.recall.toFixed(2))
      .join(
        " / ",
      )}, decoy flagged ${trials.filter((t) => t.decoy).length}/${REPEATS}`,
  );
}
return { refused: null, cells, rows };
