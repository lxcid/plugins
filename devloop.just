# Recipes for the devloop package: `just devloop::reinstall`.
#
# This file sits at the repository root, which is also the marketplace root. A
# module's recipes run in the directory of their module file, so the relative
# paths below resolve against the root only while this file stays there;
# `justfile_directory()` is the root justfile's directory at any module depth.
#
# Both hosts install a copy of the package, so edits under plugins/devloop reach
# an installed plugin only once the marketplace and the package are read again.
# Each recipe below points the lxcid marketplace at this directory, reinstalls
# the package, and reports what the host now has. The hosts disagree on
# re-pointing an existing registration, so only the Codex recipe tears the
# marketplace down; see each recipe. Start a new session in that host afterwards
# to load it.

# Reinstall into Claude Code and Codex from this working tree.
reinstall: reinstall-claude reinstall-codex

# Reinstall into Claude Code from this working tree.
reinstall-claude:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v claude >/dev/null 2>&1; then
        echo "claude is not on PATH; skipping Claude Code" >&2
        exit 0
    fi
    claude plugin validate . --strict
    claude plugin validate plugins/devloop --strict
    # `plugin uninstall` exits 1 when nothing is installed, the expected case
    # on a first run. The registration itself is left alone: `marketplace add`
    # re-points an existing lxcid at this directory, while `marketplace remove`
    # reaches across scopes and would drop a project-scoped install.
    claude plugin uninstall devloop@lxcid --yes || true
    claude plugin marketplace add {{ quote(justfile_directory()) }}
    claude plugin install devloop@lxcid
    claude plugin details devloop@lxcid

# Reinstall into Codex from this working tree.
reinstall-codex:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v codex >/dev/null 2>&1; then
        echo "codex is not on PATH; skipping Codex" >&2
        exit 0
    fi
    # Codex ships no manifest validator, so a malformed catalog surfaces as a
    # failed `marketplace add`. Unlike Claude Code, `marketplace add` refuses a
    # registration that points elsewhere, so the teardown is required here.
    # `plugin remove` is idempotent; `marketplace remove` exits 1 when nothing
    # is registered.
    codex plugin remove devloop@lxcid
    codex plugin marketplace remove lxcid || true
    codex plugin marketplace add {{ quote(justfile_directory()) }}
    codex plugin add devloop@lxcid
    codex plugin list --marketplace lxcid
