# Research And Validation

This file answers which research method fits a given design question, how many participants a usability round needs, and what evidence justifies shipping instead of another round. Read it when someone proposes a test, quotes a participant count, or asks for proof that a design works. It does not cover accessibility testing mechanics (`accessibility.md`) or the review pass itself (`review-checklist.md`).

## Choose The Method By The Question

- Separate generative from evaluative questions: "what do people need" comes before "can they use this" [2].
- Separate behavioural from attitudinal: observation and analytics show what happened, surveys show what people say about it [2][5].
- Pick the smallest method that can falsify the claim under discussion: a heuristic pass before five users, five users before a survey, an A/B test last [7][inference].
- Use qualitative work for causes and quantitative work for size; neither substitutes for the other [2][4].
- Write down the decision the study will change before recruiting. No decision, no study [inference].
- Match the artifact to the question: paper or prototype for flow, live build for interaction detail, tree for hierarchy, live traffic for outcome size [inference].
- Recruit people who match the task, not colleagues or friends; a proxy participant produces proxy findings [2][inference].
- Keep stakeholders out of the room unless they are taking notes; a stakeholder defending a decision contaminates the session [2][inference].

## Five Users, And What It Cannot Tell You

- Five participants per round typically surface about 85% of usability problems in one comparable user group [1].
- The model behind it: a single user exposes roughly 31% of problems on average, and findings overlap heavily after the fifth [1].
- Spend a fixed budget on three rounds of five rather than one round of fifteen; fixes between rounds teach more than extra users [1].
- Use 3–4 participants per group when testing two distinct groups, and 3 per group for three or more groups [1].
- Five users cannot estimate prevalence, compare options statistically, size a market, or validate pricing [1][2].
- Expect about 15% of problems to survive a round, and redesigns to introduce new ones; a redesign needs its own test [1].
- One participant can mislead through accident or an unrepresentative approach; three is the minimum for a sense of variety [1].
- Report "5 of 5 participants", never "100% of users" [inference].

## Running A Task-Based Test

- Write tasks as scenarios from the participant's life, with a goal and a reason, not a route through the interface [2].
- Strip interface nouns from task wording; a task that contains the button label tests reading, not finding [3].
- Ask participants to read the task aloud and think aloud; silent success hides the reasoning behind a failure [2].
- Record task success and time on task at minimum; add error counts and satisfaction when severity needs defending [2][inference].
- Do not rescue a stuck participant before a fixed time limit; a rescue erases the finding [inference].
- Ask "what were you expecting?" after a failure, not "would you like it if…"; hypotheticals produce polite fiction [inference].
- Do not demo the intended path, explain the interface, or use leading questions before or during the task [2].
- Pilot with one or two participants and rewrite any task that needed explanation [3].
- Keep the clip: finding, timestamp, participant words. A finding without evidence is an opinion [inference].

## Moderated, Unmoderated, And IA Methods

- Use moderated sessions for why and for early prototypes, where the follow-up question is the point [2]; add moderated sessions when assistive-technology users are in scope [inference].
- Use unmoderated sessions for scale, benchmarks, and simple tasks; you lose follow-ups, so misreads stay unexplained [2].
- Both can run remotely; the difference is who administers the task, not the location [2].
- Test information architecture before visual design with tree testing: a hierarchy with no layout, content, or styling [3].
- Tree-test tasks must not contain the category label; describe the need instead of the menu item [3].
- Read three numbers from a tree test: success rate, time, and directness (whether users went straight to the right place without detours) [3].
- Compare alternate trees between subjects; showing both in one session contaminates the second [3].
- Treat a tree test as qualitative for insight, and as quantitative only with an adequate sample; it explains findability, not desire [3].
- Record first click in a prototype as a cheap hierarchy signal; a wrong first click usually predicts a failed task [inference].

## Cheap Pre-Tests: Heuristic Evaluation And Analytics

- Run a heuristic evaluation against a fixed heuristic set, scoped to one task, section, user group, or device [7].
- Timebox each evaluator to about 1–2 hours, and use three to five independent evaluators [7].
- Keep evaluators separate until their own pass is finished; shared notes anchor the group on the first reviewer's findings [7].
- Consolidate afterwards, cluster duplicates, and send disagreements to a user test rather than settling them by seniority [7].
- Treat the output as hypotheses about problems, not findings about users; it cannot replace research [7].
- Do not log every heuristic violation as a defect; a violation can be the right trade-off for the context [7].
- Record heuristic, element, evidence, and proposed fix; "violates recognition rather than recall" alone is not actionable [inference].
- Use analytics to find where people leave, not why; instrument funnels and events, then watch five users at the worst step [6][inference].
- Define metrics as goal → signal → metric before launch; the HEART categories (happiness, engagement, adoption, retention, task success) are a coverage checklist, not a score [6].

## A/B Tests And Surveys: Preconditions

- Run an A/B test only with a hypothesis from prior research, one changed element, a primary metric, and guardrail metrics [4].
- Size the test before starting: baseline rate, minimum detectable effect, significance threshold; then run at least one to two weeks to absorb weekly variation [4].
- Skip A/B on low-traffic pages; without thousands of interactions the difference is noise [4].
- Do not bundle several changes into one variant; you learn that the bundle moved a number, not which change did it [4].
- Expect most tests to lose: about one in seven wins, so a losing test is normal rather than a failed team [4].
- Do not let one winning metric overrule guardrails; a deceptive variant can raise conversion and destroy retention [4].
- Use SUS after a study for comparable perceived usability: ten items, five response options, scored 0–100, average around 68 [5].
- Report SUS as a percentile, not a percentage; 70 sits near the middle, not at 70% [5].
- SUS is not diagnostic and correlates only modestly with task performance; use it for trends across releases, not to explain a failure [5].

## Reporting Findings And Deciding To Ship

- Write each finding as observation → evidence → impact → recommendation, with task and participant count [2][inference].
- Rate severity by frequency × impact × reversibility; a rare data-loss bug outranks a common cosmetic one [inference].
- Separate what you saw from what you conclude; label the interpretation so a later reader can challenge it [inference].
- Do not weight findings by who complained loudest; weight by task criticality and participants affected [inference].
- Keep a decision log: what was tested, what changed, what was left, and why [inference].
- Ship when no open finding is a blocker, the last round produced no new severe issue, and the remaining fixes cost more than shipping [inference].
- Run another round when a severe finding is unconfirmed, when the fix changed the flow, or when an entire state (error, empty, permission) was never seen in test [1][inference].
- Stop when additional sessions only repeat known findings; five-user rounds flatten quickly [1].

## Sources

[1] [Why You Only Need to Test with 5 Users](https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: 31% per-user discovery, ~85% at five users, 15 users for all problems, group sizes, three-round iteration, limits of small samples.
[2] [Usability (User) Testing 101](https://www.nngroup.com/articles/usability-testing-101/) — Kate Moran, Nielsen Norman Group — accessed 2026-11-27 — supports: facilitator/task/participant model, realistic tasks, think-aloud, qualitative vs quantitative, task success and time, five participants, moderated vs unmoderated.
[3] [Tree Testing: Evaluate Menu Labels and Categories](https://www.nngroup.com/articles/tree-testing/) — Page Laubheimer, Nielsen Norman Group — accessed 2026-11-27 — supports: hierarchy-only testing, task wording without label giveaway, directness, between-subjects tree comparison, qualitative vs quantitative limits.
[4] [A/B Testing 101](https://www.nngroup.com/articles/ab-testing/) — Tim Neusesser, Nielsen Norman Group — accessed 2026-11-27 — supports: hypothesis, one element per test, primary and guardrail metrics, sample size and 1–2 week duration, low-traffic limits, one-in-seven win rate, deceptive variants.
[5] [Measuring Usability with the System Usability Scale (SUS)](https://measuringu.com/sus/) — Jeff Sauro, MeasuringU — accessed 2026-11-27 — supports: ten-item scoring, average 68, percentile interpretation, not a percentage, not diagnostic, modest correlation with task performance.
[6] [Measuring the User Experience on a Large Scale: User-Centered Metrics for Web Applications](https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/) — Kerry Rodden, Hilary Hutchinson, Xin Fu, Google Research (CHI 2010) — accessed 2026-11-27 — supports: HEART framework, mapping product goals to signals and metrics, large-scale behavioural measurement.
[7] [How to Conduct a Heuristic Evaluation](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/) — Kate Moran and Kelley Gordon, Nielsen Norman Group — accessed 2026-11-27 — supports: 1–2 hour timebox, three to five independent evaluators, narrow scope, independent passes, consolidation, heuristics as hypotheses not user findings.
