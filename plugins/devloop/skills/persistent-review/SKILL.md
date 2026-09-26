---
name: persistent-review
description: Coordinate independent reviewers in Claude Code, Codex, or both, and reconcile their findings on evidence. Use when the user asks for an independent, persistent, second-opinion, or cross-model review of a branch, commit range, worktree, or PR, or asks to re-run such a review after fixes. Keeps each reviewer's session across rounds and returns PASS, BLOCKED, or NEEDS_HUMAN.
---

# Persistent Review

You are the coordinator. You run review rounds through persistent reviewer sessions and reconcile what they find. You do not review the code yourself, and you do not edit the reviewers' findings.

- The reviewer role is `agents/reviewer.md` in this plugin.
- The review methodology is the `deep-review` skill. Do not restate or adapt it in prompts.
- `scripts/reviewer.py` in this skill's directory creates and resumes the sessions. Every command below runs it from inside the target repository.

Requested review: `$ARGUMENTS`

## Requirements

- Each requested host's CLI is installed and authenticated, and devloop is installed in that host. Reviewers discover `deep-review` through the installed plugin.
- The script's child processes call model APIs. Run it with network access; in Codex, that means a sandbox escalation.
- Reviewers reuse each host's own settings, and the script grants nothing.
  - **Claude:** headless Claude denies any Bash command its settings do not allow. The project's `.claude/settings.json` must allow `Bash(git *)`, and the test command if reviewers should run tests. deep-review runs git as `git -C <path> …`, which per-subcommand rules such as `Bash(git diff *)` do not match. Claude applies project settings only in folders it trusts.
  - **Codex:** reads work in any sandbox. Running tests needs a writable sandbox, for example `sandbox_mode = "workspace-write"` in the project's `.codex/config.toml`.
- Codex reviewers read `AGENTS.md`. Claude reviewers read `CLAUDE.md`, and fall back to `AGENTS.md` only when there is no `CLAUDE.md`. So the one case to catch is a project with both files where `CLAUDE.md` neither links to nor imports `AGENTS.md`. Tell the user before reviewing, because the Claude reviewer would miss the rules in `AGENTS.md`.

## 1. Resolve Reviewers And Target

- Reviewers: `claude`, `codex`, or both. If the request does not say, ask.
- Target: resolve it to something both reviewers can read locally, because a reviewer may have no network. Codex's sandbox blocks network by default.
  - A branch against its base, a commit range, or a worktree can be used as is.
  - For a PR, fetch its head into a local ref, then review that ref against the PR's base. Put the PR's title and body in the prompt as the claimed intent.
- Uncommitted changes: decide whether they are in scope, asking the user if they have not said. Reviewers cannot ask.
- Label the target briefly, for example `feature vs main`. The label ties the sessions to the target.

## 2. Independent Review

Write the review prompt. It names the target with the head SHA, states the uncommitted-changes decision and "do not ask", includes any claimed intent, and asks for Phase 1 findings only. Give each reviewer its own copy that differs only in the id prefix, `C` for Claude and `X` for Codex, so ids never collide.

Run each reviewer with its prompt file:

```bash
python3 <skill-dir>/scripts/reviewer.py review <host> --target "<label>" --prompt-file <file>
```

Run it in the foreground and wait for it, with the longest timeout your shell tool allows. A review can take several minutes. With two reviewers, start both in one command so they run in parallel, for example `… > claude.json & … > codex.json & wait`. Do not end your turn while a reviewer is still running. A headless session exits when its turn ends and stops any background command with it.

The script invokes deep-review for you and prints the findings as JSON. If it says the reviewer belongs to another target, confirm with the user, then run `reset <host>` and try again.

Do not show either reviewer the other's findings until both have finished this round. Independent first passes are the point of having two.

With one reviewer, skip to step 5: every blocking finding is CONFIRMED, and every other finding is NON_BLOCKING.

## 3. Cross-Check

A finding is material when its reviewer marked it blocking. Send each reviewer the other's material findings, with their evidence:

```bash
python3 <skill-dir>/scripts/reviewer.py respond <host> --prompt-file <file>
```

Ask it to inspect the evidence itself and answer each finding with `confirm`, `revise`, `downgrade`, or `withdraw`. A reviewer's own finding that matches one it is shown counts as a confirmation.

- `confirm`, or `revise` that stays blocking: the finding is CONFIRMED.
- `downgrade` or `withdraw`: the finding is disputed. Go to step 4.

## 4. Challenge

For each disputed finding, resume its original reviewer with the objection and the objector's evidence. Ask it to respond on the named findings only, and not to change position merely because another reviewer disagrees.

- `withdraw`: WITHDRAWN.
- `downgrade`, or `revise` to non-blocking: NON_BLOCKING.
- `confirm`, or `revise` that stays blocking: send that reply back to the objector once.
  - If the objector now confirms, the finding is CONFIRMED.
  - Otherwise it is UNRESOLVED.

Batch every disputed finding for the same reviewer into one message. Stop after that one exchange: do not vote, and do not keep relaying until someone yields. Two reviewers who still disagree after re-reading the evidence are the operator's call.

## 5. Outcome

Non-blocking findings from either reviewer are NON_BLOCKING and are reported without reconciliation.

| Outcome     | When                                                                |
| ----------- | ------------------------------------------------------------------- |
| NEEDS_HUMAN | any material finding is UNRESOLVED                                  |
| BLOCKED     | no UNRESOLVED findings, and at least one CONFIRMED blocking finding |
| PASS        | no UNRESOLVED and no CONFIRMED blocking findings                    |

Report the outcome first. Then list each material finding with its disposition, location, and the evidence from each reviewer. For UNRESOLVED findings, set out both positions so the operator can decide. List NON_BLOCKING findings last, briefly. Name the reviewers and the target SHA reviewed.

## 6. Re-Review After Fixes

A BLOCKED outcome keeps the sessions. After the main session fixes and tests, run step 2 again with the same label and a prompt that starts "Review the current work again", names the new head SHA, and asks the reviewer to re-check each earlier finding against the current state. The script resumes the same sessions, so each reviewer keeps its earlier reasoning as history, not as truth. Then reconcile as before.

Run `status` to see the stored sessions, and `reset [<host>]` to start a reviewer over.

## Failure

If the script fails, report its error and stop. Do not fall back to one reviewer, or retry on a new session, without asking.
