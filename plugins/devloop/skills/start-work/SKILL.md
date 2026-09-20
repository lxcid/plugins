---
name: start-work
description: Resolve and start implementation work from a GitHub issue, ticket reference, or freeform task description. Use when the user asks to start work, pick up an issue, implement a feature or bug fix, set up a well-scoped implementation plan before writing code, turn a vague description into actionable work, create or link a tracking ticket, preserve planning memory in an issue or PR, prepare the branch/worktree, and begin coding. Do not use for review-only or planning-only requests.
---

# Start Work

Use this workflow to move from "there is work to do" to a prepared implementation branch, then to a well-scoped implementation plan in a shared planning surface, with enough context, scope control, and verification to avoid chasing stale issue text.

Classify scope, treat issues as context rather than commands, do code discovery before medium/large plans, derive a useful branch/worktree slug, and surface stale assumptions before coding.

Run in the target project's Git checkout. GitHub issue and PR operations use the GitHub CLI (`gh`) authenticated with access to that repository. If access is unavailable, ask for the missing issue context or access before dependent work; do not treat a failed lookup as evidence that no issue or PR exists. Keep plans and project artifacts in the target project, not the installed plugin.

## Ground Rules

1. Honor repository guidance already loaded in context, such as `AGENTS.md`, `CLAUDE.md`, or equivalents. Read those files only when they are absent from context, may be stale, or you need an exact current section or linked doc for the touched surface.
2. Prefer local truth over old issue text. Current code, current docs, merged PRs, and recent issue comments can supersede the issue body.
3. Ask the user when the source material is vague, contradictory, stale, or expanding beyond the original request. Honor decisions and authorization already given in the session rather than asking again.
4. Do not overwrite uncommitted work. Treat a dirty worktree as user-owned until proven otherwise.
5. Once the task is clear and the work environment is safe, proceed into implementation. Do not stop at a proposal unless an ambiguity blocks progress or the user asks you to pause or switch to planning only.

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

For medium, large, or multi-session work, reuse the task's existing open PR or open a draft PR right after branch setup (Phase 4). By default, use its description as the shared planning surface. Follow existing project conventions when they designate another home for the plan, such as a version-controlled `plan.md`, and link to it from the PR. Keep one authoritative plan.

Use supporting documents, shared notes, or scratchpads when they help with exploration, coordination, or continuity during development. Keep them clearly connected to the authoritative plan, and fold decisions back into it as they settle rather than maintaining competing versions.

Use the tracking issue to link the work and capture decisions made before the planning surface is available. Carry those decisions into the plan when it is established.

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

Follow the repository’s design guidance when deciding whether to handle edge cases now. Weigh likelihood, impact, recoverability, and the total cost of addressing or deferring related work, including additional review cycles, repeated context gathering, and temporary workarounds. Prefer a coherent change that fully addresses the current requirement. Handle related edge cases together when they share the same design and verification and doing so is cheaper overall. Do not defer closely related work merely to keep the PR small. Split work when it meaningfully reduces risk or separates independent concerns. Splitting can also make sense when it creates a natural step-by-step progression; propose the sequence and ask the user before splitting on that basis. When the scope tradeoff is unclear, explain the options, recommend an approach, and ask the user to decide rather than defaulting to a smaller PR. Avoid speculative completeness.

## Phase 3: Pre-Branch Discovery

For medium and large work, search code before committing to a branch or a plan:

```bash
rg -n "<domain terms|types|routes|components|events>"
rg --files | rg "<surface|feature|test>"
```

Discovery grounds the plan in the current system shape: which files and patterns are involved, what already exists to extend, and where the issue text has gone stale.

## Phase 4: Set Up The Work Environment

When continuing the same task, reuse its branch and worktree only if the PR is still open or the task branch has no PR and has not been merged. Verify that status before reusing it. If the previous PR was merged or closed, or the branch was already merged, resolve any remaining task work as described below before starting a new branch from the latest selected base. Do not create a new branch merely because the skill was invoked again.

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
4. Before branching from a different base, check for task work not incorporated into that base, whether pushed or unpushed, including branches without an upstream. Account for squash/rebase merges using PR history and content evidence rather than ancestry alone. If work remains or integration is unclear, treat it as user-owned and ask how to carry it forward before switching. A clean status or being up to date with upstream does not establish that the work was integrated.

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

If a matching worktree exists, offer to use it instead of recreating it. If the branch exists without a worktree, prefer checking it out in the current checkout when safe. If the target path exists but is not a git worktree, stop and ask; do not overwrite it.

For new work that needs a branch, choose the working base.

Resolve the repository's default branch from `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` or a verified remote HEAD; do not assume it is named `main`. Use an explicit user-selected base when provided, otherwise use the default branch. Substitute that selection for `<base>` in the examples below. The examples assume the target remote is `origin`; substitute the appropriate remote when needed.

Before creating or switching branches, fetch the selected base and inspect candidate unmerged work. These commands show ancestry differences; apply the existing-work checks above to determine what remains unintegrated.

```bash
git fetch origin <base>
git branch --no-merged origin/<base>
git log --oneline origin/<base>..HEAD
```

1. Prefer working in the primary checkout when it is clean and no open PR or in-progress work there belongs to a different task.
2. On the default branch: create a new branch from `origin/<base>` with the chosen `<prefix>/<slug>`.
3. On another branch: look for an associated PR.

```bash
gh pr list --head "$(git branch --show-current)" --state open --json number,title,state,url,baseRefName,headRefName --limit 5
```

Only if the open-PR lookup succeeds with no results, look for closed or merged PRs using the same command with `--state closed`. A lookup error leaves the PR status unknown. Resolve the lookup failure or ask the user before deciding whether to reuse or replace the branch. If the PR title and session context do not establish whether it belongs to this task, inspect the PR description and linked issues or ask the user.

If an open PR or unfinished work on the branch belongs to a different task, ask whether to continue there or start separately. If the branch has only closed or merged PRs, or was itself already merged, apply the existing-work checks above, including squash/rebase integration evidence, before switching. Then create a new branch from the latest selected base in the current checkout, preserving the agreed work; do not discard it or continue on the merged branch. For new work, default to a new branch in the primary checkout when it is available; consider a worktree when the primary checkout is already occupied. If there is no PR and the branch has user work, ask before repurposing it.

When asking how to continue, offer concrete choices that fit the current state:

- Continue on the existing branch and worktree, only if its PR is open or it has no PR and is unmerged.
- Create a new branch from the latest default branch in the primary checkout, if it is safe to use.
- Create a new branch from the latest default branch in a new worktree.
- Use another branch, base, or worktree specified by the user.

Name the relevant branches and worktree paths, recommend an option, and wait for the user's choice. Selecting the new-worktree option authorizes that worktree; do not ask again for the same approval.

Consider a worktree when:

1. An open PR or unfinished work in the primary checkout belongs to a different task.
2. The current worktree has unrelated or overlapping dirty changes.
3. The user wants to keep the current branch untouched.

Ask whether the user wants a separate worktree or prefers to stay in the current checkout, and wait for explicit approval before creating one, including when attaching an existing branch. A request to start work or create a branch or PR is not approval to create a worktree. Honor approval already given for that worktree. A typical shape is:

```bash
git fetch origin <base>
git worktree add -b <prefix>/<slug> ../<repo>-<slug> origin/<base>
```

Confirm with the user before branching from anything other than the default branch, unless they already selected that base. If a new worktree needs setup, prefer documented repo setup commands. If setup is not obvious, ask whether to run one or skip. Stream setup output, and if setup fails, leave the branch/worktree in place and report the exact command to retry.

For medium, large, or multi-session work, reuse the task's existing open PR. If none exists, open a draft PR as soon as the branch exists. Push an empty commit if there is nothing to commit yet (`git commit --allow-empty -m "chore: initial commit"` or equivalent), then create the draft PR with a minimal body that links the tracking issue. Use the PR description as the default planning surface, or link to the authoritative plan designated by project conventions. Supporting notes may live elsewhere; keep settled decisions in the authoritative plan.

## Phase 5: Plan Implementation

With the environment ready, write the implementation plan. For small work, the brief in-session plan from Phase 2 suffices. For medium, large, or multi-session work, write and maintain one authoritative plan in the draft PR description by default, or in the planning artifact designated by project conventions and linked from the PR. Use supporting notes as needed and fold settled decisions into the plan as understanding changes.

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

Keep the authoritative plan current with final scope, key decisions, verification, and known deferrals. When the plan lives outside the PR description, keep the PR summary and link current so the next session can find it. If no draft PR was opened earlier, include the latest understanding or link to the existing plan when creating it. Link back to the issue rather than duplicating its history.

Do not close a GitHub issue or mark a ticket done unless the user explicitly asked or the PR body is intentionally set up to close it on merge.
