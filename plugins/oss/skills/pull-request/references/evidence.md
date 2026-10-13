# Visual evidence

Before/after evidence lets a reviewer see a change without checking out the branch.
Add it when the change is visible: UI, CLI or API output, a rendered page. Skip it for
refactors and internals.

## Capture

Run the same steps against both sides so the pair is comparable:

- **After**: the branch, using the project's `verify` skill or its documented run steps.
- **Before**: the base branch, in a throwaway worktree (`git worktree add <tmp> <base>`)
  on its own ephemeral instance. Remove the worktree and stop the instance afterwards.

Pick the format by what changed:

| Change              | Evidence                                                                      |
| ------------------- | ----------------------------------------------------------------------------- |
| UI                  | Screenshots at the same viewport and state, before and after                  |
| Interaction or flow | A short recording (Playwright `recordVideo`), converted to a GIF under ~10 MB |
| CLI or API output   | Before/after text in a `<details>` block, not a screenshot of a terminal      |

Never capture real user data, tokens, or internal hostnames. Use the instance's test
data.

## Upload

`gh` cannot upload images. Use GitHub's own uploader in a browser where the user is
already signed in to GitHub (for example through a browser-automation tool attached to
their browser):

1. Open the PR and start editing the description, or open a new comment box.
2. Set the editor's file input (`input[type=file]` under the Markdown field) to the
   image, or paste it. GitHub uploads it and inserts
   `![name](https://github.com/user-attachments/assets/<id>)` into the text.
3. Copy the inserted Markdown, then cancel the edit. The uploaded URL keeps working.
4. Put the URLs into the body with `gh pr edit --body-file`.

Do not sign in on the user's behalf or handle their credentials. If no signed-in browser
is available, do not host the images anywhere else (no extra branches, commits, or
third-party hosts). Leave the files in a scratch directory, list their paths in the
handoff, and ask the user to drag them into the PR.

## Layout in the body

Put an `## Evidence` section after `## Tests`:

```markdown
## Evidence

| Before                                                  | After                                                  |
| ------------------------------------------------------- | ------------------------------------------------------ |
| ![before](https://github.com/user-attachments/assets/…) | ![after](https://github.com/user-attachments/assets/…) |
```

One line under the table says what to look at when it is not obvious.
