---
name: start-work
description: Start implementation from a GitHub issue, ticket reference, or freeform task. Resolve current scope, prepare a branch or worktree, preserve the plan in a draft PR when warranted, and begin coding. Do not use for review-only or planning-only requests.
---

# Start Work

Use this workflow to move from "there is work to do" to a prepared implementation branch, then to a well-scoped implementation plan written on its draft PR, with enough context, scope control, and verification to avoid chasing stale issue text.

Classify scope, treat issues as context rather than commands, do code discovery before medium/large plans, derive a useful branch/worktree slug, and surface stale assumptions before coding.

Run in the target project's Git checkout. GitHub issue and PR operations use the GitHub CLI (`gh`) authenticated with access to that repository. If access is unavailable, ask for the missing issue context or access before dependent work; do not treat a failed lookup as evidence that no issue or PR exists. Keep plans and project artifacts in the target project, not the installed plugin.

## Ground Rules

1. Honor repository guidance already loaded in context, such as `AGENTS.md`, `CLAUDE.md`, or equivalents. Read those files only when they are absent from context, may be stale, or you need an exact current section or linked doc for the touched surface.
2. Prefer local truth over old issue text. Current code, current docs, merged PRs, and recent issue comments can supersede the issue body.
3. Ask the user when the source material is vague, contradictory, stale, or expanding beyond the original request. Honor decisions and authorization already given in the session rather than asking again.
4. Do not overwrite uncommitted work. Treat a dirty worktree as user-owned until proven otherwise.
5. Once the task is clear and the work environment is safe, proceed into implementation. Do not stop at a proposal unless the user asked for planning only or an ambiguity genuinely blocks safe work.

## Phase 0: Resolve The Work Item

Determine the work source:

1. GitHub issue URL or number: read it directly.
2. Other ticket reference: use available tools or local references to retrieve it; if no tool exists, ask the user for the ticket content or URL.
3. Freeform description: search local docs and GitHub issues for a matching existing ticket before creating new tracking work.
4. No usable source: ask one concise clarification question before proceeding.

For GitHub issues, gather the issue and discussion:

```bash
gh issue view <issue> --json number,title,body,state,labels,assignees,milestone,comments,createdAt,updatedAt,url
gh pr list --state all --search "<issue number or title keywords>" --json number,title,state,url,headRefName,baseRefName,mergedAt,closedAt
```

For freeform descriptions, search both repo context and GitHub:

```bash
rg -n "<keywords>"
gh issue list --state all --search "<keywords>" --json number,title,state,labels,updatedAt,url --limit 20
```

If a relevant issue exists, link the work to it and use it as context. If several plausible issues exist or the match is weak, ask the user which one to use. If no issue exists:

1. Large, vague, or cross-cutting work: ask whether to create a tracking issue unless the user explicitly requested one, proposing a concrete title/body from the gathered context.
2. Small work: ask whether the user wants a tracking issue; otherwise proceed without one.
3. Never create a duplicate issue when an existing ticket is close enough to carry the work.

For medium, large, or multi-session work, the shared planning surface is a draft PR opened right after branch setup (Phase 4). Use the tracking issue only to link the work and to record decisions that must survive before a branch exists; do not run a parallel planning thread in issue comments.

## Phase 1: Review The Current State

Consolidate the latest state before planning. Read:

1. The issue body and all comments, weighting newer comments and maintainer/operator decisions over older text.
2. Linked or search-discovered PRs, especially merged or closed PRs that may have completed or invalidated part of the request.
3. Relevant guidance and docs for the touched surface, per Ground Rule 1.
4. Current code around the affected surface.

Produce an internal brief:

1. Goal: what outcome the user or ticket is asking for.
2. Latest stage: open, blocked, partially shipped, closed-but-follow-up, or stale.
3. Scope boundaries: what is in and out for this pass.
4. Known decisions: decisions recorded in docs, comments, or merged PRs.
5. Unknowns: questions that could change the implementation.
6. Ticket link: the issue or tracking ticket to mention in branch names, commits, PRs, and final handoff.

If the ticket is closed, mostly done, contradicted by current docs, or appears to request the wrong product direction, stop and confirm the intended follow-up before editing.

## Phase 2: Classify Scope

Classify before planning:

1. Small: one clear concern, likely 1-2 files, obvious verification. Plan briefly in session and proceed.
2. Medium: a few files or one subsystem, with some unknowns. Run focused discovery before finalizing the plan.
3. Large: cross-cutting, user-facing workflow, schema/data migration, architectural choice, many unknowns, or vague source material. Link an existing tracking issue or ask whether to create one, run deeper discovery, and confirm scope with the user before implementation.

Follow the repository's design guidance when deciding whether to solve edge cases now. Weigh likelihood, impact, recoverability, and cost instead of making the plan "complete" for its own sake.

## Phase 3: Pre-Branch Discovery

For medium and large work, search code before committing to a branch or a plan:

```bash
rg -n "<domain terms|types|routes|components|events>"
rg --files | rg "<surface|feature|test>"
```

Discovery grounds the plan in the current system shape: which files and patterns are involved, what already exists to extend, and where the issue text has gone stale.

## Phase 4: Set Up The Work Environment

Inspect git state:

```bash
git status --short --branch
git branch --show-current
git remote get-url origin
```

Protect existing work:

1. If the worktree is dirty, identify whether the changes are yours and whether they overlap the planned files.
2. If dirty changes are unrelated, avoid touching them.
3. If dirty changes overlap and you did not make them, ask how to proceed.
4. If `git status --short --branch` shows the branch ahead of its upstream or holding unpushed commits, treat those commits as user-owned work and ask before branching from a different base.

Derive a branch slug:

1. Prefer an issue/ticket prefix plus 2-4 meaningful keywords, for example `316-search-freshness` or `wiki-link-preview`.
2. Keep the slug lowercase, concise, and stable. Drop filler words like `add`, `fix`, or `improve` unless they carry useful meaning.
3. If the task is freeform and no tracking issue exists, use a short description-based slug.

Choose a branch prefix:

1. Honor repository or host branch-naming guidance. Otherwise use the repo's normal work-type prefixes, such as `feat/<slug>`, `fix/<slug>`, `chore/<slug>`, or `docs/<slug>`.
2. Use `<prefix>/<slug>` in the commands below.

Before creating a branch or worktree, check whether one already exists:

```bash
git worktree list --porcelain
git branch --list "<prefix>/<slug>"
```

If a matching worktree exists, offer to use it instead of recreating it. If the branch exists without a worktree, offer to attach a worktree to it. If the target path exists but is not a git worktree, stop and ask; do not overwrite it.

Choose the working base:

Resolve the repository's default branch from `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` or a verified remote HEAD; do not assume it is named `main`. Use an explicit user-selected base when provided, otherwise use the default branch. Substitute that selection for `<base>` in the examples below. The examples assume the target remote is `origin`; substitute the appropriate remote when needed.

1. Prefer working in the primary checkout when it is clean and not already on a branch with an open PR or in-progress work.
2. On the default branch: fetch the latest base, then create a new branch from `origin/<base>` with the chosen `<prefix>/<slug>`.
3. On another branch: look for an associated PR.

```bash
gh pr list --head "$(git branch --show-current)" --state open --json number,state,url,baseRefName,headRefName --limit 5
```

Only if the open-PR lookup succeeds with no results, look for closed or merged PRs using the same command with `--state closed`. A lookup error leaves the PR status unknown.

If the branch has an open PR or in-progress work for a different task, ask whether this work belongs there or should use a new branch/worktree. If it has only closed or merged PRs and no remaining user work, move back to the latest selected base in the primary checkout and branch from there. Default to a new branch in the primary checkout when it is available; consider a worktree when the primary checkout is already occupied. If there is no PR and the branch has user work, ask before repurposing it.

Consider a worktree when:

1. The primary checkout is already on a branch with an open PR or in-progress work for a different task.
2. The current worktree has unrelated or overlapping dirty changes.
3. The user wants to keep the current branch untouched.

Ask before creating a worktree. A typical shape is:

```bash
git fetch origin <base>
git worktree add -b <prefix>/<slug> ../<repo>-<slug> origin/<base>
```

Confirm with the user before branching from anything other than the default branch, unless they already selected that base. If a new worktree needs setup, prefer documented repo setup commands. If setup is not obvious, ask whether to run one or skip. Stream setup output, and if setup fails, leave the branch/worktree in place and report the exact command to retry.

For medium, large, or multi-session work, open a draft PR as soon as the branch exists. Push an empty commit if there is nothing to commit yet (`git commit --allow-empty -m "chore: initial commit"` or equivalent), then create the draft PR with a minimal body that links the tracking issue. From then on the draft PR is the planning surface: update its description as planning and implementation progress instead of posting planning notes elsewhere.

## Phase 5: Plan Implementation

With the environment ready, write the implementation plan. For small work, the brief in-session plan from Phase 2 suffices. For medium, large, or multi-session work, write the plan into the draft PR description and keep it updated there as understanding changes.

Plan from the current system shape surfaced in discovery:

1. Relevant files and patterns to follow.
2. Reuse opportunities: existing helpers, components, routes, schema patterns, tests, or docs that should be extended.
3. Mismatches: stale issue assumptions, already-shipped pieces, changed interfaces, or simpler paths.
4. Phases or steps: each step should be focused, testable, and leave the codebase coherent.
5. Verification: exact commands or manual checks appropriate to the touched surface.

Tests belong with the behavior they protect. Do not create a standalone "add tests later" phase for behavior introduced earlier.

If planning reveals the issue is getting out of hand, stop and offer the smallest credible slice. Name what will be deferred and why.

## Phase 6: Start Actual Work

After the work item is resolved, scope is sane, and the branch/worktree is safe, implement the task.

1. Use the plan as a guide, but keep reading the code as you go. If the plan conflicts with current code, update the plan instead of forcing the code to match stale assumptions.
2. Keep edits tightly scoped to the request and the touched surface.
3. Follow existing patterns and helper APIs before adding abstractions.
4. Update docs only when behavior, commands, architecture, or user-facing workflow changes.
5. Run the focused verification first, then broader checks when the blast radius warrants it.
6. If a fix fails, narrow the hypothesis with source reading, logs, or a smaller repro before trying a different design.

When using a task list, keep it current: exactly one item in progress, mark completed items as they finish, and revise the list when discovery changes the work.

## Handoff

Finish with:

1. Work item: issue/ticket link or "no tracking ticket".
2. Branch/worktree: branch name and, if relevant, worktree path.
3. What changed: concise implementation summary.
4. Verification: commands run and results.
5. Open questions or deferred scope.

Keep the PR body current as the continuation surface: final scope, key decisions, verification, and known deferrals. If no draft PR was opened earlier, bring the latest understanding into the PR body when creating it. Link back to the issue rather than duplicating its history.

Do not close a GitHub issue or mark a ticket done unless the user explicitly asked or the PR body is intentionally set up to close it on merge.
