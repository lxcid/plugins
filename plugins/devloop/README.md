# devloop

Devloop uses intents as units of change within its own development workflow. The intent concept informs the process; the plugin has its own scope and conventions.

Shared plugin package for Claude Code and Codex. Version `0.2.0` includes `start-work` and `deep-review`; intent stage automation, hooks, and agents are not implemented yet.

## Start work

The [start-work skill](skills/start-work/SKILL.md) turns a GitHub issue, another ticket reference, or a freeform task into scoped implementation work. It checks current code, docs, and recent decisions before planning, protects existing work, prepares the branch or worktree, and begins implementation with focused verification.

- Claude Code: `/devloop:start-work 123` or `/devloop:start-work <task description>`.
- Codex: ask “Use devloop's start-work skill to implement issue 123” or “Use devloop's start-work skill to fix <problem>.”

Small tasks use a brief in-session plan. Medium, large, or multi-session tasks use a draft PR as the shared planning and continuation surface. The skill can create a branch, push commits, open or update that PR, and edit project files as part of implementation; it is not a planning-only or review-only workflow. It asks when scope is unclear or stale, before creating a tracking issue or worktree unless already authorized, and before repurposing existing user work.

Run in the target project's Git checkout with the GitHub CLI (`gh`) authenticated for issue and PR access, and the ability to push for the draft PR workflow. Other ticket sources need an available integration or content supplied by the user. The skill follows repository and host guidance for branch names and resolves the default branch rather than assuming `main`.

The skill adapts the personal `start-work` workflow originally used in Mempipe. It does not require Mempipe-specific tooling or devloop intent artifacts.

## Deep review

The [deep-review skill](skills/deep-review/SKILL.md) reviews a PR, branch, explicit path, or commit range for correctness, regressions, redundancy, and accidental complexity. It reports findings first, then proposes minimal fixes. Both phases leave files unchanged.

- Claude Code: `/devloop:deep-review 123` or `/devloop:deep-review` to choose a target.
- Codex: ask “Use devloop's deep-review skill to review PR 123” or “Use devloop's deep-review skill to review this branch.”

If the target is missing or ambiguous, the skill first asks whether to continue the session's previous review target. If there is no previous target or you decline without naming a replacement, it offers recent PRs, branches, and worktrees and waits for your choice. If the selected worktree has uncommitted changes, it asks whether to include them before reviewing, unless you have already decided.

Run in a Git checkout. GitHub PR lookup and diff retrieval use the GitHub CLI (`gh`) and require authentication with access to the repository. Explicit paths and commit ranges can be reviewed directly without GitHub PR discovery.

The skill adapts the original personal `deep-review` instructions for a shared package. It does not require devloop intent artifacts or a separate reviewer agent.

## Package layout

- `plugin.json`: portable Agent Plugins manifest and canonical package identity.
- `.claude-plugin/plugin.json`: Claude Code manifest.
- `.codex-plugin/plugin.json`: Codex compatibility manifest and display metadata. The portable manifest intentionally omits `extensions.com.openai` so this file supplies the OpenAI-specific settings.

Keep the name, version, description, author, homepage, and repository identical across all three manifests. Bump all three versions together when releasing changes. The repository's root `package.json` describes development tooling, not the installable plugin.

Add shared workflow content under this directory as it is implemented: `skills/<name>/SKILL.md`, `templates/`, and `scripts/`. Keep packaged resources within this directory so they remain available after either host installs its own copy. Add host-specific hook and agent configuration only when implemented and verified in that host.

Both repository marketplace catalogs point here. Each host manages its own installation, settings, and updates. Downstream plans and artifacts belong in the target project's repository and PRs, outside the installed plugin. `start-work` keeps the evolving plan in the draft PR for medium, large, or multi-session work; it does not require a `docs/intents/` directory.
