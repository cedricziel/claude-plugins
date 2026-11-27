# Content and Microcopy

Answers one question: does this wording tell the reader what they need, in the order they need it, in words they already use? Read it when reviewing headings, links, buttons, labels, errors, empty states, tone, or formatting conventions. Layout, scanning, and spacing belong to `layout-and-visual-hierarchy.md`.

## Plain language and reading level

- Target an 8th-grade reading level for consumer copy and 10th–12th for expert and B2B audiences; above 12th costs even educated readers [1].
- Keep sentences to 15–20 words and one idea per paragraph; a one- or two-sentence paragraph is fine [1].
- Write in the active voice; use the passive only when it front-loads the term that matters [1].
- Choose the word your reader would search for, not the word your organisation prefers [1].
- Delete redundancies ("therapeutic treatment"), idioms, pointless modifiers ("at this moment in time"), and empty generalities [1].
- Keep specialist vocabulary when the audience shares it, and explain it at first use when they do not [1][5].
- Lead with the conclusion; the inverted pyramid lets a reader stop early without losing the point [1].
- Score drafts with Flesch-Kincaid or Fry and rewrite anything above target instead of arguing about it [1].
- Treat the score as a smoke alarm, not a pass mark: keep the word the audience needs even when it lifts the grade, and never chop a sentence into fragments to satisfy a formula [8].
- "No one has ever complained that a text was too easy to understand." [1]

## Front-load the first words

- Assume two words get read: put the distinguishing term first in every heading, link, bullet, and page title [2].
- Order page titles page-first and organisation second; add the step for multi-step flows ("Buy Your Bear (Step 1 of 3)") [2].
- Do not open every bullet with the same verb or every link with "Read more"; the shared prefix is skipped. [2][inference]
- Make headings describe the section's content, not its category ("What you'll pay" beats "Fees information") [1].
- Keep headings short enough to read in one fixation; if a heading needs a comma and a clause, split it. [inference]

## Links and action labels

- Link text must describe the destination; "click here", "read more", and "learn more" fail as standalone labels [2].
- Add format and size when linking a file: "Proposal documents (RTF, 20MB)" [2].
- Never point two different destinations at the same link text on one page. [inference]
- Label buttons with the outcome in the user's words ("Create account", "Send invoice"), not "Submit" or "OK". [inference]
- Lead the label with the constraint when it changes the decision: "Out of stock — notify me" carries the fact and the next action in one line [3].
- Keep the label consistent with the result: a "Publish" button produces "Published", not "Saved". [inference]
- Write "select", not "click"; not every user clicks [5].
- Name the object in destructive actions ("Delete 3 files") so the label cannot be confirmed by reflex. [inference]

## Capitalisation and emphasis

- Use sentence case everywhere, including page titles, service names, buttons, and table headers; proper nouns are the exception [5].
- Never set phrases or sentences in block capitals; they slow reading and remove word shape [5].
- Use bold only for interface elements inside instructions ("Select **Start**"), never for emphasis [5].
- Drop italics; use single quotation marks for document, scheme, or product names [5].
- Leave buttons, links, and labels without terminal punctuation. [inference]
- Lower-case generic titles (government, minister, department) and capitalise only full proper names [5].

## Errors, empty states, helper text

- Every error names what happened, why it matters, and what to do next, placed next to the field it concerns. [4] Full error placement and recovery patterns live in `errors-and-empty-states.md`.
- Replace generic text ("An error occurred", "Invalid input") with the specific condition [4].
- Avoid blame words: invalid, illegal, incorrect, and "you forgot" [4].
- Preserve what the user typed and let them edit it instead of retyping [4].
- Do not fire an error while the user is still exploring; validate on submit or after a completed entry [4].
- Show codes and identifiers only for diagnostics, never as the message [4].
- Pair the error colour with an icon and text; colour alone fails SC 1.4.1 [4].
- State requirements before input — format, length, units, allowed values — rather than after failure [2].
- Empty states: say what will appear here, why it is empty, and the single action that fills it. [inference]
- If a feature needs more than one short sentence of instruction, change the design instead of adding microcopy; instructions are a symptom, not a fix [7].
- No-results states: echo the query back, say how many matches there are, and offer a spelling check plus two or three concrete alternatives. Users will not reformulate the query on their own [9].

| Slot           | Fails           | Passes                                       |
| -------------- | --------------- | -------------------------------------------- |
| What happened  | "Invalid input" | "That email address has no @ symbol"         |
| Why it matters | (missing)       | "We send your receipt to this address"       |
| What to do     | (missing)       | "Add @ and the domain, then select Continue" |

## Voice, tone, and personality

- Hold one voice; change tone with the reader's state — a failed payment gets no jokes [3].
- Rank the goals clarity, then concision, then character; character never buys back lost clarity [3].
- Allow humour only at low stakes and only when it does not delay the instruction [3].
- Cut the joke before cutting the fact; forced humour reads worse than none [3].
- Address the reader as "you" and avoid gendered pronouns [5].
- Pick one term per concept and reuse it; synonyms read as different features [6].
- Keep the same label for the same object across button, heading, confirmation, and email. [inference]

## Numbers, dates, units, jargon

- Dates: "2 June 2026" — no ordinal, no comma before the year; ranges use "to", not a dash [5].
- Money: "£75", with decimals only when pence are included ("£75.50"); write pence out in prose [5].
- Large sums: "£138 million"; never "£0.2 million" outside a sequence that already uses billions [5].
- Measurements: numeral plus unit with no space in abbreviations ("3,500kg"); spell out multi-word units at first mention [5].
- Temperature in Celsius with the degree symbol ("37°C"); ratios close up ("5:12") [5].
- Expand abbreviations at first use on the page and drop full stops from initialisms ("BBC", not "B.B.C.") [5].
- For international readers, use ISO currency codes ("25 USD", not "$25") and metric units spelled out [6].
- Write "no data" or "not applicable" in empty table cells, never "N/A" [5].

## Localisation and cutting

- Remove idioms, slang, clichés, and local references; they either mistranslate or mean nothing [6].
- Repeat the subject and verb instead of eliding ("The Standard plan offers X, but the Essentials plan does not") [6].
- Avoid ambiguous words (once, since, right) and -ing forms that translators cannot classify [6].
- Do not concatenate fragments around variables in code; ship the whole sentence so translators can reorder it. [inference]
- Budget roughly 30% extra width for translated strings and test the longest label, not the English one. [inference]
- Cut any sentence that restates its heading; compare paragraph one against H1 and delete the overlap [1].
- Read the copy aloud; rewrite every sentence you have to restart. [inference]
- Test comprehension with tasks, not opinions: five participants per round restate the instruction and perform it, and a Cloze test scores a passage before and after a rewrite. [1][inference]

## Sources

[1] [Legibility, Readability, and Comprehension: Making Users Read Your Words](https://www.nngroup.com/articles/legibility-readability-comprehension/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: reading-level targets, sentence and paragraph length, active voice, jargon, inverted pyramid, comprehension testing.
[2] [Writing for Web Accessibility](https://www.w3.org/WAI/tips/writing/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: page titles, meaningful link text, file format and size, instructions before input.
[3] [The 3 C's of Informational Microcopy](https://www.nngroup.com/articles/3-cs-microcopy/) — Taylor Dykes, Nielsen Norman Group — accessed 2026-11-27 — supports: clarity/concision/character order, button labels that lead with the constraint, humour limits.
[4] [Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/) — Tim Neusesser and Evan Sunwall, Nielsen Norman Group — accessed 2026-11-27 — supports: error anatomy, proximity, blame-free wording, preserving input, colour plus icon.
[5] [A to Z style guide](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide) — Government Digital Service, GOV.UK content and publishing guidance — accessed 2026-11-27 — supports: sentence case, bold and italics, dates, money, measurements, abbreviations, "no data", "select".
[6] [Writing for Translation](https://styleguide.mailchimp.com/writing-for-translation/) — Mailchimp Content Style Guide — accessed 2026-11-27 — supports: idioms, repeated subjects and verbs, ambiguous words, ISO currency codes, metric units, one term per concept.
[7] [Getting Practical With Microcopy](https://www.smashingmagazine.com/2016/07/getting-practical-with-microcopy/) — Rade Brujić, Smashing Magazine — accessed 2026-11-27 — supports: one-sentence limits on instructional microcopy, treating instructions as a symptom of a design problem, contextual words in labels and buttons.
[8] [Readability Algorithms Should Be Tools, Not Targets](https://www.smashingmagazine.com/2020/05/readability-algorithms-tools-targets/) — Frederick O'Brien, Smashing Magazine — accessed 2026-11-27 — supports: Goodhart's law applied to readability scores, sentences butchered to satisfy formulas, audience-appropriate vocabulary.
[9] [Better Search UX Through Microcopy](https://www.smashingmagazine.com/2019/06/better-search-ux-microcopy/) — Andrew Millen, Smashing Magazine — accessed 2026-11-27 — supports: echoing the query and result count, no-results copy and paths forward, users not reformulating a query.
