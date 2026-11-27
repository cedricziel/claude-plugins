# Forms

This file answers one question: how should a form be built so people can answer it correctly the first time? Read it when designing, reviewing, or auditing any screen that collects input — sign-up, settings, checkout, admin editors. It covers structure, labels, input constraints, validation, and recovery; `feedback-and-status.md` covers what the interface does after a submit (waits, progress, success and failure states), and this file stops where that one starts.

## One question per field, one thing per page

- One control, one value. Split a value into parts only when each part is separately meaningful downstream (day/month/year, card expiry); never split a name by default. In Baymard testing 42% typed their full name into "First name"; a single "Full name" field reduced hesitation to 4% [8].
- Start with one question or one decision per page. Merge pages only when research shows users benefit, such as expert tools where people repeat tasks quickly [4].
- When a page asks one question, make the label or legend the `h1` so screen readers hear the question once, not twice [4].
- When a page must ask several related questions, use a statement as the heading and style each label or legend as a visible sub-question [4].
- Keep one column. Multi-column forms break the vertical scan and make tab order ambiguous [inference].
- Ask for each piece of information once per journey; pre-fill it or offer a previously entered answer as a choice [4].
- Order questions by the user's task, not the data model: ask disqualifying questions first so ineligible users stop early [inference].
- Write down why every question exists before building it. If you cannot say what the answer changes, delete the field [4].
- On a check-answers page, give every row its own change link that opens the page holding that answer. One shared link covering a group of answers sends people hunting, then scrolling, for the field they meant [11].

## Labels, hints, and why placeholders fail

- Give every control a visible `<label>` whose `for` matches the control `id` (explicit association); a nearby paragraph is not a label [5].
- Put labels above the field, in sentence case, without a trailing colon, short enough to scan [1].
- Never use placeholder text as the label. It vanishes on input, usually fails contrast, and is not reliably announced by screen readers [1][7].
- Put format help in hint text outside the field: one short sentence, no full stop, no links (screen readers do not announce that link text is a link) [1].
- Use a placeholder only for a non-essential example; never for a rule the user must follow to succeed [7].
- Floating labels beat placeholder-as-label but still make a filled field look pre-filled and remain unreliable for assistive tech; prefer labels outside the field when space allows [7].
- Hide a label visually only when adjacent context names the control, such as a search box beside a Search button. Form questions are never that obvious [5].
- The label is part of the hit area: clicking it focuses the input or selects the radio or checkbox, which helps users with limited dexterity [5].
- Keep labels and hints visible after submission so users can check their answers and fix errors without re-revealing text [7].

## Required, optional, input type, autocomplete

- Mark optional fields with "(optional)" in the label, or in the legend for radios and checkboxes. Do not mark required fields with asterisks [4].
- If nearly every field is optional, invert the convention: mark the few required ones and explain it once above the form [inference].
- Use `type="text"` with `inputmode="numeric"` or `"decimal"` for numbers. `<input type="number">` lets users change values by scrolling and gives no message for bad input [1].
- Set `autocomplete` on every field with a known purpose (`name`, `postal-code`, `bday-day`, `tel`, `email`). WCAG 1.3.5 requires it for common input purposes [1].
- Set `spellcheck="false"` on emails, reference numbers, codes, and names so browsers do not underline correct data [1].
- Choose the control by answer shape: radios for a short visible set, checkboxes for multiple answers, select only when the list is long and ordered [inference].
- Do not use a range slider when a number can be typed; drag-only input excludes keyboard and motor-impaired users, and needs a non-drag alternative if used at all [4].
- Keep pointer targets at least 24×24 CSS pixels, or leave 24 px of clear spacing around smaller ones [9].

## Constraining input and its costs

- Do not set `maxlength`. Truncation is silent, breaks pasted data, and blocks legitimate formats; normalise and validate the value instead [1].
- Size the field to the answer: postcode-wide for a postcode, phone-wide for a phone number. A full-width box for a four-digit code misleads [1].
- Accept the formats people actually type — spaces in postcodes, dashes in phone numbers — and normalise on submit rather than rejecting the value [6].
- Place prefixes and suffixes outside the input, mark them `aria-hidden`, and repeat the unit in the label. Tolerate users who type the symbol themselves rather than erroring [1].
- Apply input masks only to fixed, unambiguous formats. Masks break paste, IME input, screen readers, and international numbers, and can hide the real value from validation [inference].
- Do not split one number across several fields (phone, card, account). Per-segment labels are usually meaningless when read aloud [inference].
- When the value must be read back in chunks, play it back under the field or on the check-answers page instead of splitting the input. Keep multiple inputs for values that are genuinely ambiguous as one string, such as dates [13].
- Allow "I do not know" or "not sure" where that is a valid answer instead of forcing a guess [4].
- Show remaining characters next to the field when a limit is real, rather than only reporting it after submit [inference].

## Validation timing and message content

- Validate against the submitted value: errors are reported after the submit, tied to what the user actually sent [10].
- After a failed submit, re-check each field when it loses focus (blur). Do not flag a field the user has not finished, and do not re-validate on every keystroke [10].
- The exception is a check that needs the whole value to be useful, such as username availability: run it while typing, debounce it, and announce the result politely rather than interrupting [10].
- Put the message after the label and hint, next to the field, and give the control a red border so the message and field read as one unit [2].
- Connect the message with `aria-describedby` and prefix a visually hidden "Error:" so it is announced with the field [2].
- Write the message as an instruction that repeats the label's wording: "Enter your first name", not "This field is required" [2].
- One message per error state. Do not stack a generic summary and a specific message on the same field [2].
- Keep the wording identical next to the field and in the page summary so the two are recognisably the same problem [2][3].
- Ban jargon and blame: no "form post error", "invalid", "forbidden", "you forgot", "oops", or "sorry" [2].

| Error state  | Message pattern                            |
| ------------ | ------------------------------------------ |
| Empty        | "Enter [thing]"                            |
| Too long     | "[Thing] must be [n] characters or fewer"  |
| Too short    | "[Thing] must be [n] characters or more"   |
| Wrong format | "[Thing] must be a number, like 30"        |
| Out of range | "[Thing] must be between [low] and [high]" |

Patterns from the GOV.UK error message guidance [2].

## Error summary and preserving answers

- On any submit failure, show an error summary at the top of the main content: below the back link and breadcrumbs, above the `h1` [3].
- Head it "There is a problem" and list one link per error. Each link jumps to the offending field; for multi-field answers, link to the first field with an error [3].
- Move keyboard focus to the summary on load, and prefix the page `<title>` with "Error:" so screen readers hear it immediately [3].
- Show the summary even when there is only one error; a lone inline message is easy to miss on a long page [3].
- Never clear fields on failure. Keep passing and failing answers so users can see what went wrong and edit rather than retype [2].
- Preserve scroll position and any expanded sections; a submit that resets the page to a blank form reads as data loss [inference].
- Do not use field errors for problems the user cannot fix — ineligibility, no capacity, service down. Send them to a page that explains the situation [2].

## Groups, progress, and cutting fields

- Wrap related controls in `<fieldset>` with one `<legend>` holding the question; each control keeps its own label ("Day", "Month", "Year") [4].
- A multi-part answer gets one legend, one hint showing the format, and one error message about the group rather than three competing messages [4].
- Add a progress indicator only after simplifying order, type, and number of questions has failed; then show "Question 3 of 9" beside the heading and update it [4].
- State a total only when it is reliable; branching forms should say "about 7 questions", and never ship a clickable tracker that lists all steps at once [4].
- Persist a draft for long forms, restore it on return, and tell the user it was restored. Interruptions are normal, not edge cases [inference].
- Keep the browser back button working and returning the previous page in its last state; users distrust in-page back links alone [4].
- Cut fields before decorating them. Remove anything derivable, collectable later, or never used. Baymard's 2024 benchmark: average checkout 11.3 fields against roughly 8 needed, and 17% of users have abandoned over checkout complexity [8].
- Checkout specifics: hide Address line 2 and coupon code behind links (30% of testers stopped at Address line 2), default billing to shipping, offer guest checkout, and delay account creation to the confirmation step (84% of sites do not) [8].
- Keep payment fields in the expected order (number, expiry, security code), label the pay button with the amount ("Pay £24.00"), and place security or returns reassurance next to that button rather than in the footer [inference].
- Align the primary button with the left edge of the fields, put the back link above the form, and move tangentially related links ("Forgot your password?") above the form too, so they never sit between the last field and the button in the tab order [12].
- Count pause time as part of the form's cost: the re-reading, the check-answers step, and the guessing about what happens after submit. Put the facts people hesitate over — delivery time, returns window, where a submitted record goes — before the primary button [14].

## Sources

[1] [Text input](https://design-system.service.gov.uk/components/text-input/) — GOV.UK Design System team — accessed 2026-11-27 — supports: label placement and case, placeholder avoidance, hint text, `inputmode`, avoiding `type="number"`, autocomplete and WCAG 1.3.5, spellcheck, paste, `maxlength`, field sizing, prefixes and suffixes.

[2] [Error message](https://design-system.service.gov.uk/components/error-message/) — GOV.UK Design System team — accessed 2026-11-27 — supports: inline placement and red border, preserving answers, hidden "Error:" prefix, message wording rules and templates, consistency with the summary, not using field errors for service problems.

[3] [Error summary](https://design-system.service.gov.uk/components/error-summary/) — GOV.UK Design System team — accessed 2026-11-27 — supports: summary placement, "There is a problem" heading, per-field links and first-field linking, focus move, "Error:" in the page title, showing it for a single error.

[4] [Question pages](https://design-system.service.gov.uk/patterns/question-pages/) — GOV.UK Design System team — accessed 2026-11-27 — supports: one question per page, label or legend as heading, (optional) marking and no asterisks, asking once, back link behaviour, progress indicator limits, fieldset and legend grouping, date input, range sliders, "I do not know".

[5] [Labeling Controls](https://www.w3.org/WAI/tutorials/forms/labels/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: explicit label/for association, clickable label area, when a visually hidden label is acceptable, labels above fields, visible labels being preferred.

[6] [Validating Input](https://www.w3.org/WAI/tutorials/forms/validation/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: forgiving input formats and normalisation, confirmation and undo for consequential actions.

[7] [Placeholders in Form Fields Are Harmful](https://www.nngroup.com/articles/form-design-placeholders/) — Katie Sherwin, Nielsen Norman Group — accessed 2026-11-27 — supports: the seven failure modes of placeholders, floating-label limits, labels and hints outside the field.

[8] [Checkout Optimization: 5 Ways to Minimize Form Fields in Checkout](https://baymard.com/blog/checkout-flow-average-form-fields) — Edward Scott, Baymard Institute — accessed 2026-11-27 — supports: 5.1 steps and 11.3 fields on average, 17% abandonment over complexity, ~8 fields needed, name-field findings, Address line 2 and coupon hiding, billing defaults, delayed account creation.

[9] [Understanding SC 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 24×24 CSS pixel minimum target size and the 24 px spacing exception.

[10] [User Notification](https://www.w3.org/WAI/tutorials/forms/notifications/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: validation during typing versus on focus change, `aria-live` politeness, focus to the first field in error.

[11] [End with one thing per page](https://adamsilver.io/blog/end-with-one-thing-per-page) — Adam Silver — accessed 2026-11-27 — supports: one change link per row on check-answers pages, why shared change links fail, one thing per page as the default end state.

[12] [Where to put buttons on forms](https://adamsilver.io/blog/where-to-put-buttons-on-forms) — Adam Silver — accessed 2026-11-27 — supports: primary button aligned to the input edge, back link above the form, tangentially related links above the form, button choices and their cost.

[13] [Form design: multiple inputs versus one input](https://adamsilver.io/blog/form-design-multiple-inputs-versus-one-input) — Adam Silver — accessed 2026-11-27 — supports: paste and effort costs of split inputs, playing answers back in chunks, dates as the legitimate multi-input case, input masks.

[14] [The second law of form design](https://adamsilver.io/blog/the-second-law-of-form-design) — Adam Silver — accessed 2026-11-27 — supports: completion time as question time plus pause time, hesitation over delivery and returns facts, optional fields that force a decision.
