# Accessibility

This file answers what WCAG 2.2 Level AA actually requires of a screen, which criteria design work breaks most often, and how to verify a conformance claim without trusting a scanner. Read it when contrast, zoom, keyboard, focus, semantics, motion, or an accessibility claim is in play. It does not cover wording, layout craft, or form flow; the sibling references handle those and inherit the constraints here.

## What AA Commits You To, And Where It Changes Design

- Each success criterion carries a conformance level: 3.3.1 is Level A; 1.4.3, 1.4.10, 1.4.11, 1.4.12, 2.4.7, 2.4.11 and 2.5.8 are Level AA [1][2][3][4][5][6][7][8].
- Treat AA as the design bar, not the ceiling: 24×24 px targets and 3:1 component contrast are minimums that pass review and still hurt real users [2][7].
- Decide accessibility at the moment of choice: palette (contrast), control type (native vs ARIA widget), density (target size), states (focus, error, disabled), motion defaults, and content (alt text, captions) [1][4][7][9].
- Retrofitting any of those is a rewrite of tokens, components, and content; the cheap moment is before the first screen is styled [inference].
- A component library is not evidence. Failures survive in disabled, error, focus, and empty states that the library never designed [inference].
- A clean scan is not a conformance claim. Quick checks cover only a few issues, and a page can pass them while still carrying significant barriers [10].
- A conformance claim covers pages, not components or flows; a control that passes in isolation can fail inside a sticky header [inference].

## Contrast And Non-Text Visibility

- Body text needs 4.5:1 against its actual background; large text needs 3:1 [1].
- Large means at least 24 px, or at least 18.5 px when bold (18 pt / 14 pt bold) [1].
- Thresholds are not rounded: 4.49:1 fails 4.5:1, and 2.99:1 fails 3:1 [1][2].
- Measure the worst pixel: text over photographs, gradients, or scrims must pass where contrast is lowest, not where it looks best [1].
- Placeholder text, tooltip text, and text shown on hover or focus are all in scope [1].
- Disabled controls are exempt from both contrast criteria, but a disabled label still has to be readable enough to explain why the control is off [1][2].
- Logos are exempt; an author-chosen wall of low-contrast logos on a dark background is not [1].
- Hold 3:1 for the visual information that identifies a control and its state: input borders, checkbox outlines, toggle tracks, selection indicators, meaningful icons [2].
- A button with a visible text label needs no contrasting border to satisfy 1.4.11, but its focus indicator still needs 3:1 [2].
- A focus ring must contrast with the adjacent background; a two-colour ring survives both light and dark surfaces where a single-colour ring disappears [2][5].
- Chart lines, bars, map regions, and status icons are graphical objects: 3:1 against adjacent colours wherever they carry meaning [2].
- If the same values appear as text or in a table, the graphic is no longer required for understanding and the contrast bar drops [2].
- Inline body links need a non-colour cue such as an underline, or 3:1 against the surrounding text [2].
- Test in a user contrast theme, not only in default colours: forced-colors drops background images, gradients, and shadows, so every boundary and state must survive as a border, text, or `currentColor` icon, and the user's palette must not be overridden [13].

## Zoom, Reflow, And Text Spacing

- Content must work at 320 CSS px wide with no horizontal page scroll; that is a 1280 px viewport at 400% zoom [3].
- Two-dimensional scrolling is allowed only where the content needs it: data tables, maps, video, games, presentations, persistent toolbars [3].
- A table may scroll inside its own container, but the heading, search field, and pagination around it must still reflow [3].
- Sticky headers, footers, and chat widgets must not consume the viewport at 400%; make them static, collapsible, or dismissible at small widths [3].
- Test 200% text zoom and 400% page zoom separately; text enlargement and reflow fail for different reasons [3][inference].
- Text spacing overrides must not clip or overlap: line height 1.5×, paragraph spacing 2×, letter spacing 0.12×, word spacing 0.16× [4].
- The usual failures are fixed-height rows, single-line buttons with `overflow: hidden`, and absolutely positioned labels [4].
- Truncation is acceptable only when the full text is reachable by focus, expansion, or a linked page [4].
- Reflow failures are design decisions, not bugs: fixed card widths, side-by-side label/field pairs, and multi-column footers [3][inference].

## Keyboard, Focus Order, Focus Visibility

- Every interactive element must be operable by keyboard; a pointer-only control is a blocker [5][11].
- Tab order follows DOM order; fix order by moving elements, never by adding positive `tabindex` values [11].
- One tab stop per composite widget (tabs, menu, radio group, grid); arrow keys move inside it and Tab leaves [11].
- Roving `tabindex` or `aria-activedescendant` are the two supported ways to manage focus inside a composite [11].
- Never remove focus styling without a replacement; `outline: none` alone fails 2.4.7 [5].
- Use `:focus-visible` so pointer users do not see rings while keyboard users always do [5].
- The focus indicator must be visible in at least one mode of operation and must not time out [5].
- The focused element must not be fully hidden by sticky headers, sticky footers, cookie banners, or non-modal dialogs; add scroll padding or make the layer modal [6].
- When a dialog closes or an item is deleted, return focus to the trigger or the next surviving item, or focus falls to the page body [11].
- A skip link as the first focusable element is the cheapest fix for long navigation [10].
- Do not move initial focus on page load unless the page has one dominant task almost everyone performs immediately [11].

## Semantics, Accessible Names, Live Regions

- Native HTML controls ship keyboard behaviour; an ARIA role does not, so every ARIA widget adds keyboard and focus code you own [11].
- A `div` with `role="button"` inherits focusability, Enter and Space handling, disabled semantics, and name computation as your work [11][inference].
- Every focusable control needs an accessible name, and placeholder text is not a label because it disappears on input [inference].
- Name the control by what it does, not what it looks like: "Close dialog", not "X" [inference].
- Prefer the visible label as the accessible name; a divergent `aria-label` breaks voice control, which speaks the visible text [inference].
- Group related controls with `fieldset` and `legend` for radio groups, and with a named group only where native grouping is unavailable [inference].
- Announce asynchronous outcomes in a live region: `role="status"` for polite results ("Saved"), `role="alert"` for failures needing immediate attention [inference].
- Keep the live-region node in the DOM before changing its text, and do not announce the same event through both a live region and a focus move [inference].
- Headings are the page's table of contents for screen readers; a skipped level breaks the outline even when the visual size looks right [10][inference].
- The page title names screen and state ("Invoice 1042 – Paid") and is the first thing a screen reader announces [10].
- Mark up data tables with `<caption>` and `<th scope="col">` / `<th scope="row">`, and keep `<caption>` and `<th>` out of layout tables; otherwise screen readers announce a data grid with navigation that does not exist [14].

## Forms, Labels, Errors

- Label every field visibly and programmatically; place the label above the field for left-to-right languages and make it clickable [8][inference].
- Mark required fields in text ("Required"), not with colour or an unexplained asterisk; colour alone fails 1.4.1 [2].
- On submit failure, identify each field in error and describe the problem in text; icons and colour may supplement but not replace it [8].
- Say what to do next, not only what is wrong: "Enter a date as DD/MM/YYYY" satisfies both error identification and error suggestion [8].
- Pair a top-of-form error summary (linking to each field) with inline messages; either alone is permitted, together they work at zoom [8][inference].
- Native browser validation exposes only the first error and its bubble may not scale with page zoom; do not rely on it for multi-field forms [8].
- Preserve everything the user typed on error; clearing fields turns a correction into a restart [inference].
- Validate on blur and on submit, not on every keystroke, and never block paste into password or code fields [inference].
- Error text itself needs 4.5:1 and must survive colour-blind viewing [1][2].

## Motion, Colour, Media Alternatives

- Honour `prefers-reduced-motion` for parallax, scroll-triggered movement, and large transitions [9].
- Non-essential motion triggered by interaction must be disableable; vestibular reactions include dizziness, nausea, and migraine [9].
- Animation the page starts on its own is a separate problem: provide visible controls to stop animation and autoplaying sound [10].
- Colour is never the only channel; pair it with text, an icon, a pattern, or position for required, error, selected, and chart-series identity [2].
- Provide captions for prerecorded video with speech, transcripts for audio, and audio description when visuals carry meaning absent from the soundtrack [10].
- Give every image an `alt` attribute: empty for decorative or redundant images, purpose rather than appearance for informative ones, and the destination when the image is the only content of a link or button; charts need a data table or text alternative [10][2][12].
- Avoid text baked into images; where unavoidable, meet 4.5:1 inside the image and repeat the text nearby [1].

## Testing Without A Scanner

- Keyboard pass: tab the whole screen, confirm order, visible focus, no traps, Escape closes overlays, focus returns afterwards [5][11].
- Zoom pass: 200% and 400%, plus a text-spacing override; look for clipped labels, overlap, and horizontal scroll [3][4].
- Screen-reader smoke test: hear name, role, and state for each control, then one form error and one async update [inference].
- Target pass: measure the smallest interactive target; 24×24 CSS px is the floor and 44×44 the design goal, with 24 px spacing circles for undersized targets [7].
- Contrast pass: sample text over imagery, borders, placeholders, focus rings, and disabled labels, and log the measured ratios [1][2].
- State pass: focus, hover, active, disabled, error, loading, empty, plus dark and high-contrast modes [inference].
- These checks catch barriers a visual pass misses, but they are not exhaustive; passing them is a floor, not a certificate [10].
- Recruit at least one assistive-technology user for flows with legal, financial, or health consequences; expert inspection is not a substitute [inference].
- A conformance claim names the screen readers, browsers, operating systems, and versions tested and what each announced; "screen-reader tested" without that list is an assertion, not a result [15].

## Sources

[1] [Understanding SC 1.4.3: Contrast (Minimum) (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 4.5:1 and 3:1 thresholds, large-text sizes, no rounding, text over images, placeholders/hover text, disabled and logo exemptions.
[2] [Understanding SC 1.4.11: Non-text Contrast (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 3:1 for control boundaries, states, focus indicators, graphical objects; disabled exemption; relationship with Use of Color.
[3] [Understanding SC 1.4.10: Reflow (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 320 CSS px and 256 px requirements, 400% zoom equivalence, two-dimensional exceptions, sticky content, table containers, Resize Text overlap.
[4] [Understanding SC 1.4.12: Text Spacing (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 1.5/2/0.12/0.16 spacing metrics, clipping and overlap failures, truncation and reveal mechanisms.
[5] [Understanding SC 2.4.7: Focus Visible (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: visible focus in a mode of operation, no timeout, 1.4.11 applying to indicators, `:focus-visible`.
[6] [Understanding SC 2.4.11: Focus Not Obscured (Minimum) (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: sticky headers and footers, cookie banners, modal dialogs, scroll padding, user-opened overlays.
[7] [Understanding SC 2.5.8: Target Size (Minimum) (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 24×24 CSS px, 24 px spacing circles, inline and essential exceptions, 44×44 enhanced target.
[8] [Understanding SC 3.3.1: Error Identification (Level A)](https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: error described in text, field identification, error summary vs inline, native validation limits, overlap with 3.3.3.
[9] [Understanding SC 2.3.3: Animation from Interactions (Level AAA)](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: `prefers-reduced-motion`, parallax and interaction-triggered animation, vestibular harm, difference from 2.2.2.
[10] [Easy Checks – A First Review of Web Accessibility](https://www.w3.org/WAI/test-evaluate/easy-checks/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: skip link, visible focus, zoom, headings, labels, captions, transcripts, audio description checks, and the warning that passing them is not comprehensive.
[11] [Developing a Keyboard Interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) — W3C ARIA Authoring Practices Guide — accessed 2026-11-27 — supports: keyboard operability, DOM-order tab sequence, `tabindex` values, roving tabindex, `aria-activedescendant`, focus persistence, initial focus guidance.
[12] [Alternative Text](https://webaim.org/techniques/alttext/) — WebAIM — accessed 2026-11-27 — supports: every image needs an alt attribute, empty alt for decorative and redundant images, functional images inside links and buttons, "image of" redundancy, context deciding the text.
[13] [WHCM and System Colors](https://adrianroselli.com/2021/02/whcm-and-system-colors.html) — Adrian Roselli — accessed 2026-11-27 — supports: forced-colors stripping background images, gradients, and shadows; `currentColor` for icons; honouring the user's contrast theme and system colour pairings.
[14] [Creating Accessible Tables — Data Tables](https://webaim.org/techniques/tables/data) — WebAIM — accessed 2026-11-27 — supports: `<caption>`, `<th>` and `scope`, headers never empty, layout tables that must not use data-table markup, proportional sizing.
[15] [Your Accessibility Claims Are Wrong, Unless…](https://adrianroselli.com/2022/11/your-accessibility-claims-are-wrong-unless.html) — Adrian Roselli — accessed 2026-11-27 — supports: naming the assistive technology, browser, OS and versions tested, showing what was announced, distrusting inspector output.
