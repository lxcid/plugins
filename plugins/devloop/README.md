# devloop

Devloop aims to adapt [Anthropic's AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook) to its own workflow, with committed intent, specification, and planning artifacts. The `adopt` skill can install that pipeline process into a project. The other skills focus on GitHub and honor each project's conventions.

Shared plugin package for Claude Code and Codex. Version `0.4.0` includes `start-work`, `deep-review`, `persistent-review`, and `adopt`, plus a `reviewer` agent; intent stage automation and hooks are not implemented yet.

## Start work

The [start-work skill](skills/start-work/SKILL.md) turns a GitHub issue, another ticket reference, or a freeform task into scoped implementation work. It checks current code, docs, and recent decisions before planning, protects existing work, prepares the branch or worktree, and begins implementation with focused verification.

- Claude Code: `/devloop:start-work 123` or `/devloop:start-work <task description>`.
- Codex: ask “Use devloop's start-work skill to implement issue 123” or “Use devloop's start-work skill to fix <problem>.”

Small tasks use a brief in-session plan. Medium, large, or multi-session tasks default to the draft PR description as the shared planning surface. If project conventions designate a planning artifact such as `plan.md`, the skill maintains the plan there and links it from the PR. Supporting documents and scratchpads are welcome when useful, with settled decisions folded into one authoritative plan. The skill can create a branch, push commits, open or update that PR, and edit project files as part of implementation; it is not a planning-only or review-only workflow. It reuses an open PR or an unmerged task branch without a PR for ongoing work, starts a new branch after the previous PR is merged or closed, and requires explicit approval before creating a worktree. It asks when scope is unclear or stale, before creating a tracking issue unless already authorized, and before repurposing existing user work.

Run in the target project's Git checkout with the GitHub CLI (`gh`) authenticated for issue and PR access, and the ability to push for the draft PR workflow. Other ticket sources need an available integration or content supplied by the user. The skill follows repository and host guidance for branch names and resolves the default branch rather than assuming `main`.

The skill adapts the personal `start-work` workflow originally used in Mempipe. It does not require Mempipe-specific tooling or devloop intent artifacts.

## Deep review

The [deep-review skill](skills/deep-review/SKILL.md) reviews a PR, branch, explicit path, or commit range for correctness, regressions, redundancy, and accidental complexity. It reports findings first, then proposes minimal fixes. Both phases leave files unchanged.

- Claude Code: `/devloop:deep-review 123` or `/devloop:deep-review` to choose a target.
- Codex: ask “Use devloop's deep-review skill to review PR 123” or “Use devloop's deep-review skill to review this branch.”

If the target is missing or ambiguous, the skill first asks whether to continue the session's previous review target. If there is no previous target or you decline without naming a replacement, it offers recent PRs, branches, and worktrees and waits for your choice. If the selected worktree has uncommitted changes, it asks whether to include them before reviewing, unless you have already decided.

Run in a Git checkout. GitHub PR lookup and diff retrieval use the GitHub CLI (`gh`) and require authentication with access to the repository. Explicit paths and commit ranges can be reviewed directly without GitHub PR discovery.

The skill adapts the original personal `deep-review` instructions for a shared package. It does not require devloop intent artifacts or a separate reviewer agent.

## Persistent review

The [persistent-review skill](skills/persistent-review/SKILL.md) makes the current session a coordinator of independent reviewers in Claude Code, Codex, or both. Each reviewer is a persistent session of the [reviewer agent](agents/reviewer.md) applying `deep-review`. The same sessions are resumed for every round, and the skill returns `PASS`, `BLOCKED`, or `NEEDS_HUMAN`.

- Claude Code: `/devloop:persistent-review claude and codex, branch feature against main`.
- Codex: ask “Use devloop's persistent-review skill to review this branch with Claude and Codex.”

Rounds run in this order:

1. The reviewers review independently. Neither sees the other's findings until both finish.
2. Each reviewer cross-checks the other's blocking findings on the evidence.
3. A disputed finding goes back to its reviewer once, with the objection.

Findings end as confirmed, withdrawn, non-blocking, or unresolved. Unresolved disagreements go to the operator. The skill never settles them by vote. After fixes, the same reviewers are resumed to review the current state again.

- **Claude reviewer:** runs on Opus.
- **Codex reviewer:** runs on GPT-5.6 Sol at high reasoning effort.
- **Where settings live:** both sets of settings live in the agent file, not in `deep-review`.
- **Session state:** stored per worktree under the Git directory, so it is never committed.

Run in the target Git checkout. Requirements:

- Each requested host's CLI is installed and authenticated, and devloop is installed in that host.
- The coordinator can run the bundled Python 3 script with network access.
- Claude reviewers read `AGENTS.md` only when there is no `CLAUDE.md`. If a project has both, `CLAUDE.md` should link to or import `AGENTS.md`.

## Adopt patterns

The [adopt skill](skills/adopt/SKILL.md) installs devloop's engineering patterns into a project's `AGENTS.md`, and can set up its pipeline process. It keeps both current when re-run. Each pattern transfers as written and needs no knowledge of the target project.

- Claude Code: `/devloop:adopt design-judgment`, `/devloop:adopt all`, `/devloop:adopt pipelines`, or `/devloop:adopt` to choose from the catalog.
- Codex: ask “Use devloop's adopt skill to install the design-judgment pattern.”

The catalog holds six stances: `design-judgment`, `debugging-discipline`, `test-design`, `writing-style`, `commit-conventions`, and `handoff-contract`. It also holds one process, `pipelines`. Each pattern lives under [skills/adopt/references/](skills/adopt/references/). A reference file's frontmatter holds its id, version, and optional target file, which defaults to `AGENTS.md`. Everything below the frontmatter is the exact text installed. Edit a reference file to change what a pattern says, and raise its `version` so existing adopters pick up the change.

`pipelines` organises work as numbered `docs/pipelines/` directories, each holding an intent, a spec, and a plan. The operator owns the intent and its acceptance, the builder owns the plan, and the spec is shared. The pattern installs two sections:

- The process itself, as `docs/pipelines/README.md`.
- A `## Pipelines` section in `AGENTS.md` that sends agents to that README.

`all` leaves `pipelines` out. Its `AGENTS.md` section tells agents to work only through approved intents, so installing it commits the project to the process. Name it to adopt it.

Installed sections are delimited by HTML comment markers recording the pattern's version and a hash of the upstream text the section was written from. That hash is a baseline rather than a checksum of whatever is currently there: a body still matching it is untouched plugin content and can be replaced, and anything else is yours — whether you merged it in when adopting or edited it afterwards. On re-run an untouched section on an older version updates in place, a customized one stops and asks first, and a current one is left alone. Nothing outside the markers is modified, and the skill never reformats the file around them.

For repository-specific guidance, add a descriptive heading immediately after the relevant closing marker and before the next managed section:

```markdown
<!-- /devloop:debugging-discipline -->

### Local debugging guidance

- Include the failing command and relevant logs in bug reports.
```

These additions stay outside the managed body, so upstream updates can proceed without a customization conflict. State any exception to a managed rule explicitly.

Run in the target project's Git checkout. No GitHub access is required.

## Package layout

- `plugin.json`: portable Agent Plugins manifest and canonical package identity.
- `.claude-plugin/plugin.json`: Claude Code manifest.
- `.codex-plugin/plugin.json`: Codex compatibility manifest and display metadata. The portable manifest intentionally omits `extensions.com.openai` so this file supplies the OpenAI-specific settings.
- `agents/reviewer.md`: the reviewer role. Claude Code loads it as a plugin agent. Codex has no plugin agents, so `persistent-review` passes its body and its `codex:` settings to `codex exec`.

Keep the name, version, description, author, homepage, and repository identical across all three manifests. Bump all three versions together when releasing changes. The repository's root `package.json` describes development tooling, not the installable plugin.

Add shared workflow content under this directory as it is implemented: `skills/<name>/SKILL.md`, `templates/`, and `scripts/`. Keep packaged resources within this directory so they remain available after either host installs its own copy. Add host-specific hook and agent configuration only when implemented and verified in that host.

Both repository marketplace catalogs point here. Each host manages its own installation, settings, and updates. Downstream plans and artifacts belong in the target project's repository and PRs, outside the installed plugin. `start-work` defaults to the draft PR description for medium, large, or multi-session plans and follows existing project conventions for alternative planning artifacts; it does not require a `docs/pipelines/` directory.
