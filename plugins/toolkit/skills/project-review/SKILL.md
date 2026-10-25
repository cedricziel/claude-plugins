---
name: project-review
description: Review a whole project from several angles and suggest a separate fix chat for each confirmed finding, with enough context to carry the fix through merge. Use for project-wide reviews or audits, rather than reviews of a single diff or PR.
---

# Project review

Review the current project and produce evidence-backed findings with actionable fix-chat suggestions. The review itself makes no project changes and launches no fix chats unless the user asks.

## Establish scope

When the user provides no additional instructions, systematically review the entire project. Do not ask the user to choose review angles or narrow the scope. Honor any scope or constraints the user supplies.

Read project instructions, repository status, architecture, entry points, and validation commands. Establish the revision and account for local changes. Inventory all first-party components, shared libraries, tests, configuration, build and release automation, and documentation. Use that inventory as a coverage checklist, tracking each area as reviewed, inapplicable, or blocked. Exclude generated and vendored content unless it affects first-party behavior. Check existing issues, PRs, and active work when accessible to avoid proposing duplicate fixes.

Review each applicable area for correctness and edge cases, security and data handling, architecture and maintainability, performance and resource use, tests and failure coverage, delivery and operations, and documentation or user experience. Trace important flows across component boundaries as well as inspecting individual components. Prioritize deeper investigation by risk, but do not stop after the first findings or silently omit less prominent areas. Skip angles that do not apply and explain significant coverage gaps. If the project exceeds the available review budget, report completed coverage and the remaining areas without claiming a complete review.

For substantial independent angles, delegate bounded read-only reviews to subagents when available. Invoking this skill authorizes review subagents, not user-visible fix chats. Give each reviewer the revision, relevant paths, angle, constraints, and expected evidence. Use direct inspection for small projects or when delegation is unavailable.

## Verify findings

Inspect surrounding code and trace the affected behavior before accepting a finding. Require a concrete trigger, consequence, and source location or reproducible evidence. Run focused checks only in an isolated environment when execution is needed. Do not report hypothetical improvements as defects.

Deduplicate findings across angles and existing work. Keep unresolved suspicions separate, with the missing evidence. Prioritize confirmed findings by impact and confidence; do not invent findings to fill every angle. State plainly when no actionable findings remain.

## Suggest one fix chat per finding

For every confirmed finding, provide severity, a short title, a clickable source reference, evidence, impact, and the smallest useful fix scope. Pair it with a suggested new chat and a self-contained prompt containing:

- Project identity, repository location, reviewed revision, relevant paths, and finding evidence.
- Expected behavior, scope boundaries, dependencies on other findings, and acceptance criteria.
- A requirement to verify the finding against current HEAD and existing PRs before editing.
- The main checkout path, default branch, and the worktree and rebase instructions below.
- Relevant validation commands discovered in this project, or a request to discover them when unverified.
- The model and effort policy below, plus the completion instructions below.

Keep one independently mergeable fix per chat. If findings share a root cause, consolidate them before reporting. Make ordering explicit when fixes depend on each other.

Provide a copyable prompt for each suggested fix session. A suggestion does not create a session. When the user explicitly requests creation, use the host's supported session-creation capability and retain the full handoff context. If that capability is unavailable, provide the prompt and report the limitation.

## Preserve model choices

Carry explicit user model and effort choices into fix sessions. Otherwise use the same model policy as the review session, including its roles for scans, implementation, debugging, and judgment. Record role-specific routing in the fix prompt so workers use the established choices. Do not silently substitute an unsupported model; report the limitation and request a choice when needed.

## Drive authorized fixes through merge

Start each fix chat in a fresh, dedicated worktree created from the project's main checkout, based on the current remote default branch. Use the host's supported worktree creation flow and pass the resulting path to the chat. Keep the main checkout available for coordination. Check existing ownership first; reuse a worktree only when the user requests it or it already belongs to this fix.

Fetch and rebase owned fix branches onto the current default branch regularly during implementation, before pushing, and again before merging when the base has advanced. Rebase only from a clean state or after committing coherent work. Resolve conflicts, then rerun affected checks. Never rewrite a peer's branch. If rebasing would disrupt shared work or a dependent PR stack, report the constraint and agree on an integration order instead.

Include this completion contract in every fix prompt: recheck the premise, implement the smallest complete fix in an owned branch or worktree, add meaningful regression coverage, and run the project's required checks. Open a focused PR when authorized. Monitor it, address CI failures and accepted review findings, resolve conflicts in owned work, and resume monitoring after fixes. Merge when authorized and required checks and approvals permit it. Stop at a required user decision or external blocker with the exact next action; an open PR alone does not complete the fix. Report the merged PR and validation evidence when done.

The handoff expresses the intended outcome without granting permissions the user has not supplied. Respect repository rules, required approvals, and the host's external-action boundaries.

Finish the review with findings and their fix-chat suggestions, then a brief account of angles covered, checks performed, and remaining uncertainty.
