Be brief.

- Use semantic commits (see the commit-discipline skill). Split messages that need "and".
- Delegation models: `sonnet` for working (search, implement, verify, mechanical steps), `opus` for thinking (decisions, reviews, synthesis). Use `fable` only when explicitly asked.
- Use context7 for library docs.
- For large changes, use the git-stacked-prs skill.
- Keep PRs under 500 lines changed; split larger work into a stack.
- After opening a PR, check for automated reviews (e.g. CodeRabbit) and act on their findings to keep review cycle time low.
- Track your work as todos.
- Practice TDD: failing test first. Before commit: run the project's lint/format (see its CLAUDE.md or pre-commit hooks), then invoke `/simplify`.
- Default no code comment; see the code-comments skill for when one earns its place.
- Subagents inherit these instructions, the project CLAUDE.md and memory — but a task prompt that spells out its own checklist overrides them in practice, so any checklist you write must be complete (naming lint/format and `/simplify`) or be left out. For multi-agent work, read `{{FLEET_BRIEF}}` and hand it to them instead of improvising one.
- In spec-driven projects, plan spec updates alongside new features, and validate specs after touching them.
- Never mention competitors.

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
