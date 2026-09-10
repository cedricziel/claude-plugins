# Release notes: gathering inputs

Commands for the Procedure in `SKILL.md`. Verified against the gh manual and
a real repo; adapt owner, repo, tag names and paths.

## Previous tag

```bash
git describe --tags --match 'writer-v*' --abbrev=0 TAG^   # component-prefixed monorepo tags
git describe --tags --abbrev=0 TAG^                       # plain tags
```

Fall back to `gh release list --json tagName,publishedAt` only when the
previous release is not an ancestor of the tag.

## PR numbers in the range

Merge commits on the first-parent line carry the PR number. Scope to the
component's paths when the release is path-scoped; drop the path otherwise.

```bash
git log --first-parent --format='%s' PREV..TAG -- src/component | grep -oE '#[0-9]+' | tr -d '#'
```

A subject can carry two refs, `fix(x): ... (#921) (#980)`: the first is the
issue the author mentioned, the last is the PR. `gh pr view` returns 404 for
an issue number, which settles it.

## PR details, for exactly that set

```bash
for n in $(cat numbers.txt); do
  gh pr view "$n" --json number,title,body,labels,closingIssuesReferences
done > prs.json
```

When the range has no usable first-parent line, a date window is the
alternative; it is repo-wide, so filter it to the scoped numbers before
reading bodies:

```bash
gh pr list --state merged --base main --search "merged:2026-08-01..2026-08-17" \
  --limit 200 --json number,title,body,labels,closingIssuesReferences
```

Optional cross-check when the repo has `.github/release.yml` or the ledger's
count looks off. It is repo-wide too:

```bash
gh api repos/OWNER/REPO/releases/generate-notes \
  -f tag_name=TAG -f previous_tag_name=PREV --jq .body
```

## Breaking-change markers

```bash
git log --format='%h %s' PREV..TAG | grep -E '^[0-9a-f]+ [a-z]+(\([^)]*\))?!:'
git log --format='%h %s%n%b' PREV..TAG | grep -B1 -A3 'BREAKING CHANGE'
gh pr list --state merged --label breaking --json number,title
```

A `!` marker or footer is a candidate for Before you upgrade, not proof. Read
the diff for the actual reader-facing action.

## Ledger template

Keep it in a scratch file, not in the notes.

```
#1204  one signaldb binary; per-service binaries removed        upgrade
#1020  orphan cleanup re-validates before delete                fixed
#1006  forbid log:: macros                                      omit (internal)
#845   bump docker/login-action                                 omit (deps)
```

Past about 50 PRs, group the ledger by destination (upgrade, highlight, tail
by area, omit by reason) so the cut order in `SKILL.md` can be applied per
group.

## Reading and editing the published release

```bash
gh release view TAG --json body --jq .body
gh release edit TAG --notes-file notes.md
```

The generated section stays useful as the audit trail; put the curated notes
above it or replace it, as the project prefers.
