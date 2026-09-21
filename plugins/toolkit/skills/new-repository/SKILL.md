---
name: new-repository
description: Set up a new GitHub repository the way Cedric usually does — repo settings, CI, semantic PR titles, release-please, Dependabot, CLAUDE.md, and the Claude plugin pin with its auto-update workflow and cloud-session install hook. TRIGGER ONLY on /new-repository <name>, or an explicit ask to create/bootstrap/set up a new repo. DO NOT trigger for editing an existing repo, or for a bare "create a project" that doesn't ask for the repo setup.
---

# /new-repository

```
/new-repository my-project                 # creates cedricziel/my-project, public
/new-repository my-project --private
/new-repository existing-repo --adopt      # apply the setup to a repo that already exists
```

Creating a repo and changing its settings are outward-facing. Confirm name, owner, visibility, and language before the first `gh repo create` or `gh api -X PATCH/PUT`. Everything else lands as a commit.

## 1. Create

```bash
gh repo create cedricziel/<name> --public --clone --add-readme --license mit
```

`--adopt` skips this step. Default branch is `main`.

## 2. Repo settings

```bash
gh repo edit cedricziel/<name> --enable-auto-merge --delete-branch-on-merge \
  --enable-squash-merge --enable-merge-commit=false --enable-rebase-merge=false
gh api -X PUT repos/cedricziel/<name>/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true
```

The second call lets Actions open PRs, which the plugin-update workflow needs. Then require the CI check on `main` with a ruleset, so auto-merge waits for it instead of merging immediately. If a step is denied, stop and tell the user which setting is missing rather than working around it.

## 3. Files

Adapt each to the repo's language; keep them minimal.

**Pin every third-party action to a full commit SHA**, with the release as a trailing comment (`uses: actions/checkout@<40-char sha> # v7.0.1`). Tags and branches can be retargeted, and these workflows run with write tokens. Resolve the SHA with `gh api repos/<owner>/<action>/git/ref/tags/<tag> --jq .object.sha` (dereference again if the object type is `tag`). The `github-actions` entry in Dependabot keeps the pins current. The one exception is `cedricziel/claude-plugins/actions/update-plugin@main`: it's first-party and tracks `main` on purpose.

| File | What |
| --- | --- |
| `.github/workflows/ci.yml` | Build, lint, test for the stack. This is the required check. |
| `.github/workflows/lint-pr.yml` | `amannn/action-semantic-pull-request@v6` on `pull_request_target` (opened, edited, synchronize, reopened), `permissions: pull-requests: read`. Titles follow the commit format. |
| `.github/workflows/release-please.yml` | `googleapis/release-please-action@v5` on push to `main`, `permissions: contents: write, pull-requests: write`, `token: ${{ secrets.RELEASE_PLEASE_TOKEN \|\| secrets.GITHUB_TOKEN }}`. Set `release-type` for the stack (`rust`, `node`, `dart`, `simple`). Tell the user to add the `RELEASE_PLEASE_TOKEN` PAT secret: a PR opened by `GITHUB_TOKEN` doesn't trigger CI, so the release PR would merge ungated. |
| `.github/dependabot.yml` | `version: 2`; one entry for the language's ecosystem and one for `github-actions`, both `directory: "/"`, `interval: daily`, `assignees: [cedricziel]`. |
| `CLAUDE.md` | Build/test/lint commands, layout in a few lines, and repo-specific rules. Nothing generic — the plugins already carry that. |
| `.gitignore` | Language standard. Do not ignore `.claude/settings.json` or `.claude/hooks/`. |

## 4. Claude plugins

Enable `oss` unless the user names others (`toolkit` is the personal layer; ask before adding it to a repo other people use).

```yaml
# .github/workflows/update-claude-plugins.yml
name: Update Claude plugins
on:
  schedule:
    - cron: "0 6 * * 1"
  workflow_dispatch:
permissions:
  contents: write
  pull-requests: write
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: cedricziel/claude-plugins/actions/update-plugin@main
        with:
          plugins: oss
```

Then run it once so the action bootstraps the config rather than hand-writing it:

```bash
git add .github && git commit -m "chore(ci): add workflow to keep Claude plugins up to date" && git push
gh workflow run update-claude-plugins.yml
```

Once merged, the first run creates `.claude/settings.json` (marketplace pinned to the latest commit, `oss` enabled) and `.claude/hooks/install-claude-plugins.sh`, registered as a `SessionStart` hook that installs the plugins in cloud sessions. The action opens a PR with auto-merge on. Pass `session-hook: "false"` to skip the hook.

## 5. Report

List what was created, which settings changed, and what the user still owes: the `RELEASE_PLEASE_TOKEN` secret, the required-check ruleset if it couldn't be created, and merging the first plugin-update PR.
