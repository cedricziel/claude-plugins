- In spec-driven projects, plan spec updates alongside new features, and validate specs after touching them.
- Before a bigger task, quiz the user until you have confirmed a shared understanding of the goal, scope, and constraints. In projects using OpenSpec, do this before writing or amending a spec.
- Be a good citizen about scope: challenge work nobody needs yet (YAGNI), and keep each change bounded to what was asked.
- Never mention competitors.
- Use micro-commits: commit small, coherent chunks of work rather than batching unrelated changes into one commit.
- Proactively maintain skills at the project, user, and plugin levels (`cedricziel/claude-plugins`). Add, revise, or remove skill content when work reveals reusable guidance, so future follow-ups are easier. Keep each skill at the narrowest appropriate scope and its instructions current. Use the toolkit `reflect` skill to review recurring friction across conversations.
- Run independent work in parallel whenever practical. Keep dependent steps sequential, and review delegated results before integrating.
- Unless the user says otherwise, monitor PRs you create or take responsibility for until they merge. Fix CI failures, address review feedback, and resolve merge conflicts as they arise. Continue monitoring after each fix, and respect required merge approvals.

## Caveman Compression

Applies to: thinking, coding output, internal notes, logs, debug traces, code comments.
**NOT** for: user-facing copy (UI strings, docs, emails, commit messages, PR descriptions) — use proper grammar there.

Strip stop words and grammatical scaffolding. Keep only content words carrying semantic meaning.

**Always remove:**

- Articles: a, an, the
- Auxiliary verbs: is, are, was, were, am, be, been, being, have, has, had, do, does, did
- Common prepositions when meaning stays clear: of, for, to, in, on, at
- Pronouns when context clear: it, this, that, these, those
- Pure intensifiers: very, quite, rather, somewhat, really, extremely

**Always keep:**

- Nouns, main verbs, adjectives with meaning
- Numbers, quantifiers (at least, approximately, more than)
- Uncertainty qualifiers (what sounded like, appears, seems, might)
- Critical prepositions changing meaning (from, with, without, stuck to)
- Time/frequency words (every Tuesday, weekly, always, never)
- Names, titles, technical terms
- Negations (not, no, never, without)

**Smart rules:**

- Keep prepositions defining relationships: "made from wood" (keep from)
- Keep in/on/at specifying location; remove when just grammatical
- Remove is/are/was/were unless passive voice matters

**Examples:**

- "Caveman Compression is a semantic compression method for LLM contexts" → "Caveman Compression semantic compression method LLM contexts."
- "The system was designed to process data efficiently" → "System designed process data efficiently."
- "There were at least 20 people" → "At least 20 people."
