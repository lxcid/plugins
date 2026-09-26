#!/usr/bin/env python3
"""Create or resume devloop reviewer sessions in Claude Code and Codex.

Each host keeps one reviewer session per worktree. Its id lives in
<git-dir>/devloop/review/<host>.json, so it is never committed and each
linked worktree gets its own reviewers.

Usage:
  reviewer.py review <host> --target <label> --prompt-file <file>
  reviewer.py respond <host> --prompt-file <file>
  reviewer.py status
  reviewer.py reset [<host>]

`review` invokes deep-review and answers in the findings schema. `respond`
continues the same session and answers in the responses schema. Both
print the structured result as JSON on stdout.
"""

import argparse
import json
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

HOSTS = ("claude", "codex")
PLUGIN_ROOT = Path(__file__).resolve().parents[3]
AGENT_FILE = PLUGIN_ROOT / "agents" / "reviewer.md"
CLAUDE_AGENT = "devloop:reviewer"
SKILL_INVOCATION = {"claude": "/devloop:deep-review", "codex": "$devloop:deep-review"}
# Bash is limited to git because Codex reviewers run in a read-only, offline
# sandbox; keeping Claude to the same local evidence keeps the two comparable.
CLAUDE_TOOLS = ["Bash(git *)", "Read", "Grep", "Glob", "Skill"]


def _object(properties):
    # Codex sends schemas in strict mode, which requires every property to be
    # listed as required and no additional properties.
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


FINDINGS_SCHEMA = _object(
    {
        "findings": {
            "type": "array",
            "items": _object(
                {
                    "id": {"type": "string"},
                    "blocking": {"type": "boolean"},
                    "summary": {"type": "string"},
                    "evidence": {"type": "string"},
                    "location": {"type": "string"},
                    "verdict": {"type": "string"},
                }
            ),
        }
    }
)

RESPONSES_SCHEMA = _object(
    {
        "responses": {
            "type": "array",
            "items": _object(
                {
                    "id": {"type": "string"},
                    "position": {"enum": ["confirm", "revise", "downgrade", "withdraw"]},
                    "blocking": {"type": "boolean"},
                    "evidence": {"type": "string"},
                }
            ),
        }
    }
)


class ReviewerError(Exception):
    pass


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def repo_paths():
    top = Path(git("rev-parse", "--show-toplevel"))
    state_dir = Path(git("rev-parse", "--absolute-git-dir")) / "devloop" / "review"
    return top, state_dir


def load_state(state_dir, host):
    path = state_dir / f"{host}.json"
    return json.loads(path.read_text()) if path.exists() else None


def save_state(state_dir, host, state):
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / f"{host}.json").write_text(json.dumps(state, indent=2) + "\n")


def read_agent():
    """Return the `codex:` frontmatter settings and the role body of reviewer.md."""
    text = AGENT_FILE.read_text()
    _, frontmatter, body = text.split("---\n", 2)
    codex, in_codex = {}, False
    for line in frontmatter.splitlines():
        if line == "codex:":
            in_codex = True
        elif in_codex and line.startswith("  ") and ":" in line:
            key, value = line.strip().split(":", 1)
            codex[key.strip()] = value.strip()
        else:
            in_codex = False
    return codex, body.strip()


def run(cmd, cwd):
    # Both CLIs read a piped stdin into the prompt, and a coordinator's tool
    # shell may leave one open.
    return subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)


def toml_string(value):
    # A JSON string without ASCII escaping is also a valid TOML basic string.
    return json.dumps(value, ensure_ascii=False)


def run_claude(top, session_id, resume, prompt, schema):
    cmd = ["claude", "-p", prompt, "--agent", CLAUDE_AGENT]
    # Pass the id explicitly: a claude launched from inside another Claude Code
    # session otherwise inherits that session's id from the environment.
    cmd += ["--resume", session_id] if resume else ["--session-id", session_id]
    cmd += ["--output-format", "json", "--json-schema", json.dumps(schema), "--allowed-tools", *CLAUDE_TOOLS]
    proc = run(cmd, top)
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise ReviewerError(f"claude exited {proc.returncode} without a JSON result:\n{proc.stderr or proc.stdout}")
    if result.get("is_error") or proc.returncode != 0:
        raise ReviewerError(f"claude reported an error: {result.get('result') or proc.stderr}")
    if result.get("session_id") != session_id:
        raise ReviewerError(f"claude answered as session {result.get('session_id')}, expected {session_id}")
    if "structured_output" not in result:
        raise ReviewerError("claude returned no structured output")
    return result["structured_output"]


def run_codex(top, session_id, prompt, schema):
    settings, role = read_agent()
    config = [arg for key, value in settings.items() for arg in ("-c", f"{key}={toml_string(value)}")]
    # Codex takes model, effort, sandbox and developer instructions from the
    # current invocation, not from the saved session, so every call repeats them.
    config += ["-c", f"developer_instructions={toml_string(role)}"]
    with tempfile.TemporaryDirectory() as tmp:
        schema_file, last_message = Path(tmp) / "schema.json", Path(tmp) / "last.json"
        schema_file.write_text(json.dumps(schema))
        # -s and -C belong to `codex exec` itself and must precede `resume`.
        cmd = ["codex", "exec", "-s", "read-only", "-C", str(top), *config]
        if session_id:
            cmd += ["resume", session_id]
        cmd += ["--json", "--output-schema", str(schema_file), "-o", str(last_message), prompt]
        proc = run(cmd, top)
        events = [json.loads(line) for line in proc.stdout.splitlines() if line.startswith("{")]
        started = next((e["thread_id"] for e in events if e.get("type") == "thread.started"), None)
        failure = next((e for e in events if e.get("type") in ("turn.failed", "error")), None)
        if proc.returncode != 0 or failure or started is None:
            raise ReviewerError(f"codex exited {proc.returncode}: {failure or proc.stderr.strip()}")
        # An unmatched resume silently starts a new thread, so check the id.
        if session_id and started != session_id:
            raise ReviewerError(f"codex started thread {started} instead of resuming {session_id}")
        try:
            return started, json.loads(last_message.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise ReviewerError(f"codex returned no structured output: {error}")


def ask(host, prompt, schema, target=None):
    top, state_dir = repo_paths()
    state = load_state(state_dir, host)
    if state and target and state["target"] != target:
        raise ReviewerError(
            f"the {host} reviewer belongs to target {state['target']!r}; run `reset {host}` to review {target!r}"
        )
    if not state and target is None:
        raise ReviewerError(f"no {host} reviewer session yet; run `review` first")
    if host == "claude":
        session_id = state["session_id"] if state else str(uuid.uuid4())
        output = run_claude(top, session_id, state is not None, prompt, schema)
    else:
        session_id, output = run_codex(top, state and state["session_id"], prompt, schema)
    if not state:
        save_state(state_dir, host, {"session_id": session_id, "target": target})
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    review = sub.add_parser("review")
    review.add_argument("host", choices=HOSTS)
    review.add_argument("--target", required=True)
    review.add_argument("--prompt-file", required=True, type=Path)
    respond = sub.add_parser("respond")
    respond.add_argument("host", choices=HOSTS)
    respond.add_argument("--prompt-file", required=True, type=Path)
    sub.add_parser("status")
    reset = sub.add_parser("reset")
    reset.add_argument("host", nargs="?", choices=HOSTS)
    args = parser.parse_args()

    try:
        if args.command == "status":
            _, state_dir = repo_paths()
            print(json.dumps({host: load_state(state_dir, host) for host in HOSTS}, indent=2))
        elif args.command == "reset":
            _, state_dir = repo_paths()
            for host in [args.host] if args.host else HOSTS:
                (state_dir / f"{host}.json").unlink(missing_ok=True)
        elif args.command == "review":
            prompt = f"{SKILL_INVOCATION[args.host]} {args.prompt_file.read_text()}"
            print(json.dumps(ask(args.host, prompt, FINDINGS_SCHEMA, args.target), indent=2))
        else:
            print(json.dumps(ask(args.host, args.prompt_file.read_text(), RESPONSES_SCHEMA), indent=2))
    except (ReviewerError, subprocess.CalledProcessError, FileNotFoundError) as error:
        print(f"reviewer.py: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
