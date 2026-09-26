---
name: adopt
description: Install devloop's engineering patterns into a repository's AGENTS.md, and update them safely on re-run. Use when the user asks to adopt, install, or set up devloop patterns or conventions in a project, to add an engineering-practice section such as design judgment or commit conventions to AGENTS.md, or to refresh previously adopted patterns to their latest version. Accepts one or more pattern ids, `all`, or no argument to choose from the catalog.
disable-model-invocation: true
---

# Adopt

Install one or more engineering patterns into the target repository's `AGENTS.md`, and keep previously installed ones current without destroying local edits.

Each pattern is a self-contained section stored in `references/<id>.md`. The reference file's YAML frontmatter carries its id, version, and section heading; everything below the frontmatter is the text installed into `AGENTS.md`. Edit the reference file to change what the pattern says, and raise its `version` when you change a pattern that has already shipped.

Requested pattern: `$ARGUMENTS`

## Catalog

| id | Installs as | What it says |
| --- | --- | --- |
| `design-judgment` | `## Design Judgment` | Minimal necessary complexity; minimality is architectural, not line-count; operator direction doesn't remove the obligation to argue; weigh edge-case likelihood, impact, recoverability, and cost together while preserving required invariants; prefer derived values over mutable copies; separate domain calculations from caching and scheduling; fail loud over self-heal |
| `debugging-discipline` | `## Debugging Discipline` | A failed fix means an incomplete mental model; escalating commitment under uncertainty; read the dependency's source; name the falsifier before editing |
| `test-design` | `## Test Design` | TDD for behavior changes; lowest useful level with real contracts; over-stubbing is worse than no test; skipping is an explicit call |
| `writing-style` | `## Writing Style` | Comments only for non-obvious _why_; prose with one idea per sentence; shell output never column-padded |
| `commit-conventions` | `## Commits` | Conventional Commits; why-not-what bodies; amend only when explicitly asked; never skip hooks; inspect and fix commit failures before retrying |
| `handoff-contract` | `## Handoff` | What every finished task reports back, including trade-offs taken, drift noticed, tests skipped, and what you could not verify |

These are stances, not repository facts. They transfer as written and need no knowledge of the target repo.

## Ground Rules

1. Never edit a managed section's text in place in `AGENTS.md`. Change the reference file and re-run, so the installed copy and its recorded baseline stay consistent.
2. Treat any section that differs from its recorded baseline as user-owned. Ask before replacing it; never silently overwrite.
3. Never downgrade. If the installed version is newer than the reference file's, report it and leave it alone.
4. Touch nothing outside the markers of the patterns being installed. Not the user's prose, not their other sections, not the rest of the file.
5. Adopt only what was asked for. Do not install adjacent patterns because they seem related.

## Local Customization

Recommend placing repository-specific guidance immediately after the relevant pattern's closing marker, before the next managed section. Use a heading that describes the repository-specific guidance. Content outside the markers is preserved on re-run, so local additions do not mark the managed body as customized or block clean upstream updates. State any exception to a managed rule explicitly.

## Phase 1: Resolve What To Adopt

- One or more ids: adopt exactly those. Reject an unknown id by name and list the valid ones.
- `all`: adopt every id in the catalog, in catalog order.
- No argument: show the catalog with each pattern's current installed state, ask which to adopt, and wait for an answer.

## Phase 2: Locate The Target

`AGENTS.md` at the repository root is the target. If it does not exist, create it with an `# Agent Guide` heading and a one-line statement that it holds instructions for coding agents in this repository.

If `CLAUDE.md` exists as a regular file whose content differs from `AGENTS.md`, do not touch it — say so and let the user decide. This skill does not manage the symlink.

## Phase 3: Decide, Per Pattern

A managed section is delimited by markers recording its id, version, and a baseline hash:

```text
<!-- devloop:design-judgment v1 sha:a1b2c3d4 -->
## Design Judgment
...
<!-- /devloop:design-judgment -->
```

**`sha` is the hash of the upstream text, not of whatever is currently installed.** It is the fingerprint of the replaceable baseline: the reference body exactly as this skill would write it. A section whose body still hashes to its recorded baseline is untouched upstream content and can be replaced freely. A section whose body hashes to anything else carries local content — whether merged in at install or edited afterwards — and is user-owned.

That distinction is the whole safety mechanism. Never re-hash a body to make it match; the mismatch is the signal.

Compute the installed body's hash with the same trim and digest used for the baseline in Phase 4. The awk program spells the current line `$(0)`, because Claude Code replaces a dollar sign followed by a digit with the skill's arguments:

```bash
# installed body
awk -v id=design-judgment '$(0) ~ "^<!-- devloop:" id " "{f=1;next} $(0) ~ "^<!-- /devloop:" id " -->$"{f=0} f' AGENTS.md | perl -0777 -pe 's/\A\s+|\s+\z//g' | shasum -a 256 | cut -c1-8
```

Then act on the pair — recorded version against the reference version, installed body against the recorded baseline:

| Version | Body | Action |
| --- | --- | --- |
| absent | — | Install it. Report as added |
| older | matches baseline | Pure upstream content. Replace it. Report as updated, old version → new |
| older | differs | **Conflict.** The section carries local content and the pattern also moved. Show the differences, then ask: replace with the new version, keep the local text, or merge by hand. Wait for an answer |
| same | matches baseline | Nothing to do. Report as current |
| same | differs | Customized, nothing newer available. Leave it. Report as locally modified |
| newer | — | Installed copy came from a newer devloop. Leave it and report; do not downgrade |

When the user keeps their local text instead of taking an update, rewrite only the marker: record the new version and the new baseline hash, and leave the body alone. The section stays flagged as customized, so it will not prompt again at this version but will ask again at the next one.

A body that differs only by whitespace or line wrapping is still a difference, usually because the target repository's formatter rewrote it. Treat it as a conflict and ask — a false question is cheaper than a silent overwrite.

If `AGENTS.md` already contains a heading matching the pattern's `section` but no devloop markers, do not add a second one. Show the existing section, say which parts the pattern would add, and ask whether to replace it, merge into it, or skip.

## Phase 4: Apply

For each pattern being written, take the reference body, format it if the project has a Markdown formatter, and hash the result. That is the baseline, and it goes in the marker.

Format the body on its own — write it to a temporary file, run the project's formatter on that file, and read it back. Do not run a formatter over `AGENTS.md`. Reformatting the whole document rewrites the user's own prose and can normalize a customized section back into something that hashes as untouched, which silently converts local content into replaceable content.

Hash that temporary file after formatting, using the same trim and digest as the installed-body check. Here, `formatted_body` is the path to that file:

```bash
perl -0777 -pe 's/\A\s+|\s+\z//g' "$formatted_body" | shasum -a 256 | cut -c1-8
```

- Write the section as: open marker, body, close marker.
- **On a plain install or a clean update**, the body is the formatted reference body, and it matches the baseline in the marker.
- **On a merge**, the body is the merged text but the marker still records the baseline hash of the pure reference body. The section therefore reads as customized from that moment on, and every future update asks before touching it. Merging is permission to add the pattern's content now, not permission to delete the user's content later.
- Append new sections in catalog order, after the last devloop-managed section, or at the end of the file.
- Leave the position of already-installed sections alone. Updating a pattern rewrites its body in place; it does not move it.
- Change nothing outside the markers of the patterns you are writing.

## Phase 5: Report

List each requested pattern and its outcome: added, updated (with the version change), current, locally modified, or skipped with the reason. Name any conflict the user resolved and how, and say plainly when a section was left carrying local content.

Commit the change if the user asked for it; otherwise leave it for review.
