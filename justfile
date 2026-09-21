# Local development recipes. Run `just` for the list.
#
# The repo-wide checks that CI runs live in moon.yml. The recipes here are local
# conveniences that drive the host CLIs, never run in CI, and only sequence
# commands that README.md already documents, so `just` stays optional.
#
# One module per plugin package, named after it, so recipes read the way the
# skills do: `just devloop::reinstall`, or `just devloop reinstall`. A single
# colon is not available, because just reads `:` as the recipe separator.

mod devloop

# List the available recipes, module recipes included.
default:
    @just --list --list-submodules
