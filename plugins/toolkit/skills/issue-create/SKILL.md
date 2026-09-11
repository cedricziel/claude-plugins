---
name: issue-create
description: Create a well-structured, actionable GitHub issue from context the user gives you — picks the right template (bug/feature/docs/task/question), gathers the details that template needs, and files it with `gh issue create`. TRIGGER ONLY on `/issue-create <context>`, or an explicit ask to create/file a GitHub issue. DO NOT trigger on mentions of "issue" in passing, on bug reports the user is just describing without asking for a tracker entry, or on `/issue-run`'s own issue-triage/issue-resolve steps (those are separate workflows).
---

# Create a GitHub issue

Help turn context — a bug report, a feature idea, a documentation gap, a chore — into a
well-structured GitHub issue that gives whoever picks it up everything they need, without
making them ask follow-up questions first.

## When this fires

| Ask                                                           | Action                                            |
| ------------------------------------------------------------- | ------------------------------------------------- |
| `/issue-create <context>`                                     | run it                                            |
| "file a bug for X", "create an issue about Y"                 | run it                                            |
| user is describing a bug but hasn't asked for a tracker entry | **not this skill** — just help them               |
| `/issue-run`'s triage/resolve steps                           | **not this skill** — those are separate workflows |

If you already have enough context to write a complete, well-structured issue (the case
most of the time when this fires mid-conversation, e.g. after an investigation), skip the
interactive Q&A below and go straight to drafting — don't make the user re-answer questions
you already know the answer to.

## Step 1: Identify the issue type

If it isn't obvious from the context given, ask:

"What type of issue would you like to create?

- 🐛 **Bug Report** — something isn't working as expected
- ✨ **Feature Request** — new functionality or enhancement
- 📚 **Documentation** — missing, unclear, or incorrect documentation
- 🔧 **Task/Chore** — maintenance, refactoring, or organizational work
- ❓ **Question** — need clarification or support
- 🏷️ **Other** — specify a custom type"

## Step 2: Gather what that template needs

### 🐛 Bug Report

Bug description; steps to reproduce (numbered); expected vs. actual behavior; environment
(OS, app/browser version, device, relevant config); exact error text/stack traces;
screenshots if visual; additional context (related issues, workarounds, frequency).

### ✨ Feature Request

Problem statement; use case and who benefits; proposed solution; alternatives considered;
acceptance criteria; priority/impact; implementation notes/constraints; related issues.

### 📚 Documentation

What's missing or unclear; target audience; where it should live; what exists now;
desired outcome; examples to include; related resources.

### 🔧 Task/Chore

What work is needed and why; scope (in/out); acceptance criteria; dependencies;
effort estimate; impact of completing it.

### ❓ Question

The specific question; context and what's already been tried; what kind of answer is
wanted (guidance vs. specific steps); urgency; docs already checked.

Ask only for what's still missing — don't re-ask for details already given. Prefer one
clarifying question at a time over a long intake form.

## Step 3: Write the issue

**Title:** 50-72 characters, specific and actionable. Imperative mood for bugs ("Fix login
button on mobile Safari"), descriptive for features ("Add dark mode toggle to user
settings"). Avoid vague terms like "broken" or "doesn't work".

**Labels:** check the repo's actual labels first (`gh label list`) — never guess or invent
one. Match by type (bug/feature/documentation), and by priority/component/effort if the
repo has labels for those.

**Body:** organize with clear section headers matching the template above, checklists for
acceptance criteria, code blocks for errors/stack traces, `#123`-style links for related
issues. For a large feature/epic, use GitHub's sub-issues
(https://docs.github.com/en/rest/issues/sub-issues) to decompose it rather than writing one
sprawling issue.

Confirm the drafted title, labels, and body with the user before filing, unless they've
already reviewed equivalent content earlier in the conversation (e.g. you're filing a
followup that summarizes findings they've already seen).

## Step 4: File it

Use `gh issue create` (or `gh issue create --label ... --assignee ...` as applicable) —
always the GitHub CLI, never a raw API call, for consistency with the rest of this
toolkit's GitHub-related skills.
