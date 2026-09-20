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

1. Run `git status --short`. If staged, unstaged, or untracked changes exist and the user has not already decided their scope, pause and ask whether to include them in the review. Wait for an answer before reviewing. Keep any included local changes distinct from the committed target.
2. Resolve the target:
   - **Explicit file, path, or commit range:** review it directly; skip PR discovery.
   - **Explicit PR number or URL:** use `gh pr view` for its metadata and `gh pr diff` for its patch, passing the supplied number or URL to both.
   - **Branch, or no explicit target:** review the requested branch, defaulting to the current branch. Use `gh pr list --head <branch> --state open` for PR context only. Diff the branch's actual commit against the merge base with the user-specified base, the matching open PR's base, or the repository's default branch, in that order. Include local commits absent from the PR; never substitute an old closed or merged PR's patch.
3. For commit-based reviews, record the target SHA and read full files from that revision with `git show <sha>:<path>`. Fetch missing objects without switching, stashing, or resetting the user's checkout; use an isolated worktree if execution is needed. Keep the patch and file contents at the same revision, refreshing both if the target moves. Always read the actual diff, not just the file list.
4. Read the PR body and commit messages as the claimed intent, plus applicable repo guidance such as `AGENTS.md` or `CLAUDE.md`. Read changed files in full when surrounding code matters. On large changes, prioritize behavior, schema, and auth over mechanical churn, and disclose any sampling.

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
