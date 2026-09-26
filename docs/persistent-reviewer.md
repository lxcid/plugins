# Persistent reviewer: investigation

What Claude Code and Codex support today for devloop's persistent reviewer, and the smallest design those capabilities allow. The design follows the evidence; nothing below is implemented yet.

- Claude Code findings were verified on Claude Code 2.1.283 by running headless sessions against a scratch repository and reading their transcripts.
- Codex findings come from the Codex CLI 0.157.1 `--help` output and its Rust source at `openai/codex@e72da2b`. Codex was not run: this environment has no OpenAI credentials, and `developers.openai.com` is blocked. Every Codex claim is marked source-read, not verified.

## Claude Code

### 1. Invoking a plugin agent non-interactively

`claude -p "<prompt>" --agent devloop:reviewer` runs the plugin agent as the session's main thread. The agent's body replaces the default system prompt. Tool restrictions in the agent's `tools` and `disallowedTools` apply: an agent without `Write` could not write a file.

Verified with a fixture agent whose prompt held a codeword. The transcript records `agent-setting: devloop:reviewer`.

### 2. `--agent` with plugin agents

Both `--agent reviewer` and `--agent devloop:reviewer` resolve a plugin agent. The transcript stores the scoped name either way. Use the scoped name, so another plugin's `reviewer` cannot shadow it.

### 3. Session IDs and resume

- `--session-id <uuid>` sets the ID at creation. The coordinator can generate the UUID itself and know it before the run. The JSON result echoes it as `session_id`.
- `--resume <uuid>` continues that same session. The ID does not change unless `--fork-session` is passed.
- Resume restores the conversation, the agent, and the agent's model without repeating `--agent`.
- **Hazard:** a `claude -p` launched from inside a Claude Code session inherits `CLAUDE_CODE_SESSION_ID`. Without `--session-id`, the child reused the parent's session ID. Passing `--session-id` overrides the inherited value, so the coordinator must always pass it.

### 4. Named sessions

`-n <name>` names a session, and `--resume <name>` resumes it. Names are display labels with no uniqueness guarantee across worktrees or repeated runs. The UUID is the canonical handle; a name is optional decoration.

### 9. Discovering deep-review

- The plugin skill is listed as `devloop:deep-review`.
- The agent frontmatter `skills:` field is documented as preloading skills in `--agent` mode, but 2.1.283 does not apply it. With either `deep-review` or `devloop:deep-review`, the skill body never reached the transcript. Do not rely on it.
- Starting the prompt with `/devloop:deep-review <arguments>` works in `-p` mode. It injects the full `SKILL.md` as a user message, and that message stays in the transcript, so every resumed round still has the methodology.
- deep-review asks the user to pick a target when the request is missing or ambiguous, and asks whether to include uncommitted changes. A headless reviewer has nobody to ask. The coordinator must name the target and state the uncommitted-changes decision. With both stated, the reviewer reviewed without asking.

### 10. Project instructions

- `CLAUDE.md` loads as project instructions.
- `AGENTS.md` loads natively only when there is no `CLAUDE.md`. With both present and no import, only `CLAUDE.md` loaded.
- A project whose rules live in `AGENTS.md` must symlink `CLAUDE.md` to it, as this repository does, or import it with `@AGENTS.md`. The reviewer agent must not copy project rules.

### 11. Structured output

`--json-schema '<schema>'` with `--output-format json` returns the validated object as `structured_output` and its text as `result`. Each resumed turn can pass a different schema: the first round used a findings schema and the challenge round a dispositions schema, in the same session.

### Other Claude observations

- The agent's `model:` is honoured, and `--model` overrides it.
- In `-p` mode, Bash commands need `--allowed-tools`, for example `"Bash(git *)"` and `"Bash(gh *)"`. Anything else is denied and listed in `permission_denials`.
- A Claude Code coordinator could instead spawn the reviewer as an in-session subagent and continue it with `SendMessage`. That persists only within the coordinator's own session, and a Codex coordinator cannot use it. The CLI path works from either host.
- A small model folded under a single challenge: it withdrew the challenged finding and also an unchallenged one. Reviewer quality depends on the model, and the challenge prompt should name only the findings under dispute.

### Claude round trip with the real agent

`plugins/devloop/agents/reviewer.md` ran on its configured model, Opus, against a scratch branch that added `divide` and `safe_divide`. All three rounds used one session ID.

1. **First review.** `/devloop:deep-review` with an explicit target and a findings schema. It returned four non-blocking findings with line references. It also said plainly that a `gh` call was denied, which is how the `Bash(gh *)` requirement surfaced.
2. **Challenge.** It was resumed with another reviewer's objection to C1 and a dispositions schema. It re-checked the code, accepted the part of the objection that held, and downgraded C1 rather than withdrawing it. It gave evidence for each point and answered only about C1.
3. **Re-review.** After a new commit removed `safe_divide`, it was resumed with "review the current work again". It inspected the new commit, marked C1 and C2 resolved, and narrowed C3 to what remained.

The three rounds cost about $0.80 in total on a two-file repository.
