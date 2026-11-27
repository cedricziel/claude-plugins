# Feedback and Status

This file answers one question: what should the interface do between a user's action and its result? Read it when designing or reviewing async operations — saves, uploads, payments, search, background jobs — and anything that can be slow, fail after a delay, or change state while the user watches. `forms.md` covers input structure and validation; this file covers time, waiting, confirmation, and the states of async controls.

## The three response-time limits

| Wait      | What the user experiences                                  | Required feedback                      |
| --------- | ---------------------------------------------------------- | -------------------------------------- |
| 0–0.1 s   | Direct manipulation; the result feels caused by the action | Result only                            |
| 0.1–1 s   | Flow intact, delay noticed                                 | Visible state change; no spinner       |
| 1–10 s    | Attention held, work feels slow                            | Indicator plus text naming the work    |
| Over 10 s | Attention lost; user starts another task                   | Determinate progress, estimate, cancel |

Limits and required behaviour from Nielsen's response-time thresholds [1].

- Under 0.1 s, show only the result. Extra feedback at this speed is noise the user cannot process [1].
- Between 0.1 s and 1 s, keep the interaction moving with a state change and no spinner; a flash of spinner reads as a glitch [1][2].
- Past 1 s, show that work is happening, near the thing that is working [1][2].
- At 10 s, add a percent-done indicator and a visible way to interrupt; assume the user will reorient on return [1].
- Design for variance, not the mean. If a call is usually 1 s but sometimes 20 s, the design must handle 20 s [1].
- Never let a wait end in silence: completion must produce a visible change in the control or the page [inference].

## Acknowledge the action immediately

- Every activation produces a visible change within about 100 ms: pressed state, label change, row inserted, checkbox ticked [2].
- Put pending state on the control itself ("Saving…" inside the button), keep its width fixed, and block a second submit at the source [2].
- Do not use "do not click twice" warnings. Users do not read them, and the warning admits the interface failed to acknowledge the first click [3].
- If work continues after navigation, show it where the user now is ("3 files uploading" in the header), not only on the page they left [inference].
- Duplicate-submit protection belongs on the server too; a disabled button is not idempotency [inference].

## Optimistic and confirmed updates

- Update optimistically only for reversible, local, cheap-to-roll-back changes: toggles, likes, reordering, draft text [inference].
- Confirm before commit for money, deletion, permission changes, and anything the server can reject for a reason the user must fix [inference].
- An optimistic update needs a visible rollback: revert the control and say what failed. A silent revert teaches users the UI lies [2].
- Say "Saved" only after the server confirms. Before that say "Saving…"; on failure say "Not saved" and offer retry [inference].
- Never report a queued or offline write as done. Say "Queued — will sync when online" and show the pending state until it clears [inference].

## Progress indicators

- Use determinate progress when the total is known or countable: "Updating address 3 of 50". Reserve it for 10 s+, or for record-processing jobs that finish sooner [3].
- Use an indeterminate loop (spinner or looping bar) only for roughly 2–10 s. Under 1 s it is flashing noise; past 10 s it reads as stuck [3][4].
- Any indeterminate wait likely to exceed 10 s needs text ("Still importing…") and an exit, not an endless spinner [3].
- Start progress slow and let it accelerate. A bar that races to 99% and stalls destroys the reassurance it was meant to give [3].
- Static "Loading…" text is not a progress indicator. If the process hangs, the user cannot tell it apart from a crash [3].
- Show progress next to the element being updated, not only in a global corner the user is not looking at [inference].

## Perceived performance and motion

- Use a skeleton screen only for a full-page load expected under 10 s; use a spinner for one module (a card, a video), and a progress bar for a process such as upload or export [4].
- Never ship a frame-only skeleton (header, footer, blank body). It is a spinner with extra markup and gives no structural expectation [4].
- Match the skeleton to the final layout. A skeleton that predicts the wrong block sizes turns content arrival into a jarring reflow [4][inference].
- Treat a shimmer as motion: keep it subtle, and disable it under reduced-motion preferences [4][5].
- Skeletons buy tolerance, not speed. Fix the request before polishing the placeholder; the article is explicit that they do not replace performance work [4].
- Paint the shell and above-the-fold content first, then stage the rest, so the first paint carries real information [inference].
- Accept the limit: no indicator makes a 30 s wait acceptable. Reduce the work, cache it, or move it off the critical path [inference].

### Motion for state changes

- Use about 100 ms for simple feedback (toggle, checkmark), 200–300 ms for a modal or sheet entering, and treat 400 ms as the practical ceiling [5].
- Make exits slightly faster than entrances, so the UI feels like it is keeping up [5].
- Use ease-out on enter and ease-in on exit. Linear motion reads as mechanical [5].
- Animate opacity, position, scale, and colour sparingly; drop full-screen sweeps for actions users repeat often [5].
- Respect `prefers-reduced-motion`: remove non-essential motion and keep the state change itself [5].
- Motion must never delay the result. A 300 ms transition on every list row compounds into seconds [inference].

## Confirmation and notification hierarchy

- Field-level problem: inline message. Action-level failure: alert or summary near the action. Completed transaction: page-level confirmation stating the outcome [6][7].
- Use a toast only for passive, low-stakes information. Never use one for an error that requires action [6].
- An auto-dismissing error toast can cost minutes: one user waited five minutes for content because the failure notice had faded after five seconds [6].
- Action-required messages should be intrusive and persistent, dismissed by an explicit act; passive messages can be a badge or non-modal popover [6].
- Place confirmation near the control that caused it. A banner at the top of a long page is routinely missed [6].
- Do not confirm what the user can already see. Per-keystroke "Draft saved" toasts train dismissal [inference].
- A confirmation nobody reads is worse than none: it adds noise and teaches users to close messages unread [inference].
- State completion in words, not only a checkmark or a colour [7]; add what happens next and a reference the user can quote [inference].

## Every async control has four states

- Specify idle, pending, success, and error for each async control, not just the happy path [inference].
- Pending: change the label, set `aria-busy="true"`, block repeat submission, and keep the control's size stable [inference].
- Error: persistent, actionable, next to the control, with retry. Never only a toast [6].
- Success: acknowledge briefly, then return the control to idle showing the new value [inference].
- Disabled is not a loading state. It hides the reason and removes the control from keyboard and screen-reader reach [inference].
- On timeout, say the request timed out, keep the entered data, and offer retry rather than silently reverting [inference].
- Offline or queued writes need their own visible state and a clear point at which they become final [inference].

## Live updates and focus

- Use `aria-live="polite"` for status text ("Saved", "12 results"); reserve `assertive` for errors that must interrupt [7].
- Announce result counts and state changes in text, not only through a spinner, colour, or icon [7].
- On validation failure, move focus to the summary or the first field in error [7].
- After async navigation, move focus to the new `h1` or a skip target; never leave focus on a node that was removed [inference].
- Keep the live region mounted before updating it. Replacing the node usually prevents the announcement [inference].
- Do not announce every poll or refresh; throttle and announce only meaningful changes [inference].
- Pair reduced-motion support with a text status so users who disable animation still get the update [5].

## Sources

[1] [Response Times: The 3 Important Limits](https://www.nngroup.com/articles/response-times-3-important-limits/) — Jakob Nielsen, Nielsen Norman Group — accessed 2026-11-27 — supports: the 0.1 s, 1 s, and 10 s limits and the interaction contract at each, percent-done for 10 s+, interrupt paths, feedback when response times vary.

[2] [Visibility of System Status (Usability Heuristic #1)](https://www.nngroup.com/articles/visibility-system-status/) — Aurora Harley, Nielsen Norman Group — accessed 2026-11-27 — supports: immediate acknowledgement, state changes preventing repeat clicks, trust through explicit status, explaining state changes rather than letting items disappear.

[3] [Progress Indicators Make a Slow System Less Insufferable](https://www.nngroup.com/articles/progress-indicators/) — Katie Sherwin, Nielsen Norman Group — accessed 2026-11-27 — supports: indicators past 1 s, looped animation for 2–10 s, percent-done for 10 s+, text explanations, cancel options, slow-fast progress, static indicators, no "do not click twice" warnings.

[4] [Skeleton Screens 101](https://www.nngroup.com/articles/skeleton-screens/) — Samhita Tankala, Nielsen Norman Group — accessed 2026-11-27 — supports: skeleton screens under 10 s, spinners for single modules, progress bars for processes, no frame-only skeletons, animation distraction, skeletons not replacing performance work.

[5] [Executing UX Animations: Duration and Motion Characteristics](https://www.nngroup.com/articles/animation-duration/) — Page Laubheimer, Nielsen Norman Group — accessed 2026-11-27 — supports: 100 ms simple feedback, 200–300 ms screen changes, 400–500 ms ceiling, faster exits, ease-out/ease-in, linear motion, reduced-motion, frequent animations being shorter.

[6] [Indicators, Validations, and Notifications: Pick the Correct Communication Option](https://www.nngroup.com/articles/indicators-validations-notifications/) — Kim Flaherty, Nielsen Norman Group — accessed 2026-11-27 — supports: indicator versus validation versus notification, action-required versus passive messages, toasts unsuitable for errors, the five-second error that cost five minutes, confirmations missed when placed away from focus.

[7] [User Notification](https://www.w3.org/WAI/tutorials/forms/notifications/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: overall versus inline feedback, success messaging, focus to the first field in error, `aria-live="polite"` during typing versus `assertive` on focus change.
