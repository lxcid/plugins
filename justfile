# Local development recipes. Run `just` for the list.
#
# The repo-wide checks that CI runs live in moon.yml. The recipes here are local
# conveniences that drive the host CLIs, never run in CI, and only sequence
# commands that README.md already documents, so `just` stays optional.

# List the available recipes.
default:
    @just --list

# Both hosts install a copy of the package, so edits under plugins/devloop reach
# an installed plugin only once the marketplace and the package are read again.
# Each recipe below rebuilds that state from scratch: drop any existing lxcid
# registration, because `marketplace add` is a no-op once the name is taken and
# would leave a GitHub source shadowing this checkout; point the marketplace at
# this directory; install the package; and report what the host now has. Start a
# new session in that host afterwards to load it.

# Reinstall devloop into Claude Code and Codex from this working tree.
devloop-reinstall: devloop-reinstall-claude devloop-reinstall-codex

# Reinstall devloop into Claude Code from this working tree.
devloop-reinstall-claude:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v claude >/dev/null 2>&1; then
        echo "claude is not on PATH; skipping Claude Code" >&2
        exit 0
    fi
    claude plugin validate . --strict
    claude plugin validate plugins/devloop --strict
    # Both teardown commands exit 1 when there is nothing to remove, which is
    # the expected case on a first run.
    claude plugin uninstall devloop@lxcid --yes || true
    claude plugin marketplace remove lxcid || true
    claude plugin marketplace add "{{ justfile_directory() }}"
    claude plugin install devloop@lxcid
    claude plugin details devloop@lxcid

# Reinstall devloop into Codex from this working tree.
devloop-reinstall-codex:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v codex >/dev/null 2>&1; then
        echo "codex is not on PATH; skipping Codex" >&2
        exit 0
    fi
    # Codex ships no manifest validator, so a malformed catalog surfaces as a
    # failed `marketplace add`. `plugin remove` is idempotent; `marketplace
    # remove` exits 1 when nothing is registered.
    codex plugin remove devloop@lxcid
    codex plugin marketplace remove lxcid || true
    codex plugin marketplace add "{{ justfile_directory() }}"
    codex plugin add devloop@lxcid
    codex plugin list --marketplace lxcid
