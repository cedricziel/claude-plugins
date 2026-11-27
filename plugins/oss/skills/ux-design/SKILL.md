---
name: ux-design
description: >
  Design, critique, or repair user interfaces and information architecture:
  navigation, page structure, forms, flows, error and empty states, microcopy,
  accessibility, design-system use, and UX research plans. Use when building a
  UI, reviewing a screen or flow, deciding how information is organized, or
  arguing about a design decision. Do not use for backend architecture or
  brand-identity-only work.
---

# UX Design

A decision guide, not a style guide. It exists to make design choices
defensible and to stop the common failure where a screen is styled before the
task, states, and structure are settled.

Two jobs, one route:

- **Designing** something new — start at _Start With The Task_, then load one
  reference.
- **Critiquing** something existing — run
  [references/review-checklist.md](references/review-checklist.md), then load the
  reference for the weakest area.

## Start With The Task, Not The Screen

Answer these in two lines total before choosing components. No fetching, no
reference loading yet.

1. **Who and where** — the person, their situation, their device, their
   attention budget.
2. **The task, in their words** — not the feature name. If you cannot phrase it
   without internal jargon, the labels will be wrong too.
3. **Cost of failure** — reversible annoyance, lost money, lost data, or safety.
   This decides how much prevention, confirmation, and undo the flow earns.
4. **What already exists** — platform convention, design system, adjacent
   screens. Existing patterns win over this skill's defaults.

If 1 or 2 is genuinely unknowable, state the assumption in the output and
design for it. Do not invent a persona to avoid asking.

## Default Positions

These resolve most decisions without opening a file. They are the compressed
form of the references; read the reference when the decision is contested,
expensive, or unusual. A project or platform convention overrides them.

- **Structure** — one primary task per screen; the primary action is visually
  unmistakable and never below a wall of secondary controls.
- **Navigation** — 5-7 top-level destinations, labelled with the nouns users
  say, current location always visible.
- **Forms** — visible labels above fields, one column, one question per field,
  validate on blur, summary of errors plus inline messages on submit.
- **States** — every view ships loading, empty, partial, error, success, and
  permission-denied. Undesigned states are the most common review blocker.
- **Feedback** — acknowledge under 1s, reassure between 1s and 10s, show
  progress and an exit beyond 10s.
- **Destructive actions** — undo beats confirmation; confirmation beats nothing.
  Irreversible + expensive earns a typed confirmation.
- **Copy** — verb + object on buttons ("Delete project"), sentence case, the
  user's vocabulary, no exclamation marks.
- **Accessibility** — 4.5:1 body contrast, 3:1 for large text and UI edges,
  44px touch targets (24px is the legal floor, not the goal), visible focus,
  keyboard-operable everything.
- **Density** — choose per task, not per taste: operator and data screens can be
  dense; consent, payment, and onboarding cannot.

## Route To The Right Reference

Load **one** file. Load a second only when the work genuinely spans two areas.
Don't load the whole set, and don't re-read one already loaded this session.

| The work is about                                                               | Read                                                                        |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Grouping, labelling, hierarchy of content, sitemaps, taxonomies, findability    | [information-architecture.md](references/information-architecture.md)       |
| Menus, tabs, breadcrumbs, search vs browse, wayfinding, deep links              | [navigation-and-wayfinding.md](references/navigation-and-wayfinding.md)     |
| Visual hierarchy, spacing, grids, type scale, density, responsive reflow        | [layout-and-visual-hierarchy.md](references/layout-and-visual-hierarchy.md) |
| Fields, labels, validation, checkout, long forms, saving progress               | [forms.md](references/forms.md)                                             |
| Affordances, target size, choice cost, modals, progressive disclosure, defaults | [interaction-patterns.md](references/interaction-patterns.md)               |
| Waiting, progress, loading, optimistic updates, success confirmation            | [feedback-and-status.md](references/feedback-and-status.md)                 |
| Error messages, recovery, empty and no-result states, partial failure           | [errors-and-empty-states.md](references/errors-and-empty-states.md)         |
| First run, activation, tours, time-to-value, progressive onboarding             | [onboarding-and-first-run.md](references/onboarding-and-first-run.md)       |
| Wording, labels, tone, plain language, link text, formatting                    | [content-and-microcopy.md](references/content-and-microcopy.md)             |
| Contrast, keyboard, focus, screen readers, WCAG conformance, motion             | [accessibility.md](references/accessibility.md)                             |
| Reusing vs extending vs creating components, tokens, conventions                | [design-systems.md](references/design-systems.md)                           |
| Test plans, participant counts, heuristic evaluation, metrics, A/B              | [research-and-validation.md](references/research-and-validation.md)         |
| A review pass, severity, or a pre-ship gate                                     | [review-checklist.md](references/review-checklist.md)                       |

If two rows fit, pick the one matching the artifact you will change (a form →
`forms.md`, not `information-architecture.md`). [index.md](references/index.md)
carries the same map with the primary source behind each file, plus the cost of
loading it.

## Verify Before You Assert

Citations are cheap; fabricating one is expensive. Match effort to stakes.

- **Tier 0, default — cite from the reference.** Every reference ends with
  numbered sources and inline `[n]` markers. Reuse them. Zero fetches.
- **Tier 1, load-bearing — fetch exactly one page.** Do this when
  (a) the recommendation is irreversible or costly, (b) two references conflict,
  (c) the user challenges the advice, or (d) you are about to state a specific
  number (ratio, participant count, percentage, duration). Fetch the deep link
  from that reference's source list, confirm, stop.
- **Tier 2, skip — re-verifying a paraphrase.** Don't fetch a homepage to
  "double-check" something already cited, don't fetch a second source for the same
  claim, and don't paste page text into the answer.

Rules:

- A citation you did not read is a fabrication. If you could not fetch, write
  "per [n] in `references/<file>.md` (not re-verified)" and keep going.
- **At most three verification fetches per session.** On the fourth, list the
  claims that remain unverified instead of fetching.
- If the live source contradicts the reference, say so in one line and follow
  the live source when the page is visibly newer (a WCAG or design-system
  version bump is exactly this case).
- The `[inference]` tag marks a judgement no cited source makes. Treat it as an
  opinion and say so when it drives a decision.

## Alignment Check

Five questions before delivering. No fetching, no reference loading.

1. On every screen, can the person tell where they are, what they can do, and
   what happens next?
2. Is the primary action unambiguous, and is there one?
3. Are loading, empty, error, and permission states designed — not implied?
4. Does the copy use the user's words and name outcomes?
5. Keyboard, focus, contrast, and label association checked?

Any "no" is a blocker, not a nit.
[references/review-checklist.md](references/review-checklist.md) expands this
into a full ordered pass with severity.

## Output Shape

- **Decision first.** One or two sentences: what you recommend and why.
- **Then the change.** Component, copy, state, layout — concrete enough to
  apply without interpretation.
- **Then the evidence tag.** `forms.md [3]` plus the reference path is enough;
  don't reproduce the source's prose.
- **Split must-fix from optional.** Severity beats completeness in reviews.
- **Name the failure mode** the change prevents. "Prevents accidental delete"
  is reviewable; "improves UX" is not.

## Boundaries

- Not brand identity, illustration direction, or logo work.
- Not framework implementation detail — component APIs are the design system's
  job.
- Not legal advice on deceptive patterns; name the pattern and the harm.
- Does not override a project's design system, platform conventions, or
  documented user research. Missing evidence is a reason to say so, not to
  invent a rule.

## Guardrails

[scripts/ux-lint.py](scripts/ux-lint.py) is the deterministic half of this skill:
shipped placeholder copy, non-semantic click targets, a removed focus ring,
images without alt, raw colour beside a real token set, off-scale spacing, and
marketing vocabulary. It exits 2 on a blocking finding, 0 otherwise.

The oss plugin runs it on every UI edit — `PreToolUse` blocks the four
unambiguous defects before they land, `PostToolUse` attaches up to six findings
to the next model step, once per session. Run it by hand with
`python3 scripts/ux-lint.py --staged`, or check one file with
`python3 scripts/ux-lint.py src/Hero.tsx`. Off switches: `UX_LINT_DISABLE=1`, a
`.no-ux-lint` file at the repo root, or `ux-lint-ignore` on the line before a
finding the project intends.

It is a floor, not a review. It cannot see hierarchy, density, or whether the
states exist; that is what the checklist and the reference files are for.

## Sources And Licensing

The references synthesize public guidance from Nielsen Norman Group, the W3C
(WCAG 2.2 understanding docs, WAI-ARIA Authoring Practices, WAI tutorials),
GOV.UK Design System and GOV.UK content guidance, USWDS, Baymard Institute,
Laws of UX, MeasuringU, Mailchimp's content style guide, and Google Research,
plus practitioner writing from Smashing Magazine, A List Apart, WebAIM, Adrian
Roselli, Heydon Pickering's Inclusive Components, Sara Soueidan, Adam Silver,
Brad Frost, Josh Comeau, and Practical Typography. Each file lists the exact
pages it drew on, the access date, and what each supports.

Text is paraphrased; quotations stay under 25 words and are attributed. Nothing
here reproduces a source wholesale, and no source is paywalled content
paraphrased from memory. Nielsen's ten heuristics are credited to Jakob Nielsen
and Nielsen Norman Group and linked to their canonical page.

## Maintenance

- New source: append to the relevant file's `## Sources`, keep the numbering,
  update the access date, and add the inline marker where it supports a bullet.
- Version-sensitive sources (WCAG, GOV.UK, USWDS) get re-read when they publish
  a release, not on a schedule.
- If a rule stops being true, delete it. A reference that argues with itself
  costs more than a missing one.
