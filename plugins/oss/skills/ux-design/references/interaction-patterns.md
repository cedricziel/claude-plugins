# Interaction Patterns

How a control should look, sit, and behave — target size, choice count, disclosure, defaults, dialogs, drag, and focus. Read this when reviewing a specific interaction ("is this button too small", "should this be a modal", "is this flow too long"). Wording of failure messages and the design of empty or no-result screens live in `errors-and-empty-states.md`.

## Make the actionable thing look actionable

- Give every clickable element a visible signifier — fill, border, shadow, underline, or icon plus label — present before any hover [2].
- Never style static text with the link colour, and never give a heading a button's background; a false target is a defect, not a style [2].
- Make buttons resemble physical buttons: rectangular, consistent, distinguishable from headings and cards. Avoid ghost buttons (text inside a thin outline) for primary actions [2].
- Pair every icon with a text label; the bare icon is a weaker signifier and a smaller target [2][3].
- Link all elements that belong to the same destination (thumbnail, title, image); it also enlarges the effective target [2].
- Keep one treatment per meaning across the product; the same visual style must not mean "link" here and "label" there [2].
- Do not strip depth to look modern: flat redesigns remove the strongest clickability cue and produce click uncertainty. Keep a border, a shadow, or a filled surface [2].
- Never let hover be the only evidence of interactivity — users should not scrub the page with the pointer to discover what is clickable [2].
- On touch there is no hover: trigger the same state change on tap-down or the first tap, and keep the cue permanently visible [inference].

## Target size, spacing, and Fitts's law

- Size pointer targets at 24×24 CSS px minimum, or space undersized targets so a 24 px circle centred on each touches no other target or circle [4].
- Treat 24×24 as the accessibility floor, not the design target: the stricter tier (2.5.5) uses 44×44 CSS px, and the touch research behind both favours larger sizes [4].
- Set touch targets at 44×44 CSS px or more; raise primary one-handed mobile actions to 48×48 where the grid allows [4][inference].
- Enlarge the visible target rather than only its invisible padding: users who cannot see the padded area still slow down or miss, so padding alone does not buy the speed [3].
- Space adjacent targets apart; crowding small targets together produces overshoot onto the wrong control [3].
- Put the next action where the pointer or thumb already is — Submit next to the last field, not in a page header [3].
- Order linear menus by frequency; the last item is the most expensive to reach [3].
- Place contextual menus next to their trigger, not in a distant bottom sheet [3].
- Use screen edges for frequent chrome in mouse-driven UIs (they are effectively infinite targets), but not as a rationale on touch, where edge targets are slower [3].

## Choice cost and recognition

- Count the decisions per screen: decision time grows with the number and complexity of options. Split a screen that asks for more than one decision [6].
- Highlight a recommended option instead of presenting choices as equals, and do not simplify until the options stop describing real things [6].
- Show the information needed for the task in place — label, unit, example — instead of relying on memory from an earlier screen [1].
- Surface state and history: current value, last used, recently viewed, previous selection. A user should never reconstruct a value from two screens back [1].
- Keep the frequent path short and the expert path visible; hiding the shortcut entirely removes the efficiency gain [1].
- Prefer a list of known values (recent projects, saved addresses) over a blank text field wherever the value already exists in the system [inference].

## Progressive disclosure

- Show only the options most tasks need on the first screen; defer specialised settings behind a labelled control [7].
- Disclose up front anything users need frequently — a second level that most users must open is a failed split [7].
- Label the disclosure control by what it reveals ("Shipping options", "Advanced filters") so the next level has information scent [7].
- Stay at two levels; three or more levels lose users moving between them [7].
- Never hide the primary action, the total cost, a destructive consequence, the current validation state, or anything that changes what the user is agreeing to [7][inference].
- Do not use disclosure to hide the price of an action; that is deception, not simplification [inference].
- Accept the extra click only when the hidden content is genuinely rare; otherwise the click cost exceeds the clutter saved [7].
- Keep interdependent options (dates, prices, availability) on one screen so users can compare without navigating [7].

| Disclose behind a click          | Keep visible at all times         |
| -------------------------------- | --------------------------------- |
| Advanced filters, export formats | Primary action and total cost     |
| Rare settings, integrations      | Destructive consequence           |
| Long explanations and help       | Current step and validation state |

## Defaults

- Pre-select the most common value; the default is the answer most users keep [8].
- Use the default as inline instruction: a representative value teaches the expected format and prevents errors [8].
- Never default to the option that profits you most; consistently defaulting to the expensive plan costs credibility [8].
- Default to the safer state — private visibility, marketing off, nothing pre-checked for irreversible or public actions [inference].
- Mark consequential defaults as defaults, so users can tell their choice from the system's [inference].
- Ship no default at all for high-stakes irreversible choices; an empty required choice forces a decision [inference].

## Destructive actions and modal dialogs

- Prefer undo to confirmation: a timed undo restores the user without interrupting the flow [10].
- Confirm only serious, irreversible consequences; routine confirmations teach users to dismiss them unread [10].
- Name the object and the consequence ("Delete 3 files, including Q3-report.pdf"), never "Are you sure?" [10].
- Label buttons by outcome ("Delete file" / "Keep file") rather than Yes/No [10].
- Give the destructive action no default and no initial focus; focus the least destructive control [9][10].
- For irreversible bulk operations, require a nonstandard action (type the project name), and reserve it for the rarest, most dangerous cases [10].
- Offer a way to skip future routine confirmations so experts are not interrupted every time [10].
- Open a modal only when the background must be inert while the user decides; a modal that merely displays information blocks work for nothing [9].
- Trap focus inside the modal (Tab and Shift+Tab cycle within), close on Escape, and return focus to the invoking element on close [9].
- Include a visible close control (X or Cancel) in the dialog's tab order [9].
- Set `aria-modal="true"` only when the background is genuinely inert and visually obscured [9].
- Place initial focus deliberately: first field for short forms, the content container for long text, the least destructive action for irreversible steps [9].

## Inline editing, drag and drop, and multi-step flows

- Edit inline for a single field already on screen; open a dedicated form when the change needs context the row does not show [inference].
- In inline edit, keep the row's identity visible, and provide explicit Save and Cancel — commit-on-blur leaves no exit [inference].
- Give every drag operation a single-pointer alternative: up/down buttons, a "Move to…" menu, or tap-item-then-tap-target [5].
- Keyboard equivalence alone does not satisfy the drag requirement; the alternative must work with clicks or taps only [5].
- Make the drop target and the drop result visible before commit, and allow undo afterwards [inference].
- Name the steps and show position ("Step 2 of 4 — Address"); unnamed steps leave users estimating the remainder [7].
- Use a wizard only when steps do not interleave; if users must compare across steps, use one screen [7].
- Do not add steps beyond the task's real decisions; excess navigation is the known failure of staged disclosure [7].
- Back must preserve entered data and land on the previous step, never restart the flow [inference].
- Make long flows resumable: save a draft and return to the last completed step [inference].

## Keyboard, focus, and hover

- Provide keyboard shortcuts for frequent actions and show them in menus and tooltips; accelerators are the expert half of flexibility and efficiency [1].
- Keep focus order equal to visual order; a focus ring that jumps around the layout breaks the model of the page [inference].
- Make focus visible with a high-contrast ring on every interactive element; never remove the outline without a replacement [inference].
- Trap focus only inside modals; everywhere else Tab must be able to leave the region [9].
- Return focus after any dialog, overlay, or inline edit closes, to the control that opened it [9].
- Send initial focus to the first field of a form opened by an explicit action, and to the page heading after navigation [inference].
- Bind Escape to cancel or dismiss, and Enter to submit only while a single-line input has focus [inference].
- Let hover add information, never gate it: tooltips and hover menus need focus and tap equivalents, and no label may be readable only on hover [2][inference].

## Sources

[1] [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: recognition over recall, visibility of state, accelerators, user control.
[2] [Beyond Blue Links: Making Clickable Elements Recognizable](https://www.nngroup.com/articles/clickable-elements/) — Hoa Loranger, Nielsen Norman Group — accessed 2026-11-27 — supports: signifiers, flat design, icons with labels, hover as weak cue.
[3] [Fitts's Law and Its Applications in UX](https://www.nngroup.com/articles/fitts-law/) — Raluca Budiu, Nielsen Norman Group — accessed 2026-11-27 — supports: target size and distance, crowding, padding, edge targets, menu placement.
[4] [Understanding SC 2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 24×24 CSS px minimum, spacing exception, 44×44 stricter tier.
[5] [Understanding SC 2.5.7 Dragging Movements](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: single-pointer alternative to drag, independence from keyboard equivalence.
[6] [Hick's Law](https://lawsofux.com/hicks-law/) — Laws of UX — accessed 2026-11-27 — supports: decision time, splitting steps, highlighting a recommended option.
[7] [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: two-level limit, split of initial and secondary features, staged disclosure and navigation cost.
[8] [The Power of Defaults](https://www.nngroup.com/articles/the-power-of-defaults/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: defaults as instructions, credibility cost, pre-populating common values.
[9] [Dialog (Modal) Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: focus containment, Escape, focus return, `aria-modal`, initial focus choice.
[10] [Confirmation Dialogs Can Prevent User Errors — If Not Overused](https://www.nngroup.com/articles/confirmation-dialog/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: undo over confirmation, specificity, outcome-labelled buttons, typed confirmation.
