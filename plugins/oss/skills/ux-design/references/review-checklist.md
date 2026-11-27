# Review Checklist

This file is the ordered review pass: nine areas, each a set of yes/no questions with the failure each one catches. Run it on a design file, a screenshot set, or a built screen without opening a browser. It assumes the constraints in `accessibility.md` and the task framing in `SKILL.md`; it does not replace a usability test (`research-and-validation.md`).

## How To Run This Pass

- Review one artifact at a time: one screen, or one flow of up to six screens [inference].
- Timebox to 20–30 minutes per screen and 60 minutes per flow, then report what remains unreviewed [inference].
- Answer in order. Area 1 failures make areas 3–9 irrelevant, and area 5 failures hide behind visual polish [inference].
- Write one finding per line as you go; batched findings lose the element and the evidence [inference].
- Mark items the artifact cannot show as "unverified", never "pass"; focus and loading behaviour are the usual false passes [inference].
- Cite the heuristic or criterion behind each finding; a finding without a principle is a preference [1].

## The Ordered Pass

### 1. Task Fit

- **Can the screen be stated as one task in the user's words?** Catches: feature-named screens that answer an internal roadmap [1].
- **Is the primary action unique and findable within three seconds?** Catches: three co-equal buttons, or the primary action below the fold [inference].
- **Does the flow follow the order the work happens (collect, check, commit)?** Catches: payment before address, account creation before price [1].
- **Is prevention proportional to the cost of failure?** Catches: a confirmation for a reversible rename and none for a permanent delete [1].
- **Would a first-time user with no memory of the previous screen succeed?** Catches: context carried only in a prior step's heading [1].
- **Is anything here serving the business at the user's expense?** Catches: preselected extras and obstructed cancellation; see anti-patterns [2].

### 2. Information Architecture And Navigation

- **Are there 5–7 top-level destinations, labelled with user nouns?** Catches: fourteen menu items and internal product names [inference].
- **Is current location visible on every screen (selected nav, breadcrumb, or title)?** Catches: a settings subpage that looks identical to its parent [inference].
- **Can every top-level section be reached in two actions or fewer?** Catches: navigation hidden behind a hamburger on desktop [inference].
- **Is there a search path when browsing would need more than seven categories?** Catches: deep catalogues with browse-only navigation [inference].
- **Do back, cancel, and close lead somewhere predictable and distinct?** Catches: three labels for one exit, or "Cancel" that submits [1].
- **Could a user pick the right label without opening it?** Catches: sibling categories distinguished only by an internal distinction [1].

### 3. Hierarchy And Scanning

- **Is there one `h1` and a visible two- or three-level hierarchy?** Catches: flat pages where every block has equal weight [7].
- **Does the page still make sense read as headings only?** Catches: headings used as styling for non-structural text [7].
- **Is the most important value or state the strongest element (size, weight, contrast)?** Catches: decoration outranking the number the user came for [inference].
- **Are secondary actions visually quieter than the primary?** Catches: outline buttons competing with the primary action [inference].
- **Does the layout hold at 320 px wide without hiding content?** Catches: fixed-width cards and side-by-side label/field pairs [7].
- **Is grouping done by proximity and spacing rather than boxes and rules?** Catches: every field in its own card, which flattens hierarchy [1].

### 4. Copy

- **Do buttons read verb + object ("Delete project"), not "OK" or "Submit"?** Catches: actions that need the surrounding paragraph to interpret [inference].
- **Do headings name the outcome, not the feature?** Catches: "Notifications" where the task is "Choose what we email you" [inference].
- **Is jargon absent or defined at first use?** Catches: internal terms leaking into labels and errors [1].
- **Are errors free of codes, blame, and exclamation marks?** Catches: "Error 422: invalid input!" and "You failed to…" [1][4].
- **Is link text meaningful out of context?** Catches: a screen of "click here" and "learn more" [inference].
- **Is the same concept named the same way on every screen?** Catches: "workspace", "project", and "site" for one thing [1].

### 5. Forms And Errors

- **Does every field have a visible label above it, not a placeholder?** Catches: labels that vanish on input and fail at autofill [4].
- **Are required fields marked in text rather than colour or an asterisk alone?** Catches: red-only marking that disappears for colour-blind users [3].
- **Is help text adjacent to the field it explains?** Catches: format instructions collected in a paragraph above the form [inference].
- **On failure, is there a summary plus an inline message, with input preserved?** Catches: a cleared form and a single banner at the top [4].
- **Does each error state the fix ("Use DD/MM/YYYY"), not just the fault?** Catches: "Invalid date" with no accepted format [4].
- **Is the form one column, one question per field, with nothing the flow does not need?** Catches: side-by-side names and a "company" field nobody uses [inference].

### 6. States

- **Is there a loading state for under 1 s, 1–10 s, and over 10 s?** Catches: a spinner on a 30 s import with no progress or exit [1][inference].
- **Does the first-run empty state explain the area and offer its action?** Catches: "No items" on a screen the user has never populated [1].
- **Is no-results distinct from first-run empty, and does it offer a way out?** Catches: a failed search that looks like an empty account [inference].
- **Does every data region have a recoverable error state?** Catches: one failed request that blanks the whole page [1].
- **Is partial success shown as partial, with what is missing named?** Catches: an import that silently dropped 12 of 400 rows [1].
- **Does success confirm what happened and name the next step?** Catches: a save with no visible change and no destination [1].
- **Is permission-denied designed, not a blank screen or a raw 403?** Catches: an admin link that renders an empty table for non-admins [inference].

### 7. Interaction And Control

- **Is every clickable element obviously clickable without hover?** Catches: text styled as body copy that turns out to be a link [1].
- **Are targets at least 24×24 px, and 44×44 on touch surfaces?** Catches: 16 px icon buttons in a toolbar row [5].
- **Does every overlay close with Escape and return focus to its trigger?** Catches: a modal that traps focus or drops it to the page body [inference].
- **Is every destructive action undoable, confirmed, or typed-confirmed in proportion to cost?** Catches: instant permanent delete behind a single click [1].
- **Are defaults safe (no pre-checked paid extras, no preselected marketing consent)?** Catches: silent opt-in that inflates conversion [2].
- **Can the user return to their place after a detour (filters, pagination, scroll)?** Catches: filter state reset by opening a detail page [inference].

### 8. Accessibility

- **Is body text at 4.5:1, and large text or UI edges at 3:1?** Catches: grey-on-white captions and 1 px light borders [3][8].
- **Can every control be reached and operated by keyboard, in a logical order?** Catches: div-based buttons, positive `tabindex`, focus traps [9].
- **Is focus visible on every focusable element, including inside menus and dialogs?** Catches: `outline: none` with no replacement [6].
- **Does 200% and 400% zoom keep content and actions usable?** Catches: clipped headings and horizontal page scroll [7].
- **Does every control have a visible label and an accessible name?** Catches: icon-only buttons announced as "button" [7].
- **Are errors and status changes conveyed in text, not colour alone?** Catches: a red border as the only failure signal [3][4].
- **Are captions, transcripts, and alt text present where media or images carry meaning?** Catches: autoplaying video with speech and no captions [7].

### 9. Trust And Disclosure

- **Are total price, fees, and renewal terms visible before commitment?** Catches: costs revealed at the last step or only in the terms [2].
- **Is it clear who is asking for data, and why, at the point of asking?** Catches: an unexplained field for a phone number [inference].
- **Is consent opt-in, granular, and as easy to refuse as to accept?** Catches: one "Accept all" and a buried refusal [2].
- **Are irreversible consequences stated before the action, not after?** Catches: "This cannot be undone" shown in the toast [1].
- **Can the user leave or cancel without obstruction?** Catches: cancellation behind retention screens and hidden confirmations [2].
- **Is any urgency or scarcity claim true and verifiable?** Catches: a countdown that resets on reload, or "3 left" that never changes [2].
- **Is system state honest (no fake progress, stock counters, or activity)?** Catches: a progress bar that jumps to 90% and waits [1].

## Severity, And When To Stop

| Severity | Test                                                                                             | Typical examples                                                       |
| -------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| Blocker  | Task cannot be completed, or money, data, or safety is at risk; a legal or accessibility failure | No keyboard path to submit; error state loses input; total cost hidden |
| Major    | Task completes only with a workaround, or a common path produces frequent errors                 | Primary action below the fold; ambiguous labels; no empty state        |
| Minor    | Friction, inconsistency, or polish that does not change the outcome                              | Two names for one concept; inconsistent spacing                        |

- Stop the pass when a blocker invalidates the flow; report it and skip the remaining areas rather than polishing a dead end [inference].
- Stop a screen when the next pass yields no new issue type, not when you run out of things to say [inference].
- Do not re-review a fix inside the same pass; verify it in a fresh pass so the change, not the memory of it, is judged [inference].
- Leave at most five blockers in a report; thirty blockers is triage failure, not thoroughness [inference].

## Issues Table

```markdown
| #   | Issue                                  | Why it matters                                        | Severity | Source |
| --- | -------------------------------------- | ----------------------------------------------------- | -------- | ------ |
| 1   | Delete has no undo and no confirmation | One misclick destroys a project with no recovery path | Blocker  | [1]    |
```

Fill "Why it matters" with the user consequence, not the principle. Fill "Source" with the number this file already cites, for example `[5]` for target size or `[1]` for user control. One row per finding, ordered by severity, not by screen position [inference].

## Anti-Patterns To Name

- **False urgency** — countdowns, "only 2 left", expiring discounts that are neither true nor verifiable. Principle: truthful claims and enough time to decide [2].
- **Confirmation-shaming** — a decline labelled "No thanks, I don't like saving money". Principle: symmetric, neutral wording for accept and decline [2].
- **Hidden costs** — fees, delivery, or renewal terms disclosed only at the final step. Principle: total cost before commitment [2].
- **Roach motel** — easy to enter, obstructed to leave; cancellation behind retention screens. Principle: exit as easy as entry, user control and freedom [1][2].
- **Preselection and sneaking** — pre-checked extras, opt-in consent, items added to the basket. Principle: no action on the user's behalf without an explicit choice [2].
- **Nagging** — repeating a declined request until the user gives up. Principle: a refusal is recorded and respected [2].
- Name the pattern, the element, and the harm. Do not give legal advice; several of these are unlawful under consumer and data-protection law, and that determination belongs to counsel [2].

## Sources

[1] [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: visibility of status, user control and freedom, error prevention, recognition over recall, consistency, plain-language error recovery.
[2] [Deceptive Patterns in UX: How to Recognize and Avoid Them](https://www.nngroup.com/articles/deceptive-patterns/) — Maria Rosala, Nielsen Norman Group — accessed 2026-11-27 — supports: obstruction, nagging, confirmshaming, preselection, false scarcity, symmetry of choice, legal exposure without legal advice.
[3] [Understanding SC 1.4.3: Contrast (Minimum) (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 4.5:1 body text and 3:1 large text checks.
[4] [Understanding SC 3.3.1: Error Identification (Level A)](https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: text error identification, error summary and inline messages, suggestion wording.
[5] [Understanding SC 2.5.8: Target Size (Minimum) (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 24×24 CSS px minimum and spacing exceptions.
[6] [Understanding SC 2.4.7: Focus Visible (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: visible focus, no removal of indicators, keyboard operability.
[7] [Easy Checks – A First Review of Web Accessibility](https://www.w3.org/WAI/test-evaluate/easy-checks/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: heading structure, zoom, form labels, captions and alt checks, and the warning that these checks are not exhaustive.
[8] [Understanding SC 1.4.11: Non-text Contrast (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 3:1 for control boundaries, states, and meaningful graphics.
[9] [Developing a Keyboard Interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) — W3C ARIA Authoring Practices Guide — accessed 2026-11-27 — supports: keyboard operability of all interactive elements, DOM-order tab sequence, `tabindex` guidance.
