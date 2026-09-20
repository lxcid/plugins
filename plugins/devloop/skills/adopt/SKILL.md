---
name: adopt
description: Install devloop's engineering patterns into a repository's AGENTS.md, and update them safely on re-run. Use when the user asks to adopt, install, or set up devloop patterns or conventions in a project, to add an engineering-practice section such as design judgment or commit conventions to AGENTS.md, or to refresh previously adopted patterns to their latest version. Accepts one or more pattern ids, `all`, or no argument to choose from the catalog.
disable-model-invocation: true
---

# Adopt

Install one or more engineering patterns into the target repository's `AGENTS.md`, and keep previously installed ones current without destroying local edits.

Each pattern is a self-contained section stored in `references/<id>.md`. The reference file's YAML frontmatter carries its metadata; everything below the frontmatter is the exact text installed into `AGENTS.md`. Edit the reference file to change what the pattern says, and raise its `version` when you do.

Requested pattern: `$ARGUMENTS`

## Catalog

| id | Installs as | What it says |
| --- | --- | --- |
| `design-judgment` | `## Design Judgment` | Minimal necessary complexity; minimality is architectural, not line-count; operator direction doesn't remove the obligation to argue; the `likelihood × impact × recoverability × cost` edge-case test |
| `debugging-discipline` | `## Debugging Discipline` | A failed fix means an incomplete mental model; escalating commitment under uncertainty; read the dependency's source; name the falsifier before editing |
| `test-design` | `## Test Design` | TDD for behavior changes; lowest useful level with real contracts; over-stubbing is worse than no test; skipping is an explicit call |
| `writing-style` | `## Writing Style` | Comments only for non-obvious _why_; prose with one idea per sentence; shell output never column-padded |
| `commit-conventions` | `## Commits` | Conventional Commits; why-not-what bodies; never `--amend`, never `--no-verify`; fail loud over self-heal |
| `handoff-contract` | `## Handoff` | What every finished task reports back, including trade-offs taken, drift noticed, tests skipped, and what you could not verify |

These are stances, not repository facts. They transfer as written and need no knowledge of the target repo.

## Ground Rules

1. Never edit a managed section's text in place in `AGENTS.md`. Change the reference file and re-run, so the installed copy and its recorded hash stay consistent.
2. Treat a locally edited section as user-owned. Ask before replacing it; never silently overwrite.
3. Never downgrade. If the installed version is newer than the reference file's, report it and leave it alone.
4. Adopt only what was asked for. Do not install adjacent patterns because they seem related.

## Phase 1: Resolve What To Adopt

- One or more ids: adopt exactly those. Reject an unknown id by name and list the valid ones.
- `all`: adopt every id in the catalog, in catalog order.
- No argument: show the catalog with each pattern's current installed state, ask which to adopt, and wait for an answer.

## Phase 2: Locate The Target

`AGENTS.md` at the repository root is the target. If it does not exist, create it with an `# Agent Guide` heading and a one-line statement that it holds instructions for coding agents in this repository.

If `CLAUDE.md` exists as a regular file with different content, do not touch it — say so and let the user decide. This skill does not manage the symlink.

## Phase 3: Decide, Per Pattern

A managed section is delimited by markers that record its id, version, and a hash of the installed body:

```markdown
<!-- devloop:design-judgment v1 sha:a1b2c3d4 -->

## Design Judgment

...
<!-- /devloop:design-judgment -->
```

Compute the installed body's hash, and the reference file's, with the same recipe:

```bash
awk -v id=design-judgment '$0 ~ "^<!-- devloop:" id " "{f=1;next} $0 ~ "^<!-- /devloop:" id " -->$"{f=0} f' AGENTS.md | perl -0777 -pe 's/\A\s+|\s+\z//g' | shasum -a 256 | cut -c1-8

perl -0777 -ne 'print $1 if /^---\n.*?\n---\n(.*)\z/s' references/design-judgment.md | perl -0777 -pe 's/\A\s+|\s+\z//g' | shasum -a 256 | cut -c1-8
```

Then act on the pair (recorded version vs. reference version, recorded hash vs. installed hash):

| Installed | Body | Action |
| --- | --- | --- |
| absent | — | Install it. Report as added |
| older | matches recorded hash | Replace with the new text. Report as updated, old version → new |
| older | differs | **Conflict.** The section was edited locally and the pattern also moved. Show the differences, then ask: replace with the new version, keep the local text, or merge by hand. Wait for an answer |
| same | matches | Nothing to do. Report as current |
| same | differs | Locally edited with nothing newer available. Leave it. Report as locally modified |
| newer | — | Installed copy came from a newer devloop. Leave it and report; do not downgrade |

A body that differs only by whitespace or line wrapping is still a difference the hash will catch, usually because the target repository's formatter rewrote it. Treat it as a conflict and ask — a false question is cheaper than a silent overwrite.

If `AGENTS.md` already contains a heading matching the pattern's `section` but no devloop markers, do not add a second one. Show the existing section, say which parts the pattern would add, and ask whether to replace it, merge into it, or skip.

## Phase 4: Apply

Write each section with its open marker, the reference body, and its close marker, with the reference file's version and the freshly computed hash.

- Append new sections in catalog order, after the last devloop-managed section, or at the end of the file.
- Leave the position of already-installed sections alone. Updating a pattern rewrites its body in place; it does not move it.
- If the reference frontmatter lists a `related` pattern that is not installed and will not be installed in this run, drop any Markdown link to that section and keep the prose. A live document should not carry dead anchors.
- Preserve everything outside the markers untouched.

## Phase 5: Report

List each requested pattern and its outcome: added, updated (with the version change), current, locally modified, or skipped with the reason. Name any conflict the user resolved and how.

If the repository has a Markdown formatter, run it on `AGENTS.md`, then recompute and rewrite each affected hash so the recorded value matches the formatted text. Skipping this makes the next run report a false conflict on every section.

Commit the change if the user asked for it; otherwise leave it staged for review.
