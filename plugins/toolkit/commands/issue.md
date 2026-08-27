Please analyze and fix the GitHub issue: $ARGUMENTS.

Guidelines:
1. when committing, dont mention Claude
2. when committing and opening PRs, always use sematic commit format

Preparation:
1. checkout main
2. update main branch / pull
3. create a new branch from main

Follow these steps:

1. Use `gh issue view` to get the issue details
2. Understand the problem described in the issue
3. Search the codebase for relevant files
4. Implement the necessary changes to fix the issue
5. Write and run tests to verify the fix
6. Ensure code passes linting and type checking
7. Create a descriptive commit message
8. Push and create a PR

Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks.
