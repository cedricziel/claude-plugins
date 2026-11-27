# Layout and Visual Hierarchy

Answers one question: in what order will a reader's eye travel through this screen, and does that order match what matters? Read it when reviewing page structure, spacing, type, grid, responsive behaviour, dark mode, or colour. It stops at the boundary of wording — for headings, labels, and error text see `content-and-microcopy.md`.

## Reading order is a decision

- Before styling, list the three elements the eye must hit first, in order; review the rendered page against that list, not against taste. [1]
- Build rank from size, weight, contrast, position, isolation, and whitespace together; one channel alone carries too little signal. [1]
- Hold the page to three type sizes (body, subhead, head) and at most two large elements per screen. [1]
- Cap the palette at two primary and two secondary colours and no more than three contrast variations; when everything is contrasted, nothing leads. [1]
- Give the primary action its own fill; if Cancel and Submit share a colour, users must read both labels to find the exit. [4]
- Pair every colour cue with size, weight, icon, or text — hue alone fails readers with colour vision deficiency and fails SC 1.4.1. [1][8]
- Squint test: blur 5–10px and confirm the intended first element survives longest; a 20px blur exposes a bright photo or tile outranking the template. [1]

## Grouping: proximity first, containers second

- Place related controls nearer each other than to anything else; the gap carries the grouping and the border only repeats it. [2]
- Set space above a heading to at least 1.5× the space below it, so the heading binds to its own section. [6]
- Keep a field label closer to its input than to the previous field; equal gaps make label ownership ambiguous. [2]
- Chunk long forms: 12 fields in one block read as heavier than the same 12 split into three meaningful groups. [2]
- Re-check proximity after reflow; stacking two compared columns on mobile can push items that belonged side by side screens apart. [2]
- Add a border or background only when whitespace has failed; common region overrides proximity and similarity, and is easy to overuse. [3]
- Drop decorative borders: unnecessary boxes add noise, and full-width bands create false floors that stop scrolling. [3]
- Reuse one shape, colour, and size per function; two near-identical icons in one menu read as the same command. [4]
- Use closure for cheap grouping — a rule, an edge-aligned run, or a background change implies the container — then check that the implied edges do not group unrelated items. [inference]

## Grid and alignment

- Set an explicit column grid and place every block on it; a block that misses the grid reads as a mistake, not as emphasis. [inference]
- Left-align body text: a constant starting point per line is what makes a column scannable. [6]
- Keep one left edge shared by headings, body, lists, and captions; centred paragraphs and justified text both destroy that recurring start. [6]
- Right-align numeric columns and use tabular figures so digits stack vertically. [6]
- Align controls to the text column rather than the viewport edge on wide screens. [inference]
- Fix ragged edges before adding polish: unequal card heights in a row, or a button a few pixels off the field edge, read as breakage. [inference]
- Limit centred text to a short heading plus one supporting line; longer centred runs lose the left anchor. [inference]

## Whitespace groups and paces

- Use space to separate before adding a rule or a box; removing chrome usually reads cleaner than adding it. [3]
- Set at least 1em between paragraphs and 0.5em between list items; below that, blocks fuse. [6]
- Keep container padding smaller than the margin around the container, or the container stops reading as one group. [inference]
- Give the most important element more surrounding space; isolation is a hierarchy channel, not wasted area. [1]
- Never compress to fit: if the content only fits by dropping padding under the grouping threshold, cut content or split the screen. [2]
- Use one spacing scale (4px or 8px steps) for every margin and padding value so section rhythm stays comparable across templates. [inference]

## Type: scale, measure, leading

- Keep body at 16px or larger; the three-step scale of 14–16 / 18–22 / ≤32px satisfies both the size cap and the floor. [1][6]
- Hold running text to 45–90 characters per line, targeting 66 for long passages. [6]
- Set line height at 1.5 or more for body text, and 1–1.35 for headings of one or two lines. [6]
- Increase line height as measure grows; long lines need more separation to keep the return sweep findable. [6]
- Constrain measure with a max-width on the text column, not the page, so a sidebar does not dictate reading width. [6]
- Avoid long runs of bold, italic, or uppercase; all three slow reading, and uppercase removes word shape. [6]
- Separate paragraphs with space, not first-line indents; indentation is a print convention. [6]
- Stop at two typefaces, and give the second a distinct role (code, numerals) rather than variety. [inference]

## Scanning: F, layer-cake, Z

- Expect F-shaped scanning whenever text is unformatted, the user is efficient, and the user is not committed to reading. [5]
- Put the main point in the first two paragraphs; later lines collect fewer fixations. [5]
- Make headings visually stronger than body text and readable on their own; that invites layer-cake scanning instead of a wall of text. [5]
- Front-load the first two words of every heading, link, and bullet — that is where fixations concentrate. [5]
- Avoid list items that all open with the same word; readers skip the shared prefix (bypassing pattern). [5]
- Align to the content column's left edge, not the page edge: the F stem falls where the text starts, not where the nav ends. [5]
- Put numbers and distinctive word shapes where they will be found; digit-seeking fixations are a documented scan mode. [5]
- Reserve Z-pattern layouts for sparse pages with one headline and one action; do not design a text page for Z. [inference]

## Above the fold and density

- Treat the first viewport as a promise: it must name the page and show one next action, or nothing below it gets seen. [5]
- Keep orientation and the primary action above the fold at every breakpoint; the fold moves with the device but never disappears. [inference]
- Set density from use frequency, not from brand: an hourly operator screen keeps filters, values, status, and the primary action visible, on 32–40px rows. [10][inference]
- On expert screens, defer rather than delete; staged disclosure keeps capability while removing the clutter that slows visual search. [10]
- Raise salience by subtraction: deleting an icon beside a dashboard number makes the number easier to find than bolding it. [10]
- Do not apply marketing spacing to a comparison screen; padding that scatters related numbers costs more than it buys. [10]

| Screen                        | Keep visible                                    | Defer or remove                            |
| ----------------------------- | ----------------------------------------------- | ------------------------------------------ |
| Operator console (hourly use) | filters, current values, status, primary action | help prose, illustrations, onboarding [10] |
| Analyst table or record view  | column headers, row identity, bulk actions      | column chooser, advanced filters [10]      |
| Settings or onboarding        | one task per screen, current step               | other sections, marketing copy [10]        |
| Marketing or landing page     | value statement, one primary CTA                | feature detail, dense tables [inference]   |

## Reflow, dark mode, structural colour

- Test text at 320 CSS px (1280px at 400% zoom) with no horizontal scrolling. [7]
- Restrict two-dimensional scrolling to the excepted content — tables, maps, video, canvases, persistent toolbars — and keep it inside that container. [7]
- Convert sticky headers and footers to static below the tablet breakpoint so they cannot eat the reading area. [7]
- Do not ship dark mode as the default for a general audience; light mode measured better for normal vision, while dark mode helps some low-vision users. [9]
- Offer the switch, follow the OS preference, and apply it across every screen rather than one page. [9]
- Re-tune dark themes rather than inverting them: light text on dark gains apparent weight, so drop one weight step and avoid pure white on pure black. [inference]
- Treat colour as structural only when it repeats a meaning defined elsewhere — status, category, required — and give each one a label, icon, or pattern. [8]
- Keep decorative colour off the tokens that carry meaning; a brand tint that matches the error red teaches users to ignore errors. [8][inference]
- Accept a hue pair only when it also differs in luminance by 3:1 or more; hue-only pairs fail as a distinction. [8]

## Sources

[1] [Visual Hierarchy in UX: Definition](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/) — Kelley Gordon, Nielsen Norman Group — accessed 2026-11-27 — supports: reading order, scale and contrast caps, the squint test, grouping.
[2] [Proximity Principle in Visual Design](https://www.nngroup.com/articles/gestalt-proximity/) — Aurora Harley, Nielsen Norman Group — accessed 2026-11-27 — supports: grouping, form chunking, proximity loss under reflow.
[3] [The Principle of Common Region: Containers Create Groupings](https://www.nngroup.com/articles/common-region/) — Aurora Harley, Nielsen Norman Group — accessed 2026-11-27 — supports: containers, border overuse, false floors.
[4] [Similarity Principle in Visual Design](https://www.nngroup.com/articles/gestalt-similarity/) — Aurora Harley, Nielsen Norman Group — accessed 2026-11-27 — supports: shared shape/size per function, reserved CTA colour, near-identical icons.
[5] [F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant (Even on Mobile)](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/) — Kara Pernice, Nielsen Norman Group — accessed 2026-11-27 — supports: scanning patterns, first two paragraphs, heading and first-word guidance.
[6] [Typography](https://designsystem.digital.gov/components/typography/) — U.S. Web Design System (GSA) — accessed 2026-11-27 — supports: 16px floor, measure 45–90, line height, flush-left alignment, paragraph and list spacing, uppercase.
[7] [Understanding SC 1.4.10 Reflow (Level AA)](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: 320/256 CSS px, two-dimensional exceptions, sticky header guidance.
[8] [Understanding SC 1.4.1 Use of Color (Level A)](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: second channel for colour-coded meaning, 3:1 luminance distinction.
[9] [Dark Mode vs. Light Mode: Which Is Better?](https://www.nngroup.com/articles/dark-mode/) — Raluca Budiu, Nielsen Norman Group — accessed 2026-11-27 — supports: light-mode default, offering a switch, OS preference.
[10] [8 Design Guidelines for Complex Applications](https://www.nngroup.com/articles/complex-application-design/) — Kate Kaplan, Nielsen Norman Group — accessed 2026-11-27 — supports: staged disclosure, clutter reduction, visual salience by subtraction.
