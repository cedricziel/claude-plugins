---
name: forgejo-cli
description: "How to use the Forgejo CLI (`fj` — forgejo-contrib/forgejo-cli) to work with Forgejo/Codeberg instances from the terminal, the same way `gh` works for GitHub. Use whenever a task involves a Forgejo/Codeberg repo, issue, pull request, release, tag, or Actions workflow — cloning, viewing, creating, searching, merging, dispatching — or authenticating against a Forgejo host. Triggers on: \"fj\", \"forgejo\", \"codeberg\", a `code.*`/`git.*` host that runs Forgejo, or a git remote pointing at a Forgejo instance."
---

# Forgejo CLI (`fj`)

`fj` is the Forgejo/Codeberg equivalent of `gh`. Binary is **`fj`** (not `forgejo-cli`).
Homebrew: `brew install forgejo-cli`. Source: https://codeberg.org/forgejo-contrib/forgejo-cli.

## Golden rules

- **Command shape:** `fj <group> <command> [ARGS] [OPTIONS]` — groups are `repo`, `issue`, `pr`, `wiki`, `actions`, `release`, `tag`, `user`, `org`, `auth`, `whoami`.
- **`-H, --host <HOST>`** selects the instance (e.g. `-H codeberg.org`). If only one instance is configured `fj` usually infers it; when inside a repo it infers host+repo from the git remote. **When a command errors with "not found" or picks the wrong instance, add `-H <host>` explicitly.**
- **Repo argument format is `owner/repo`** (e.g. `owner/repo`), NOT a URL. Many commands also accept `-r/--repo <owner/repo>` or infer the repo from the current git remote (`-R/--remote <name>`).
- **`-C, --cwd <DIR>`** runs as if in another directory — useful to target a checkout without `cd`.
- Bodies for issues/PRs open `$EDITOR` if omitted. For non-interactive use pass `--body "..."` or `--body-file <file>`. **Always pass `--body` in scripts/automation** so it never blocks on an editor.

## Auth

```bash
fj auth login   -H <host>          # browser OAuth — only if the instance has an OAuth app configured
fj auth add-token -H <host> [TOKEN] # token flow; reads TOKEN from stdin if omitted
fj auth list                       # show configured instances
fj auth logout  -H <host>
fj whoami       -H <host>          # verify: "currently signed into <user>@<host>"
```

- **Many self-hosted instances don't support `fj auth login`** (no OAuth app). It falls back with: *"your installation doesn't support login… create a token at `https://<host>/user/settings/applications`"*. Use `fj auth add-token` instead.
- Create the token at `https://<host>/user/settings/applications`. Scopes: for general CLI use `read:repository`, `write:repository`, `read:user` (or `all`).
- Feed the token via stdin so it doesn't linger in shell history/args:
  ```bash
  echo -n '<TOKEN>' | fj auth add-token -H <host>
  ```
- Credentials are stored in `~/Library/Application Support/forgejo-cli.forgejo-cli/keys.json` (macOS), mode `0600`. Rotate a leaked token in the instance's Applications settings, then re-run `add-token`.

## Common commands (gh → fj cheat sheet)

### repo
```bash
fj repo clone <owner/repo> [PATH] [-S]     # -S / --ssh clones over SSH
fj repo view [<owner/repo>]                # infers from cwd remote if omitted
fj repo create <name> [-P] [-d "desc"] [-p] [-r origin] [-S]   # bare NAME (created under signed-in user, NOT owner/repo); -P private, -p push current branch
fj repo fork <owner/repo>
fj repo browse                             # open in browser
fj repo labels ...                         # manage issue labels
fj repo edit / units / delete / star / watch / readme
```

### issue
```bash
fj issue create "<title>" --body "..." [-r owner/repo]
fj issue search [QUERY] [-s open|closed|all] [-l labels] [-a assignee] [-c creator] [-r owner/repo]
fj issue view <ID>
fj issue comment <ID> --body "..."         # (comment is a subcommand of issue)
fj issue close <ID>  /  assign  /  unassign  /  edit  /  browse  /  templates
```

### pr
```bash
fj pr create ["<title>"] --base <branch> --head <branch> --body "..." [-A]  # -A autofills title/body from commits; "WIP: " prefix = draft
fj pr search [QUERY] [-s open|closed|all] [-l labels] [-a assignee] [-r owner/repo]
fj pr view <ID>
fj pr status <ID>                          # mergeability + CI status
fj pr checkout <ID>                        # check out PR into a new branch
fj pr merge [<ID>] -M merge|rebase|rebase-merge|squash|manual [-d] [-t title] [-m msg]  # -d deletes branch
fj pr review / comment / assign / edit / close / browse
```

### actions
```bash
fj actions tasks [-r owner/repo]           # list workflow runs
fj actions dispatch <WORKFLOW> <REF> [-r owner/repo]   # trigger workflow_dispatch on a git ref
fj actions variables ...  /  secrets ...   # manage repo variables & secrets
```

### release / tag
```bash
fj release list / view / create / edit / delete / asset / browse
fj tag list / view / create / delete
```

### user / org
```bash
fj user repos <username>                   # list a user's repos
fj user view / search / follow / key / gpg / activity / orgs / edit
fj org list / view / create / members / team / repo / label
```

## Notes

- `fj` has no `--version` flag; use `fj version`.
- Zsh completions ship with the Homebrew formula (`/opt/homebrew/share/zsh/site-functions`).
- When output must be parsed, prefer explicit `-r owner/repo` + `-H host` for determinism rather than relying on remote inference.
