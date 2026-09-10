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
