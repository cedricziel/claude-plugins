# Errors and Empty States

What to say and show when the system cannot do what the user asked: validation, failure, no data, no permission, no connection. Read this when reviewing message copy, error placement, or an empty container. The control-level decisions that cause these states — target size, disclosure, dialogs, focus — live in `interaction-patterns.md`.

## Slips, mistakes, and the right fix

- Classify before fixing: a slip is the right intention with the wrong action (typo, wrong row); a mistake is a wrong intention built on a wrong mental model [1].
- Fix slips with constraints — forbid impossible input (a return date before departure), suggest while typing, format as the user types [1].
- Fix mistakes with explanation and a better model: state what the system does, show the consequence before commit, let users compare options [1].
- Treat the interface as the cause: if a control invites the wrong action, redesign the control instead of warning harder [1].
- Answer neither kind with training or longer documentation; the fix belongs in the interface [1].
- Spend prevention effort on the highest-cost errors first, not the most frequent annoyances [7].

## Prevention before messages

- Do not disable the submit button as the validation strategy: a disabled control cannot say which field is wrong, while the guidance is to explain the problem and the fix [4][inference].
- Let the user attempt the action and report errors on submit; validate while typing only for error-prone formats such as passwords and dates [2].
- Never fire an error on blur of an empty field the user merely tabbed through; premature errors are hostile [2].
- Accept forgiving input — spaces, punctuation, several date and phone formats — normalise server-side rather than rejecting [1].
- Warn before a likely mistake (missing attachment, unsaved changes) rather than reporting it afterwards [2].
- Constrain only where the rule is absolute; leave open-ended input open-ended [1].

## Error message anatomy and wording

- Cover four things: what happened, why, what to do next, and where — in the user's words, beside the element that failed [2].
- State the problem in terms of the user's input ("This date is in the past"), not the system's internals ("constraint violation") [2].
- Give the next step as a concrete instruction and, where possible, a control that performs it [2][3].
- Reuse the field label's words so the message still makes sense out of context [4].
- Ban these: "invalid", "illegal", "forbidden", "prohibited", "you forgot", "please", "sorry", "oops", "an error occurred", "this field is required" [4].
- Show an error code only as secondary diagnostic text, never as the message [2].
- Drop exclamation marks, humour, and blame; describe the requirement, not the user's failure [2][6].
- Write a distinct message per case — empty, too long, too short, wrong format, out of range [4].
- Use an instruction for an empty field ("Enter your name") and a description for a violated rule ("Name must be 35 characters or fewer") [4].

```
Bad:  Error: Invalid input (code 422). Please try again.
Good: Enter a start date after 31 August 2017.
```

## Inline errors, summaries, and focus

- Show both a summary and a per-field message, even for a single error [3].
- Move focus to the error summary on submit, so keyboard and screen-reader users land on the list [3].
- Title the summary "There is a problem"; list one link per failing field, each linking to that field [3].
- Word the summary entry and the inline message identically [3][4].
- Place the summary at the top of the main content, below the back link and above the `h1` [3].
- Prefix the page title with "Error: " so it is announced on load [3].
- Link a multi-field question to its first failing field, and an unknown field to the first field [3].
- Never rely on colour alone: pair red with an icon, bold text, and a field border, and connect the message with `aria-describedby` [2][4].
- Do not clear or reset fields when re-rendering the error state; keep both passing and failing values [4].
- Keep the layout stable when a message appears so the rest of the form does not jump [inference].

## Preserving work and recovery paths

- Re-render the submitted values with the error; losing typed input on failure is the worst recoverable defect [4].
- Keep the user on the same step and scroll position after a failed submit [inference].
- Offer the smallest correction: pre-fill the nearest valid value or provide a one-click fix instead of demanding re-entry [2].
- Always offer an exit that keeps partial work — save draft, save and finish later [2].
- For a failure the user cannot fix (eligibility, permission, capacity), leave the form pattern and use a dedicated page that explains the situation and what to do next [4].
- Name the support route in the page: channel, hours, and any reference number, not only in a follow-up email [inference].
- In a total outage, say plainly that the failure is the service's, give a retry expectation, and keep any novelty small and optional [2].

## Empty states: four distinct cases

- Name the state before designing it: first use (nothing created), no results (query matched nothing), cleared (user finished or deleted everything), error (the fetch failed) [5][6].
- First use: say what the container holds, why it is empty, one primary action to create the first item, and an example or demo data [5].
- No results: show the query and filters that produced zero, keep the search box populated, offer similar queries, spelling fixes, and a browse path [6].
- Cleared: confirm the completion ("All 12 items reviewed") and offer the next action; do not reuse first-use copy [5][inference].
- Error: say loading failed, keep a retry control, and never render the no-data message for a failed request [5].
- Show a progress indicator while a request is in flight; never render "No records" before the result arrives [5].
- Put a system-status sentence in the content area; an illustration without a sentence leaves the state ambiguous [5].
- Make the empty state's primary action a real control (Create, Add source), not a link to documentation [5].
- Keep illustrations subordinate to one line of copy and one action [5][inference].
- Distinguish zero-because-filtered from zero-because-empty and offer "Clear filters" in the first case [6].

## No-results, permission, and partial failure

- Make "no results" visually loud: users expect results in the body and skip small, low-contrast notices placed near the header [6].
- Never joke on a no-results or error page; the user has just failed at something [6].
- For a permission-restricted state, name the role or plan required and who can grant it; do not render an empty list [4].
- Do not disguise ineligibility or missing permission as a validation error; use a dedicated explanatory page [4].
- For bulk operations, report per item — succeeded, failed with reason, skipped — never a single "some items failed" [inference].
- Retry only the failed subset and keep succeeded items out of the retry [inference].
- Show partial results as partial ("38 of 40 rows loaded") and keep the page usable rather than blanking it [inference].

## 404, offline, timeout, and measurement

- Give 404, service-unavailable, and timeout their own page patterns; do not reuse a form validation message for them [4].
- 404: say the page is not found, keep the attempted URL visible, offer search and the two or three most likely destinations [6][inference].
- Offline: state that the connection is down, name what still works, and retry automatically when it returns [inference].
- Timeout: give the elapsed time, a retry control, and preserve the in-flight input [inference].
- Log every error state with a stable id, the route, the user's role, the failing field or operation, and the outcome (retry or abandon) [4].
- Track how often each error appears and how often users recover; use it to rewrite the copy and remove the error [4].
- Alert on error-state volume, not only on server error rates; a spike in no-results is a content or search defect [inference].

## Sources

[1] [Preventing User Errors: Avoiding Unconscious Slips](https://www.nngroup.com/articles/slips/) — Page Laubheimer, Nielsen Norman Group — accessed 2026-11-27 — supports: slips versus mistakes, constraints, suggestions, forgiving formatting, designer blame.
[2] [Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/) — Tim Neusesser and Evan Sunwall, Nielsen Norman Group — accessed 2026-11-27 — supports: proximity, redundant indicators, premature errors, tone, preserving input, one-click fixes.
[3] [Error summary](https://design-system.service.gov.uk/components/error-summary/) — GOV.UK Design System — accessed 2026-11-27 — supports: summary plus inline, focus move, heading, field links, placement, page title prefix.
[4] [Error message](https://design-system.service.gov.uk/components/error-message/) — GOV.UK Design System — accessed 2026-11-27 — supports: wording bans, label matching, specificity, keeping entered values, dedicated pages for permission and service problems, tracking errors.
[5] [Designing Empty States in Complex Applications: 3 Guidelines](https://www.nngroup.com/articles/empty-state-interface-design/) — Kate Kaplan, Nielsen Norman Group — accessed 2026-11-27 — supports: system status, misleading empty messages, learning cues, direct pathways, demo data.
[6] [3 Guidelines for Search Engine “No Results” Pages](https://www.nngroup.com/articles/search-no-results-serp/) — Kathryn Whitenton, Nielsen Norman Group — accessed 2026-11-27 — supports: salience of the no-results message, query retention, alternative queries, no humour.
[7] [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: error prevention priority by cost, user control, plain-language recovery.
