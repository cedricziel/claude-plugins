# Design Systems

This file answers whether to reuse, extend, or create a component, how tokens and component APIs keep a system from rotting, and how to audit one that already exists. Read it when the work touches a shared component library, a token set, or a second product that must behave like the first. Accessibility constraints live in `accessibility.md`; this file assumes them and covers reuse economics, naming, and maintenance.

## Choose Reuse, Extension, Or Creation

- Default to reuse. A component used as designed costs composition only [1].
- Adopt before you adapt, and adapt before you create: cost, control, and brand differentiation rise along that axis [1].
- Create only when behaviour differs. An appearance difference is a variant request, not a new component [inference].
- Never fork a component into a product folder; a fork loses upstream fixes and splits the meaning of its name [inference].
- Extend at the token or variant layer, not with per-screen overrides; a one-off style prop is untested API from the day it lands [inference].
- Count consumers before extending: a variant for one screen is a local composition or a documented exception [inference].
- A system's public inventory is its contract: GOV.UK ships a named component for each recurring job and expects teams to compose those parts across different patterns and contexts [4].
- Compose before extending: most "missing components" are an existing text input, alert, or summary list arranged differently [4].

| Option              | Use when                                                    | Real cost                                                         |
| ------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------- |
| Reuse               | Behaviour and appearance both match                         | None beyond composition                                           |
| Extend, new variant | Same behaviour, one new axis (size, emphasis, density)      | New state × theme × accessibility combinations for every consumer |
| Create              | Behaviour genuinely differs (async combobox, editable grid) | Docs, states, keyboard model, tests, versioning, deprecation      |

Costs in the table are [inference]; the adopt → adapt → create ordering and the direction of cost are from [1].

- A design system is a product with users, a team, and a backlog; without a named owner it decays into an unused library [1].
- A library ships defaults, not decisions: disabled, error, empty, and permission states still need design per screen [inference].

## Tokens, Not Values

- Every colour, space, radius, border, shadow, type size, and duration comes from a token; a raw hex or px in a component file is a defect [2].
- Tokens are a deliberately small set drawn from a continuum; their job is to remove forty shades of grey from review [2].
- Limit each property to a named scale the way USWDS limits measure to seven tokens, rather than adding a value per screen [2].
- Name tokens by role (`surface`, `text-muted`, `danger`, `space-2`), never by value (`grey-500`); value names lie the moment a theme changes [inference].
- Separate primitive tokens (palette) from semantic tokens (role) and let components reference semantic tokens only [inference].
- Theme by swapping semantic values, never by overriding a component's internals per brand [inference].
- Keep a motion scale (for example 100/150/250 ms) and a named easing set; ad-hoc cubic-beziers are the most common untokenised value after colour [inference].
- Hardcoded values rot silently: dark mode, high-contrast mode, density, and rebrand all miss them, and audits cannot find them by token name [inference].
- A value like `13px` or `18px` signals a missing scale step; fix the scale, not the screen [inference].

## Component API, Naming, Documentation

- Prefer variants over booleans: two booleans create four combinations, five create thirty-two, and half are undefined [inference].
- Accept one `variant` enum plus orthogonal `size` and `tone`; reject `isPrimary` / `isSecondary` / `isDanger` triples [inference].
- Use slots or children for content; a component that takes `title`, `subtitle`, `iconLeft`, `iconRight`, and `actions` is a page pretending to be a component [inference].
- Do not expose raw style props (`color`, `padding`, `fontSize`); they bypass tokens and make every screen unique again [inference].
- Define every state in the API: default, hover, active, focus-visible, disabled, loading, error, selected. Missing states get improvised per screen [inference].
- Name by function and by the noun people already say (`SummaryList`, `WarningText`, `TaskList`), not by appearance (`YellowBox`); existing system inventories show the pattern [4].
- Pick one name per concept and list rejected synonyms in the docs; `Banner`, `Alert`, `Notice`, and `Callout` for one thing is four components in practice [inference].
- Documentation answers four questions: when to use it, when not to, what it replaces, and what it costs; do's, don'ts, and misuse examples teach more than a prop table [1][inference].
- Ship copy rules with the component ("labels are verb + object"), because wording failures get reported as component failures [inference].
- Document the accessibility contract: keyboard model, focus behaviour, required accessible name, announced states [inference].
- Keep docs and code in the same repository and the same release; a Figma-only library with no matching code is a mockup, not a system [1].

## Platform Convention And When To Break It

- Expectations come from the other products people use, not from your system [3].
- Use the platform control for the job: native select over a custom dropdown, native date input over a bespoke calendar, unless the native control cannot complete the task [3][inference].
- Deviate only with evidence: a measured task failure, a legal requirement, or a capability the convention cannot express [inference].
- When you deviate, keep an escape hatch and let people stay on the familiar pattern through a transition period [3].
- Consistency of meaning beats consistency of pixels: same word for the same thing everywhere, even if two screens then look slightly different [1][inference].
- Do not import another organisation's system wholesale and call it yours; adopt deliberately, adapt what differs, and document the divergence [1].

## Density And Theming Without Forking

- Model density as a mode (compact, default, comfortable) that changes spacing and control-height tokens, not as a second component set [inference].
- Keep the type scale stable across densities; shrinking type to fit more rows trades legibility for rows and breaks zoom [inference].
- Set a target-size floor per density: 24×24 CSS px everywhere, 44×44 on touch-first surfaces [inference].
- Theme through semantic tokens so one component tree serves light, dark, and brand themes; never fork a component per theme [inference].
- Test every theme for contrast and state visibility; a focus ring that works on white can vanish on a dark surface [inference].
- Let brands change palette and type, not layout grammar or interaction behaviour [inference].

## Contributing, Deprecating, Versioning

- Publish intake criteria: used in two products or twice in one, stable behaviour, accessible, and owned by a team [inference].
- Give every component an owner and a response time; unowned components accumulate stale issues and quiet forks [1].
- Deprecate in three steps: mark it in docs, warn at build time, remove it at a major version, with the replacement and a codemod published [inference].
- Version semantically: a breaking prop or markup change is major, a new variant is minor, a visual fix is patch [inference].
- Snapshot every component in every theme and state; visual regression is the cheapest guard against silent token drift [inference].
- Keep a changelog humans read, with migration notes, not commit titles [inference].
- Treat removal as a feature: a variant kept "just in case" costs documentation, tests, and every future decision [1].

## Audit An Existing System

- Count button implementations. Three or more means the system has stopped being used [inference].
- Grep for raw colour and spacing values outside token files; the count per directory is the real adoption metric [inference].
- List tokens with zero references; orphan tokens are decisions nobody made [inference].
- List components with one consumer; they are product code living in the system [inference].
- Compare the Figma library inventory with the code inventory; a gap means designers and engineers are building different products [1].
- Sample ten recent screens and count those using system components without overrides; under half means the system is optional in practice [inference].
- Ask three engineers to name the component for a described need; divergence predicts the next duplicate [inference].
- Audit states, not just components: how many document focus, error, and loading [inference].
- Start from the published inventory: USWDS lists 47 components, each described by the single need it solves; a system that cannot produce that list cannot be audited [5].
- Treat a "design system" that exists only as a Figma library as an audit finding, not a system: no tokens in code, no versioning, no parity with what ships [1].

## Sources

[1] [Design Systems 101](https://www.nngroup.com/articles/design-systems-101/) — Therese Fessenden, Nielsen Norman Group — accessed 2026-11-27 — supports: adopt/adapt/create cost spectrum, repository contents, naming, documentation, dedicated team and maintenance, Figma-versus-code library.
[2] [Design tokens](https://designsystem.digital.gov/design-tokens/) — U.S. Web Design System (GSA) — accessed 2026-11-27 — supports: discrete token sets versus continuous values, token as key and value, limited measure scale, token use in component code.
[3] [Jakob's Law](https://lawsofux.com/jakobs-law/) — Jon Yablonski, Laws of UX — accessed 2026-11-27 — supports: transferred expectations from other products, cost of discord, transition escape hatches.
[4] [Components](https://design-system.service.gov.uk/components/) — GOV.UK Design System — accessed 2026-11-27 — supports: reusable component inventory as the system's contract, composing components across patterns and contexts.
[5] [Components](https://designsystem.digital.gov/components/overview/) — U.S. Web Design System (GSA) — accessed 2026-11-27 — supports: published inventory of 47 components, one user-interface need per component, audit starting point.
