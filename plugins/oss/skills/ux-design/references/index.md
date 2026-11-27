# Reference Index

The routing table in `../SKILL.md` is the fast path. This file is for the
second question — _what is behind this rule, and how much does reading it
cost?_ — and for adding sources later.

## Cost

| Load          | Size                                          |
| ------------- | --------------------------------------------- |
| `SKILL.md`    | ~1,400 words, roughly 1,800 tokens            |
| one reference | 1,400–2,000 words, roughly 2,000–2,600 tokens |

Skill plus one reference is about 4,000 tokens. That is the design point: enough
to argue a decision, not enough to drown the task. Two references are the
ceiling, and a third means the question is too broad — narrow it instead.

## Files

| File                                                             | Answers                                                   | Primary sources                                                                                                                        |
| ---------------------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| [information-architecture.md](information-architecture.md)       | How content is inventoried, grouped, shaped, and labelled | NN/g (IA vs navigation, card sorting, tree testing, flat vs deep, taxonomy, information scent, search logs)                            |
| [navigation-and-wayfinding.md](navigation-and-wayfinding.md)     | How the structure is exposed; where am I, where can I go  | NN/g (menu checklist, hamburger study, mega menus, breadcrumbs, deep linking) + W3C WAI menus tutorial                                 |
| [layout-and-visual-hierarchy.md](layout-and-visual-hierarchy.md) | What the eye hits first; grouping, grid, type, density    | NN/g (visual hierarchy, gestalt, F-pattern, dark mode, complex apps) + USWDS typography + WCAG 1.4.1, 1.4.10                           |
| [forms.md](forms.md)                                             | Collecting input correctly the first time                 | GOV.UK Design System (text input, error message, error summary, question pages) + W3C WAI forms + NN/g placeholders + Baymard checkout |
| [interaction-patterns.md](interaction-patterns.md)               | Target size, choice cost, disclosure, defaults, dialogs   | WCAG 2.5.7/2.5.8, ARIA APG dialog, NN/g (Fitts, progressive disclosure, defaults, confirmations), Laws of UX (Hick)                    |
| [feedback-and-status.md](feedback-and-status.md)                 | What happens between an action and its result             | NN/g (response times, progress indicators, skeleton screens, animation) + W3C WAI notifications                                        |
| [errors-and-empty-states.md](errors-and-empty-states.md)         | Failures, no-results, and unpopulated containers          | NN/g (slips, error messages, empty states, no-results SERP) + GOV.UK error components                                                  |
| [onboarding-and-first-run.md](onboarding-and-first-run.md)       | First run, activation, and time to value                  | NN/g (onboarding tutorials, mobile onboarding, empty states, product-led growth) + GOV.UK (start a service, accounts, email confirmation) + WCAG 3.2.1                                                                                 |
| [content-and-microcopy.md](content-and-microcopy.md)             | Whether the words work                                    | NN/g (readability, 3 C's, error messages) + W3C writing tips + GOV.UK A–Z + Mailchimp translation guide                                |
| [accessibility.md](accessibility.md)                             | Contrast, keyboard, focus, semantics, motion              | WCAG 2.2 understanding docs, WAI-ARIA APG, W3C WAI tutorials and easy checks                                                           |
| [design-systems.md](design-systems.md)                           | Reuse, extend, or create; tokens and conventions          | NN/g Design Systems 101, USWDS tokens and component inventory, GOV.UK components, Laws of UX (Jakob)                                   |
| [research-and-validation.md](research-and-validation.md)         | What evidence to gather and how much is enough            | NN/g (five users, heuristic evaluation, usability testing), SUS, Google HEART                                                          |
| [review-checklist.md](review-checklist.md)                       | A repeatable pre-ship pass with severity                  | Synthesis; cites the heuristics, WCAG criteria, and deceptive-pattern research behind each check                                       |

## Reading Rules

- Read the frame paragraph first. Every file opens with the question it answers
  and the neighbouring file it hands off to. If the frame does not match your
  question, you are in the wrong file.
- Skip tables and examples on the first read unless the decision is visual.
  Bullets carry the rules; tables carry the comparison.
- Stop at the section you need. Sections are independent by design.
- Do not read a file to confirm a decision you already made for reasons the file
  would not know (project convention, user research, platform constraint).
  Those beat the reference, and saying so is cheaper than reading.
- Treat `[inference]` as opinion. It marks a judgement the cited sources do not
  make; it is the first thing to drop when a user pushes back.

## Adding A Source

1. Fetch the page. If it does not load, it does not get cited — no exceptions.
2. Append to that file's `## Sources` in numbering order:
   `[n] [Title](URL) — Author or org — accessed YYYY-MM-DD — supports: <the claim it backs>`
3. Put `[n]` immediately after the bullet it supports. A bullet with no marker
   and no `[inference]` is a defect.
4. Update the file's row above if the source changes what the file covers.
5. Run `python3 -m unittest tests.test_ux_design_skill`: it checks that every
   reference is routed, every source is linked and dated, and no marker points
   at a source that is not listed.

Prefer a deep article URL over a homepage, and prefer a primary standard (WCAG
understanding doc, design-system component page) over commentary about it. One
good source beats three that repeat each other.

## Provenance

Synthesis of public guidance, paraphrased, with quotes kept under 25 words and
attributed. Nielsen's ten heuristics are credited to Jakob Nielsen and Nielsen
Norman Group at their canonical page. No file reproduces a source wholesale, and
no paywalled content is paraphrased from memory — anything not readable at the
cited URL was dropped rather than guessed.

Access dates are recorded per source. Version-sensitive sources (WCAG, GOV.UK,
USWDS) get re-read when they publish a release, and a contradiction found then
is fixed in the reference rather than worked around in the answer.

What was dropped: Material Design 3 and Apple Human Interface Guidelines pages
render client-side and returned no extractable text, so neither is cited. Where
a platform-convention claim needed a source, Laws of UX and NN/g carry it, and
the rest is marked `[inference]`.
