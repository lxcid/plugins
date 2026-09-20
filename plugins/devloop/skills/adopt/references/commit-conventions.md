---
id: commit-conventions
version: 1
section: Commits
---

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for **all** commits, including bot-emitted: `<type>(<scope>): <subject>`.

- `feat(<scope>):` — user-visible new behavior.
- `fix(<scope>):` — bug fix.
- `chore(<scope>):` — refactors, version bumps, tooling that doesn't alter behavior.
- `ci(<scope>):` — only for CI workflow changes.
- `docs(<scope>):` — docs-only.

Scopes are this repository's own top-level units. Use a combined `chore(a,b): …` form only when a change genuinely spans both.

- Summary in imperative mood, lower case, no trailing period.
- Body explains _why_, not _what_. The diff shows what changed.
- One logical change per commit. Mechanical changes such as a reformat go in their own commit.
- Never `--amend` unless explicitly asked; create a new commit. Hook failure means the commit didn't happen, so an amend would modify the _previous_ commit and may destroy work.
- Never `--no-verify` to skip hooks. If a commit or hook fails, inspect and report the failure, then fix its cause before retrying.
