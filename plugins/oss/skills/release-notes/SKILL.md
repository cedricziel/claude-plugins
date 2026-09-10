---
name: release-notes
description: Use when drafting, rewriting, or reviewing release notes or a changelog entry for a GitHub release or tag, when an auto-generated or release-please release body needs to become readable, or when asked what changed between two versions for the people who use the software.
---

# Release notes

A release note answers one question for someone deciding whether and how to
upgrade: what changes for me, and what do I have to do. The commit list already
exists behind the compare link. The notes are the curated layer above it, and
their value is in what they leave out.

## The output

Sections in this order. Drop a section that would be empty. Never add one.

1. **Version and date.** Date in ISO 8601.
2. **Summary.** At most 40 words on what this release is about. Skip it for
   a patch release with no theme. It names the theme, not the list; the size
   of the release and the effort behind it never appear.
3. **Before you upgrade.** In a `> [!WARNING]` callout. Breaking changes,
   removed or renamed flags, config keys and endpoints, defaults that now
   behave differently, security fixes with the advisory ID, deprecations. Each
   item: what changed, the exact action the reader takes, the PR ref.
4. **Highlights.** One to five items. Each describes exactly one PR, not a
   theme spanning several, in at most 50 words of prose with a bold lead-in:
   the situation or problem, what the reader can now do, where it lives
   (flag, config key, endpoint, UI tab, subcommand), release stage inline as
   (beta) or (GA). That PR's ref closes the item. A lead-in that needs "and"
   is two changes: keep the bigger one, send the other to the tail. A theme
   belongs in the summary.
5. **Added / Changed / Fixed.** The long tail. One bullet per change, verb
   first, at most 30 words, PR ref at the end. Add **Performance** only when
   a bullet carries a measured number.
6. **Full changelog.** The compare link, once, here.

## Budget

The ceilings, whatever the size of the range: Before you upgrade holds every
item that qualifies; Highlights five; the tail 25 bullets across Added,
Changed and Fixed together. A patch release fits in ten bullets total. Area
subheadings inside the tail are for scanning, never for room.

A large range does not raise the ceilings. It raises the bar. When the tail
is over, cut in this order until it fits:

1. Changed bullets the reader would not notice without reading the code.
2. Fixed bullets for a bug nobody reported.
3. Sibling bullets in one area merged into one, with one ref.
4. Any tail bullet that is a smaller facet of a highlight.

Cut only once Highlights are final: a bullet dropped as a facet of a
highlight returns to the tail when that highlight narrows.

## Where a change goes

| The change… | Goes to |
|---|---|
| changes what the reader must do to upgrade, or flips a default they rely on | Before you upgrade |
| fixes a security issue | Before you upgrade, with the advisory ID |
| lets the reader do something new they would notice | Highlights, or Added when it is small |
| alters behavior the reader notices without reading the code | Changed |
| tunes internals (allocator, index sizing, planner settings, generated code) | omit, or Performance when measured |
| stops a wrong behavior the reader could have hit | Fixed |
| is measurably faster and the number is known | Performance, with the number |
| is faster but nobody measured it | Changed, or omit |
| bumps a dependency | omit, unless it changes a runtime or platform requirement or fixes a CVE |
| is a refactor, test, CI, style, build-internals or docs-only change | omit; a new doc is linked from the bullet it supports |
| is tooling only contributors touch | omit |

A ledger (below) is what makes an omission deliberate instead of accidental.

## Writing a line

- Lead with the outcome for the reader, then the mechanism if it earns a
  clause. "Queries against a dataset with no table return empty instead of
  failing" beats "Add table reconciler".
- Name the concrete thing that changed. A flag, key, endpoint, tab or
  subcommand, not "the query layer".
- Present tense. Second person or imperative. No "we're excited", no
  superlatives, no "various fixes", no "improvements" without an example.
- Describe what the reader sees, never how it was built. A line that only
  makes sense with the code open is rewritten around the effect, or dropped.
- One PR ref per line, at the end, as `(#123)`. A feature spanning PRs cites
  its umbrella issue or the last PR. Never a run of refs.
- Each change appears once. A change that is a highlight has no tail line,
  and a highlight cites the PR that made it, not a neighbor.
- No commit-type prefixes in prose. `fix(compactor)!:` is input, not output.

## Procedure

1. **Scope.** Find the previous tag, fix the ref range, and decide which
   artifact the notes describe. In a monorepo the generated body is scoped to
   the component's paths; say whether the notes cover the component or the
   whole product.
2. **Gather.** The PR numbers in range, then each PR's body, labels and
   closing issues. Commands in `reference.md`. Read the bodies. The title is
   the author's summary of the diff; the body says why it matters and what it
   breaks.
3. **Ledger.** One row per PR: number, user impact in a phrase, destination
   from the table above. Every PR gets a row. The ledger stays out of the
   notes.
4. **Draft** to the output shape.
5. **Gates**, in order, all required:
   - **Grounding.** Every line traces to a ledger row. Every action in
     Before you upgrade was checked against the diff or the docs, not
     inferred from a title.
   - **Unslop.** Run `common:unslop` over the draft. Its pattern scan
     applies; where its advice to add first-person voice or opinion collides
     with the line rules above, the line rules win.
   - **Publish only when asked.** Show the draft. On an explicit go, edit the
     published release with `gh release edit`. With release-please, never
     edit the release PR body; it is regenerated on every push.

## Example

Before, from a generated body:

```text
* feat: one signaldb binary with the services as subcommands (#1204)
* fix(compactor)!: re-validate unconditionally before deleting orphans (#1020)
* refactor(logging): forbid log:: macros in favor of tracing:: (#1006)
```

After:

```markdown
> [!WARNING]
> **The per-service binaries are gone.** `acceptor`, `router`, `writer`,
> `querier` and `compactor` are subcommands of one `signaldb` binary. Update
> service units and container commands: `acceptor` becomes
> `signaldb acceptor`. (#1204)

### Fixed
- Orphan cleanup re-checks every candidate file against the current table
  metadata before deleting it, instead of trusting an earlier scan. (#1020)
```

The refactor line is omitted.
