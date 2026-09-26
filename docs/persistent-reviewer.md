# Persistent reviewer: investigation

What Claude Code and Codex support today for devloop's persistent reviewer, and the design those capabilities allow.

- **Claude Code findings are verified.** They come from running headless Claude Code 2.1.283 sessions against a scratch repository and reading their transcripts.
- **Codex findings are mostly source-read.** They come from the Codex CLI 0.157.1 `--help` output and its Rust source at `openai/codex@e72da2b`. The installed CLI confirmed three things: the argument order, the `thread.started` event, and the stored session settings. It never reached a model, because this environment has no OpenAI credentials and blocks `api.openai.com` and `developers.openai.com`. Each Codex claim below is marked verified or source-read.

## Answers

| # | Question | Claude Code | Codex |
| --- | --- | --- | --- |
| 1 | Run the reviewer non-interactively | `claude -p --agent devloop:reviewer` | `codex exec`, with the role passed as `developer_instructions` |
| 2 | `--agent` with a plugin agent | Works, bare or scoped name | No equivalent: roles are subagent-only, and plugins cannot ship them |
| 3 | Session IDs | Caller sets it with `--session-id`; `--resume` keeps it | `thread.started.thread_id` in `--json` output; `exec resume <id>` |
| 4 | Names or IDs | IDs; names are display labels | IDs; exec cannot name a thread |
| 5 | GPT-5.6 Sol | not applicable | `-c model="gpt-5.6-sol"`; the slug is in Codex's model list |
| 6 | Reasoning effort | not applicable | `-c model_reasoning_effort="high"`, repeated on every resume |
| 7 | Resume | `--resume <id>` restores conversation, agent, and model | `codex exec … resume <id>` restores conversation only; settings come from the call |
| 8 | Custom agent equivalent | Plugin agent file | None usable; `developer_instructions` from the same agent file |
| 9 | deep-review discovery | `/devloop:deep-review` in the prompt | `$devloop:deep-review` in the prompt |
| 10 | Project instructions | `CLAUDE.md`; `AGENTS.md` only when `CLAUDE.md` is absent | `AGENTS.md` from repository root to cwd; `CLAUDE.md` only if configured |
| 11 | Structured output | `--json-schema` gives `structured_output` | `--output-schema` gives the last message as JSON, in strict mode |
| 12 | Custom persistence | Needed. Codex IDs cannot be chosen or named, so something must store them. One small file per host under the git directory is enough. | same |

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

## Codex

### 1 and 8. Reviewer role

Codex supports custom agent roles, but only for subagents.

- Roles are defined as `[agents.<name>]` in config, or as TOML files under `.codex/agents/`.
- Only spawn paths apply them; no `codex exec` flag or config key makes a role the main agent (source-read: `core/src/agent/role.rs`, `agent/child_config.rs:290`, `agent/control/spawn.rs:428`).
- Plugin manifests have no `agents` key (source-read: `core-plugins/src/manifest.rs:45-70`).

The reviewer role therefore reaches Codex as `developer_instructions`, read from the body of the same `agents/reviewer.md`. Verified: Codex parsed the generated multi-line value and stored it as the session's developer message.

### 3 and 7. Session IDs and resume

- The first `--json` event is `{"type":"thread.started","thread_id":"<uuid>"}`. Verified on the installed CLI, which emitted it before contacting the model.
- The caller cannot choose the ID, and exec cannot name a thread (source-read: `app-server-protocol/src/protocol/v2/thread.rs:62-135`).
- `codex exec -C <dir> [-c …] resume <id> --json --output-schema <file> -o <file> "<prompt>"` resumes the thread. Exec-level options such as `-C` and `-s` must come before `resume`. Verified: the CLI rejects `resume <id> -s read-only` with "unexpected argument".
- Resuming an unknown UUID fails with "no rollout found". Verified. A thread name or `--last` that matches nothing silently starts a new thread (source-read: `exec/src/lib.rs:1017-1025`), so only UUIDs are safe, and the caller should compare IDs.
- **Resume restores the conversation only.** Model, reasoning effort, sandbox, approval, cwd, and developer instructions all come from the current invocation (source-read: `exec/src/lib.rs:1386-1412`). A resume without them runs on defaults. `gpt-5.6-sol` defaults to `low` effort in Codex's model list, so a bare resume would quietly lower the reviewer's reasoning.

### 5 and 6. Model and reasoning effort

`model` and `model_reasoning_effort` are ordinary config keys, settable with `-c` on both `exec` and `exec resume`. `gpt-5.6-sol` is in the bundled model list and supports `high`. Verified: the stored session recorded `model: gpt-5.6-sol` and `effort: high`.

### 9. Discovering deep-review

- Skills are discovered from installed plugins, `.agents/skills` and `.codex/skills` in the project, and the user's skill directories.
- Plugin skills are named `devloop:deep-review` (source-read: `ext/skills/src/loader/namespace.rs`).
- A `$devloop:deep-review` mention in the prompt injects the full `SKILL.md`, and works in `codex exec` (source-read: `skills/src/mentions.rs`, `ext/skills/src/host_prompt.rs:76-96`).
- A path-linked mention only disambiguates among discovered skills, so the plugin must be installed.

### 10. Project instructions

In each directory from the repository root down to cwd, the first of `AGENTS.override.md`, `AGENTS.md`, or a configured fallback name loads (source-read: `core/src/agents_md.rs`). `CLAUDE.md` is not a default fallback. The instructions reload on every turn, including after resume.

### 11. Structured output

`--output-schema <file>` sends the schema in strict mode. The API requires `additionalProperties: false` and every property listed as required (source-read: `codex-api/src/common.rs:392-410`). The result is the final agent message's JSON text, also written to the `-o` file. The schema applies per turn, and `exec resume` accepts it.

### Other Codex observations

- `codex exec` defaults to approval `never`. Without `-s`, the sandbox comes from config `sandbox_mode`. If that is unset, it is `workspace-write` for a trusted project and `read-only` otherwise. Neither mode allows network by default (source-read), so `gh` will not work inside a Codex reviewer.
- Codex reads a piped stdin into the prompt. Verified: it printed "Reading additional input from stdin". A coordinator must close the child's stdin; `claude -p` behaves the same way.
- No environment variable links a child `codex exec` to a parent Codex session, but a child shares the parent's `CODEX_HOME`, which holds its config and auth (source-read).
- `codex exec review` is Codex's own review mode. Using it would replace deep-review, so the design does not.

## Design

The pieces map onto the requested separation:

- **deep-review** stays the only statement of how to review. Nothing else restates it.
- **`agents/reviewer.md`** is the reviewer role, and the one place its settings live:
  - Claude reads it natively. Its `model: opus` and disallowed edit tools apply.
  - Codex gets its body as `developer_instructions`, and its `codex:` frontmatter as `-c` settings: `gpt-5.6-sol` at `high` effort.
  - `claude plugin validate --strict` accepts the extra frontmatter block, and Claude ignores it.
- **`skills/persistent-review/SKILL.md`** tells the current session how to coordinate: an independent first round, a cross-check of blocking findings, one challenge exchange per dispute, the dispositions, and the outcome rule.
- **`skills/persistent-review/scripts/reviewer.py`** holds the host mechanics that an agent would otherwise have to reconstruct correctly every round:
  - the explicit Claude session ID;
  - Codex's repeated settings and its argument order;
  - closed stdin;
  - the ID check on every resume;
  - the two response schemas. It is Python standard library only.

Session state is one JSON file per host in `<git-dir>/devloop/review/`, holding the session ID and the target label.

- It sits under the git directory, so it is never committed and needs no `.gitignore` entry.
- Each linked worktree gets its own reviewers.
- Codex IDs cannot be derived or named, which is why a file exists at all.
- One file per host lets the two first-round reviews run in parallel without racing on a shared file.

Reviewers run under each host's own permission configuration, so a project decides whether they may run tests.

- **Claude.** The script passes only `--allowed-tools "Bash(git *)"`, because headless Claude denies any Bash command nothing allows, and deep-review cannot read a diff without git.
  - Verified: the flag adds to the project's `.claude/settings.json` allow rules rather than replacing them.
  - Verified: those project rules apply only in a folder Claude trusts. In an untrusted folder, a project-allowed test command was still denied.
- **Codex.** The script passes no `-s`, so the sandbox comes from the user's or project's Codex config, as for any other Codex session.
  - Running tests needs `workspace-write`.
  - Codex has no mode that runs commands but forbids edits, so a Codex reviewer allowed to run tests relies on its role, not its sandbox, to leave files alone.
- **Claude file edits.** The agent's disallowed `Edit` and `Write` tools stay in place whatever the settings say.

Codex's sandbox blocks network by default, so the coordinator resolves PR targets into local refs and passes the PR body as intent.

### Verified end to end

- **Claude, through the script and an installed plugin.** A first round found the planted bug as blocking. A cross-check confirmed the matching Codex-style finding and downgraded a debatable one with evidence. That is the dispute a challenge round would take back to its originator.
- **Codex, against a fake `codex`.** The fake emits the real event shapes. The script's create, resume, ID mismatch, turn failure, target mismatch, and missing-session paths all behave as designed. The generated arguments were also accepted by the real CLI.

### Not verified

- **A Codex reviewer answering a real prompt.** This covers applying deep-review, following the role, and resuming with context. It needs OpenAI credentials and network access.
- **Whether a Codex reviewer keeps the injected skill text in its history after resume.** The script re-invokes deep-review on every review round anyway. Challenge rounds rely on the history.
- **Running the script from inside a sandboxed Codex coordinator.** The children need network access, and a nested `codex exec` inside a sandbox was not traced.
- **The full coordinator loop with both hosts live.**
