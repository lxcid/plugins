# lxcid’s Public Plugins

Public plugins for Claude Code and Codex. The first plugin, `devloop`, packages development workflow skills for starting implementation work, reviewing PRs and branches, and adopting engineering patterns into a project. Opinionated setup, minimal and optional.

## Plugin configuration

One [plugin package](plugins/devloop/) is shared by Claude Code and Codex. The repository provides a public plugin marketplace named `lxcid` for each host. Codex displays it as “lxcid’s Public Plugins”:

- `.claude-plugin/marketplace.json` for Claude Code.
- `.agents/plugins/marketplace.json` for Codex.

Both catalogs currently list `devloop` at `./plugins/devloop`; additional public plugins can be added under `plugins/<name>/` and listed in both catalogs. Version `0.3.0` includes the `start-work`, `deep-review`, and `adopt` skills. Each application manages its own installed copy; installing, updating, or removing it in one application does not change the other.

### Start implementation work

After installing, invoke `/devloop:start-work 123` in Claude Code, or ask Codex to “Use devloop's start-work skill to implement issue 123.” An issue URL, another ticket reference, or a freeform task description also works.

The skill checks the request against current code and recent decisions, resolves scope, prepares a branch or worktree, and proceeds into implementation. For medium, large, or multi-session work, it defaults to the draft PR description for the evolving plan, or follows project conventions for a planning artifact linked from the PR. GitHub operations require the `gh` CLI authenticated to the target repository. See the [package README](plugins/devloop/README.md) for details.

### Review a PR or branch

After installing, invoke `/devloop:deep-review 123` in Claude Code, or ask Codex to “Use devloop's deep-review skill to review PR 123.” A PR URL, an explicit file or commit range, or the current branch also works.

The skill reviews correctness and whether each change earns its place, then proposes minimal fixes without editing files. GitHub PR discovery and patch retrieval require the `gh` CLI authenticated to the repository. See the [package README](plugins/devloop/README.md) for details.

### Adopt engineering patterns

After installing, invoke `/devloop:adopt all` in Claude Code, or ask Codex to “Use devloop's adopt skill to install its engineering patterns.” A single pattern id also works, and no argument lists the catalog.

The skill copies stance sections — design judgment, debugging discipline, test design, writing style, commit conventions, and the handoff contract — into the project's `AGENTS.md`, each marked with its version so a later run can update it without overwriting local edits. See the [package README](plugins/devloop/README.md) for the catalog and the update rules.

### Install from GitHub

After this configuration is merged into the default branch:

```sh
# Claude Code
claude plugin marketplace add lxcid/plugins
claude plugin install devloop@lxcid

# Codex
codex plugin marketplace add lxcid/plugins
codex plugin add devloop@lxcid
```

### Try a local checkout

Run from the repository root. These commands register this checkout as a marketplace and install the plugin into each application:

```sh
# Claude Code
claude plugin marketplace add ./
claude plugin install devloop@lxcid

# Codex
codex plugin marketplace add .
codex plugin add devloop@lxcid
```

Choose either the GitHub source or the local source for the `lxcid` marketplace. Claude Code re-points an existing registration when you add the other source, so no marketplace removal is needed there — avoid `claude plugin marketplace remove`, which reaches across scopes and drops project-scoped installs. Codex refuses to re-point one, so run `codex plugin marketplace remove lxcid` before adding the new source. Switching the source does not by itself refresh an installed plugin: `claude plugin install` reports it is already installed and keeps the previous copy, so run `claude plugin uninstall devloop@lxcid` before installing again; `codex plugin add` re-copies on its own. For a local checkout, `just devloop::reinstall` handles all of this; see [Development](#development). Start a new session after installation to load the plugin.

Claude Code can also load the package for a single development session with `claude --plugin-dir ./plugins/devloop`.

While editing the package, `just devloop::reinstall` repeats this sequence for both hosts so the edits reach an installed plugin; see [Development](#development).

### Update or uninstall

For an installation from GitHub, refresh the marketplace and install the updated package in each application:

```sh
# Claude Code
claude plugin marketplace update lxcid
claude plugin update devloop@lxcid

# Codex
codex plugin marketplace upgrade lxcid
codex plugin add devloop@lxcid
```

Start a new session after updating. To uninstall, run `claude plugin uninstall devloop@lxcid` or `codex plugin remove devloop@lxcid`.

See the [package README](plugins/devloop/README.md) for manifest versioning and where shared workflow content will live. Packaging references: [OpenAI plugins](https://developers.openai.com/plugins/build/plugins), [Claude Code plugins](https://code.claude.com/docs/en/plugins), and [Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).

## Development

The tooling below is an opinionated setup, kept minimal, and optional: repos that adopt devloop need none of it. Tool versions are pinned in `.prototools` and run through [moon](https://moonrepo.dev). With [proto](https://moonrepo.dev/proto) installed:

```sh
proto use                    # install pinned proto, moon, node, pnpm
moon run root:format         # format everything with oxfmt
moon run root:format-check   # what CI runs
```

Formatting uses [oxfmt](https://oxc.rs/docs/guide/usage/formatter) with default settings, plus `proseWrap: "never"` for Markdown so paragraphs stay on one line and your editor soft-wraps them.

Local recipes live in [`justfile`](justfile) and need [just](https://just.systems) 1.31 or newer (when modules stabilized) on your `PATH`; `just` is not pinned through proto, and nothing in CI runs it. Each plugin package gets a [module](https://just.systems/man/en/modules.html) named after it, in `<name>.just` at the repository root, so recipes read the way the skills do. Run `just` for the list:

```sh
just devloop::reinstall          # reinstall this checkout into both hosts
just devloop::reinstall-claude   # Claude Code only
just devloop::reinstall-codex    # Codex only
```

`just devloop reinstall` is the same recipe; a single colon is not available, because just reads `:` as the recipe separator.

Both hosts install a copy of the package, so edits under `plugins/devloop/` reach an installed plugin only once the marketplace and the package are read again. Each recipe points the `lxcid` marketplace at this checkout and reinstalls `devloop` from it; `reinstall` runs both and skips a host whose CLI is not on your `PATH`. Claude Code re-points an existing registration in place, so its recipe leaves the marketplace alone rather than removing it across scopes and dropping a project-scoped install; Codex refuses to re-point one, so its recipe removes the registration first. The Claude Code recipe validates both manifests first with `claude plugin validate --strict`; Codex ships no equivalent, and `claude plugin validate` covers only the Claude catalog, so a malformed `.agents/plugins/marketplace.json` surfaces there as a failed `marketplace add` after the teardown has already run, leaving the `lxcid` marketplace unregistered — the plugin's config entry and cached copy remain — until you fix the catalog and re-run. Start a new session in each host afterwards.
