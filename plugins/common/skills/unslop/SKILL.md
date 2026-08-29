---
name: unslop
description: >
  Strips AI-generated "slop" tells from user-facing prose — docs, README sections,
  PR/issue descriptions, commit message bodies, code comments meant for humans, chat
  replies. Complements (does not replace) Caveman Compression, which governs the
  internal register (thinking, logs, debug traces) instead. Use proactively before
  finishing any user-facing writing, or when asked to "clean this up", "make it sound
  less AI", "tighten this doc", or similar. Triggers on: drafting a README/PR
  description, writing a commit body, editing docs, or a request to de-slop text.
---

# Unslop

Rewrite user-facing text to read like a careful engineer wrote it, not a model.

## Always cut

- **Throat-clearing openers/closers**: "Great question!", "Let's dive in", "I hope
  this helps!", "In conclusion", "To summarize" — say the thing, skip the frame.
- **False-emphasis constructions**: "It's not just X, it's Y", "This isn't about X —
  it's about Y". State the point once, plainly.
- **Padding qualifiers**: "It's worth noting that", "It's important to remember",
  "Essentially", "Basically", "In today's fast-paced world".
- **Corporate/marketing filler words**: leverage, utilize, seamless, robust,
  cutting-edge, game-changer, unlock, elevate, empower — use the plain verb (use,
  enable, improve) or cut the sentence.
- **Rule-of-three padding**: lists stretched to exactly three items when one or two
  say it fully. Cut the weakest item rather than inventing a third.
- **Over-hedging**: stacking "might potentially perhaps" — pick one honest qualifier
  or state it directly.
- **Decorative em dashes**: an em dash used as a stylistic tic rather than to set off
  a real aside. Replace with a period, comma, or colon; keep it only when it's doing
  real syntactic work.
- **Needless bullet-ification**: turning two related sentences into a bulleted list
  for no structural reason. Prose reads faster when the content doesn't need a list.

## Always keep

- Concrete nouns, numbers, names, and technical terms.
- The actual claim or instruction — cutting slop must never cut information.
- Structure (lists, tables, headers) when the content genuinely has parallel items
  or steps, not by default.

## How to apply

1. Read the passage once for what it actually says.
2. Rewrite it in the fewest words that say the same thing, in normal grammatical
   prose (unlike Caveman Compression, keep articles and function words — this is
   still copy other people read).
3. Diff mentally against the "always cut" list above; remove anything that survived
   only as filler.
4. Read it aloud once. If a sentence sounds like it's performing confidence rather
   than stating a fact, cut the performance.

## Scope note

This skill is for text a human reads as a deliverable: READMEs, docs, PR/issue
bodies, commit message bodies, user-facing comments, chat replies. For your own
thinking, logs, debug traces, and internal code comments, use Caveman Compression
instead (`instructions/global.md` in the `toolkit` plugin) — that register drops
grammar entirely rather than just slop.
