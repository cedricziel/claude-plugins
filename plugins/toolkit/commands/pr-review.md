---
description: Review a GitHub pull request for correctness, quality, and risk
argument-hint: <PR number or URL>
---

Please provide a code review for this pull request: $ARGUMENTS.

Guidelines:
1. when committing, dont mention Claude
2. when committing and opening PRs, always use sematic commit format
3. be friendly, but enforce good practices

Preparation:
1. checkout main
2. update main branch / pull
3. create a new branch from main

Follow these steps:

1. Use `gh issue view` to get the pr details
2. Understand the problem that the PR addresses - gather context inside and outside the project
3. Search the codebase for relevant files
4. Look out for tests that cover the functionality
5. add comments to the PR and to the diffs as appropriate - use

Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks.
