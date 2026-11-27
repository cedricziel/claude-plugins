# Onboarding and First Run

What a first-time user should see, how much of it to build, and how to tell whether the first run worked. Read this when designing a first launch, a signup or setup flow, an empty account, or a post-redesign announcement. The mechanics of unpopulated containers are in `errors-and-empty-states.md`; this file decides whether the first run needs a flow at all.

## Name the three jobs

- Separate first-run onboarding (a dedicated flow outside the normal interface), activation (the first real outcome the user produces), and help (reference material consulted later). Each has a different success test [1][2].
- Onboarding is not "teaching the interface". It is whatever is required to make the first real task possible, including setup and permissions [2].
- Treat onboarding as a cost to justify, not a feature to add: it consumes attention even when skipped, because dismissing it is still a click [2].
- Default to shipping no onboarding flow. Test the bare interface first; add a flow only where people demonstrably fail without one [2].
- Keep feature promotion out of first run and put it where people compare products; inside the app, mention a feature only once it becomes usable [2].
- Design for the person who skips. Users start working immediately rather than reading preparation material [1].
- Reserve a dedicated walkthrough for a genuinely novel interaction model, not for standard controls [1].

## The first screen proves three things

- Answer three questions above the fold: what this is, what it is for, what to do first [6].
- Name the product or service after the problem it solves, not the internal codename [6].
- Ship one primary button whose label names the action ("Start now", "Create your first project"), not two equal-weight calls to action [6].
- State cost, duration, and prerequisites before the start control: what it costs, roughly how long it takes, what the user needs at hand [6].
- List the documents or facts required, minus anything the user obviously knows from memory such as their own date of birth [6].
- Offer the alternate route where one exists (phone, paper form, import from an existing tool) instead of hiding it until the digital path fails [6].
- Defer eligibility questions into the flow, where they can be answered with the context of the question [6].
- Keep the start screen free of navigation, marketing carousels, and secondary sign-in prompts; a first screen with three competing exits is a fork, not a door [inference].

## Replace the tour: pull help on an empty state

- Delete the modal tour on first paint: it interrupts, is skipped, is forgotten, and does not improve task success [1][5].
- Expect no measurable gain even from people who read it — 91% task success with the tutorial against 94% without, with tutorial readers rating the task harder (4.92 against 5.49 on a 7-point ease scale) [5].
- Expect no speed gain either; completion times did not differ significantly [5].
- Trigger help from a signal that the user is at the moment of need — they opened the tool, added the first item — never from app launch [1].
- Keep each tip dismissible and re-findable in a fixed place such as a persistent "Tips" or "What's new" entry [1].
- Keep a tip to one sentence plus one action, with depth behind "Learn more" [1].
- Never make a multi-step procedure depend on remembered tutorial content; show the guidance beside the step it belongs to [1].
- Skip explanations of conventions (a gear means settings) and spend help only on what is unusual in this product [1].
- Prefer a real first task on sample data over an explanation of how that task would work [3].
- Design the empty state before any tour: it is the first screen most new accounts see, and an undesigned one reads as a bug [3].
- Have every empty container state what will live there, why it is currently empty, and how to fill it [3].
- Attach the create action to the empty state itself, plus one "Learn more" link for people who are unsure [3].
- Offer demo or sample content as a second path so people can explore without committing their own data [3].
- Never render "No records" while a request is still running; wait for the result, then report the state [3].
- Keep loading and empty visually distinct, so an empty list is never mistaken for a slow one [3].
- Do not illustrate an empty state without a sentence; the picture explains nothing on its own [3].

## Time the account, not the welcome

- Let people use as much of the product as possible before requiring an account [7].
- Do not add accounts when the service works without them; a reference number plus an email covers most one-off transactions [7].
- Gate only where the account is functionally required: saving across devices, identity or payment checks, or email-only recovery [7].
- Keep the account screen single-purpose — no marketing, no newsletter opt-in, no unrelated links [7].
- Separate "create an account" from "sign in" as distinct labelled paths, not two buttons side by side [7].
- Never ask for the same fact twice across signup and first-run setup [7].
- Do not default to CAPTCHA or other recognition tests as abuse control; they are a cognitive test that excludes people [7].
- If email confirmation is required, prefer the non-blocking loop so the user can keep working, and let them resend or correct the address [8].
- Send the activation mail immediately and state the address it went to; a delayed or unlabelled mail strands the user at a dead end [8].
- Provide a guest or skip path wherever the account is not required, as a visible link rather than buried body text [inference].
- Defer theme, branding, team, and notification choices until the choice has a visible consequence [4].
- Ask only for data that changes the first outcome; if you cannot say what it changes, ask later [2].

## Progressive onboarding and checklists

- Introduce capability in the order the work needs it, one disclosure level at a time; two levels is the practical ceiling before people get lost [4].
- Keep the first surface to what most users need on most sessions, with everything else one clearly labelled step away [4].
- Show a checklist only when its items are finite, ordered, and required for the user's own goal [inference].
- Cap it at about five items, show progress and a completed state, and let items be dismissed rather than only ticked [inference].
- Collapse or remove the checklist once complete; a permanent "1 of 5 done" panel becomes furniture, then noise [inference].
- Only include items the product can verify. Manually ticked items that stay unticked read as personal failure [inference].
- Complete checklist items from the real action, not from clicking "Next" in a tutorial [2].

## Pick one activation event

- Define activation as a user-visible outcome (first report sent, first invoice paid), never a UI milestone such as a completed tour or filled profile [9].
- Measure time to value from first arrival to that outcome and treat the number as a cost to reduce [9].
- Choose the event by comparing what users who stayed did early against what users who left did, then take the earliest action that separates them [9].
- Instrument the funnel in steps — arrival, account, first task started, first task finished — so a drop is attributable rather than aggregate [9].
- Set the bar at a real outcome, not a session. A first session with no outcome is a failed first run even when engagement looks healthy [inference].
- Report activation rate and time to value together; fast-but-rare activation is a different problem from slow-but-common activation [inference].
- Re-derive the event after a redesign; the old milestone may no longer exist in the flow [9].

## Re-onboarding after change

- Re-onboard on change, not only at signup: existing users need the same treatment when a feature, layout, or permission model moves [1][2].
- Announce the change where it affects the user's task, not at login, and keep the announcement recallable [1].
- Mark the moved control in place rather than describing the whole redesign in prose [1].
- Keep a persistent changelog so a dismissed announcement can be found again later [1].
- When a role, permission, or plan changes, run the first-screen frame again: what you can do now, what changed, what to do first [inference].
- Re-walk the first-run path whenever onboarding copy or a permission model changes; a tour pointing at a removed control is worse than no tour [inference].

## Failure modes and the first paint

| Failure                        | What the user meets                        | Replacement                                      |
| ------------------------------ | ------------------------------------------ | ------------------------------------------------ |
| Modal tour on first paint      | A deck of cards before any content         | Help at the moment of need [1]                   |
| Blocking setup wizard          | No product until configuration is done     | Sensible defaults, configure later [4]           |
| Checklist that never completes | "1 of 5" for weeks                         | Drop optional items, allow dismissal [inference] |
| Tutorial teaching the UI       | "Click the gear to open settings"          | Explain the task, not the chrome [5]             |
| Account wall before any value  | Signup before seeing what the product does | Guest path, gate at save [7]                     |

- Move focus deliberately on first load — to the page heading or the first required control — and never trap it in an overlay [10].
- Do not change context on focus: no auto-opening help dialog and no auto-submit when a field receives focus [10].
- Make every instruction available as text, not motion alone; a gesture animation needs a written equivalent [inference].
- Caption and transcribe any onboarding video, and never autoplay it with sound [inference].
- Put the skip control first in the focus order so a keyboard user is never trapped in the flow [inference].
- Check the first screen at 200% zoom and with a screen reader: one clear heading, one announced action [inference].

## Sources

[1] [Onboarding Tutorials vs. Contextual Help](https://www.nngroup.com/articles/onboarding-tutorials/) — Page Laubheimer, Nielsen Norman Group — accessed 2026-11-27 — supports: push versus pull revelation, tours skipped and forgotten, dismiss-and-recall, memorisation, skipping conventions, re-onboarding on change.
[2] [Mobile-App Onboarding: An Analysis of Components and Techniques](https://www.nngroup.com/articles/mobile-app-onboarding/) — Alita Kendrick, Nielsen Norman Group — accessed 2026-11-27 — supports: definition of onboarding, skip it when possible, interaction cost, feature promotion, customisation timing, interactive walkthroughs, onboarding existing users.
[3] [Designing Empty States in Complex Applications: 3 Guidelines](https://www.nngroup.com/articles/empty-state-interface-design/) — Kate Kaplan, Nielsen Norman Group — accessed 2026-11-27 — supports: system status, learning cues, direct pathways, demo data, never showing a premature no-records message.
[4] [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: deferring secondary options, splitting initial from advanced, two-level ceiling, default configuration.
[5] [Mobile Tutorials: Wasted Effort or Efficiency Boost?](https://www.nngroup.com/articles/mobile-tutorials/) — Alita Kendrick, Nielsen Norman Group — accessed 2026-11-27 — supports: the 91% vs 94% success result, the 4.92 vs 5.49 ease rating, no significant time difference, teaching the UI rather than the task.
[6] [Start using a service](https://design-system.service.gov.uk/patterns/start-using-a-service/) — GOV.UK Design System team — accessed 2026-11-27 — supports: naming after the problem, one start button, cost and duration, what the user will need, alternate channels, eligibility inside the service.
[7] [Create accounts](https://design-system.service.gov.uk/patterns/create-accounts/) — GOV.UK Design System team — accessed 2026-11-27 — supports: accounts as a barrier, use before account, single-purpose signup screen, no duplicate entry, no CAPTCHA, distinguishing create from sign in.
[8] [Confirm an email address](https://design-system.service.gov.uk/patterns/confirm-an-email-address/) — GOV.UK Design System team — accessed 2026-11-27 — supports: blocking versus non-blocking confirmation loops, sending immediately, resending and correcting the address, disruption of leaving the service.
[9] [Product-Led Growth and UX](https://www.nngroup.com/articles/product-led-growth-ux/) — Sara Paul, Nielsen Norman Group — accessed 2026-11-27 — supports: definition of time to value, minimising it, removing login walls, only required steps, reading early behaviour of users who converted.
[10] [Understanding SC 3.2.1: On Focus](https://www.w3.org/WAI/WCAG22/Understanding/on-focus.html) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: no change of context on focus, the help-dialog failure case, predictable first-paint focus behaviour.
