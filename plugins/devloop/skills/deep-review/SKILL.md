---
name: deep-review
description: Deep analysis and review of a PR or branch to catch inconsistency, redundancy, flaws, regressions, accidental complexity, weak abstractions, and lazy fixes. Use when asked to decide whether every change earns its place, review a PR skeptically, make a PR smaller/cleaner, or propose minimal fixes after review. Accepts a PR number/URL, or reverse-lookups the current branch's GitHub PR before falling back to a main-branch diff.
---

# Deep Review

Do a deep analysis and review of the PR or branch. Catch inconsistency, redundancy, flaws, regressions, and accidental complexity.

Review every change for correctness, including regressions, broken contracts, and invalid states. Assess whether it aligns with the current design or a clearly justified future direction, and whether any added complexity is necessary and justified. Identify what can break, where inconsistencies arise, and what could be removed or simplified while meeting the specification and requirements, without introducing unintended behavior changes or regressions. Distinguish complexity inherent in the problem from complexity introduced by the design or implementation. Challenge abstractions, state, and new concepts whose maintenance burden outweighs their benefit, and ask whether a simpler approach could meet the same requirements.

Make sure every change earns its place without introducing accidental complexity.

Pay attention to state, which can introduce complexity through ownership, synchronization, and transitions. Question what must be stored versus what can be derived, who owns each piece of state, and which transitions are valid. Look for duplicated or contradictory state, synchronization burdens, and transitions that can leave the system in an invalid state. Prefer designs that minimize unnecessary state and make invalid states difficult to represent or reach.

Your job is not to make the PR pass by patching around problems. Your job is to decide whether each change deserves to exist.

Look for inconsistency, redundancy, regressions, accidental complexity, weak abstractions, and lazy fixes. Be especially skeptical of changes that add new concepts, flags, branches, helpers, migrations, or compatibility paths without a clear reason.

## Before Reviewing

1. Resolve the target:
   - If the user names an explicit file, path, or commit range, review that directly and skip PR discovery.
   - For a PR number or URL, run `gh pr view <N> --json title,body,baseRefName,headRefName,commits,files` for intent, then `gh pr diff <N>` for the actual patch. To read files at the PR's version instead of your working tree, `gh pr checkout <N>` first.
   - Without a PR, reverse-lookup the current branch's PR with `gh pr view --json title,body,baseRefName,headRefName,commits,files` (or `gh pr list --head "$(git branch --show-current)" --state all --json number,url,headRefName,baseRefName --limit 1` then `gh pr view <number> ...`), and fetch its patch with `gh pr diff` the same way.
   - Only if GitHub has no matching PR, diff against the base: `git diff $(git merge-base <base> HEAD)..HEAD`, using the PR's `baseRefName` when known and `main` only as the last resort. Run `git status --short` and say whether uncommitted changes are in scope.
   - The `files` list is metadata, not the patch — always read the diff itself.
2. Read the PR body and commit messages as the claimed intent; on a noisy branch, skim routine commits and focus on the ones that change behavior.
3. Read repo guidance that applies to the touched surface, especially agent guidance such as `AGENTS.md` or `CLAUDE.md`.
4. Read changed files in full when judging behavior or architecture; do not review only the diff hunk when surrounding code matters. On a large PR, triage by risk — behavior, schema, and auth first, mechanical churn last — and say so when you are sampling rather than reading everything.

Do this in two phases.

## Phase 1 - Review Only

Do not edit files.

Explain:

- what changed
- why it may have been changed
- whether it aligns with the current architecture or a clearly justified future direction
- what it breaks or risks breaking
- what is redundant or overcomplicated
- what should be removed, simplified, or redesigned

Also check:

- inconsistency between files, docs, tests, contracts, and naming
- half-finished renames or old and new shapes coexisting
- state that is stored when it could be derived, or cached with no clear authoritative source
- unclear state ownership or unnecessary synchronization between duplicated state
- data shapes or transitions that allow invalid or contradictory states
- duplicated validation, state, error handling, or abstractions
- tests that mock away the behavior they claim to protect
- docs drift for user-facing or agent-facing behavior

Before reporting, turn the same skepticism on your own findings: name what would falsify each one, then confirm it against the actual code. Drop or downgrade any finding that does not survive.

Deliver Phase 1 as findings first, ordered by practical severity: impact, likelihood, recoverability, and cost. Include file and line references. Use blunt verdicts: `keep`, `simplify`, `delete`, `redesign`, or `needs-evidence`; for `needs-evidence`, name the specific check that would resolve it. Flag pre-existing or unrelated problems separately, and do not fold them into the fix proposal or rewrite code the PR never touched. If there are no blocking findings, say that clearly and name the remaining risk.

## Phase 2 - Minimal Fix Proposal

Only after the review, propose minimal fixes. Do not edit files here either — this phase proposes, it does not apply. State once that these are reference proposals for reviewer judgment, not mandatory instructions, then give confident, concrete proposals.

Judge "minimal" against the current product need, any invariant it actually requires, the existing architecture, and any recorded architectural direction — not by diff size alone. Do not recommend a locally small patch that conflicts with the existing architecture or a recorded direction, or adds a temporary concept already known to be replaced. If the smallest credible on-path answer is deletion, deferral, or a larger redesign, say so plainly. Operator direction remains final, but surface and argue the architectural trade-off before treating it as settled.

Turn the same skepticism on your own proposals that Phase 1 turns on findings: red-team each suggested alternative as hard as the change it replaces. Name the conditions that would break it, and check them against measured reality rather than doctrine. If a proposal accumulates qualifiers or compensating patches as you write it, treat that as evidence the smaller design does not exist at this scope, and recommend the larger one plainly instead of shipping the appearance of minimal.

Prefer deletion, consolidation, or reverting bad changes over adding more code. Do not introduce new abstractions unless the existing design truly cannot handle the case.

For each suggestion, state the concrete edit, why it is the smallest credible option, and what it removes: lines, branches, concepts, duplicated state, or unnecessary vocabulary. Include tradeoffs or uncertainty when they matter, so the reviewer can use their own judgment and choose a better solution if one is available. Also name what should stay unchanged so good work does not get churned.

The goal is a smaller, cleaner PR where every change earns its place.
