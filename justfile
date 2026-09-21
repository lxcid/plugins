# Local development recipes. Run `just` for the list.
#
# The repo-wide checks that CI runs live in moon.yml. The recipes here are local
# conveniences that drive the host CLIs, never run in CI, and only sequence
# commands that README.md already documents, so `just` stays optional.

# List the available recipes.
default:
    @just --list

# Claude Code installs a copy of the package, so edits under plugins/devloop
# reach an installed plugin only once the marketplace and the package are read
# again. This recipe rebuilds that state from scratch: validate both manifests,
# drop any existing lxcid registration so a GitHub source cannot shadow this
# checkout, point the marketplace at this directory, and install the package.
# Start a new session afterwards to load it.

# Reinstall devloop into Claude Code from this working tree.
devloop-reinstall:
    #!/usr/bin/env bash
    set -euo pipefail
    claude plugin validate . --strict
    claude plugin validate plugins/devloop --strict
    # Both teardown commands exit 1 when there is nothing to remove, which is
    # the expected case on a first run.
    claude plugin uninstall devloop@lxcid --yes || true
    claude plugin marketplace remove lxcid || true
    claude plugin marketplace add "{{ justfile_directory() }}"
    claude plugin install devloop@lxcid
    claude plugin list
