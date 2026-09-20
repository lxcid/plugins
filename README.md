# lxcid’s Public Plugins

Public plugins for Claude Code and Codex. The first plugin, `devloop`, packages development workflow skills, starting with deep PR and branch review. Opinionated setup, minimal and optional.

## Plugin configuration

One [plugin package](plugins/devloop/) is shared by Claude Code and Codex. The repository provides a public plugin marketplace named `lxcid` for each host. Codex displays it as “lxcid’s Public Plugins”:

- `.claude-plugin/marketplace.json` for Claude Code.
- `.agents/plugins/marketplace.json` for Codex.

Both catalogs currently list `devloop` at `./plugins/devloop`; additional public plugins can be added under `plugins/<name>/` and listed in both catalogs. Version `0.1.0` includes the `deep-review` skill. Each application manages its own installed copy; installing, updating, or removing it in one application does not change the other.

### Review a PR or branch

After installing, invoke `/devloop:deep-review 123` in Claude Code, or ask Codex to “Use devloop's deep-review skill to review PR 123.” A PR URL, an explicit file or commit range, or the current branch also works.

The skill reviews correctness and whether each change earns its place, then proposes minimal fixes without editing files. GitHub PR discovery and patch retrieval require the `gh` CLI authenticated to the repository. See the [package README](plugins/devloop/README.md) for details.

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

Choose either the GitHub source or the local source for the `lxcid` marketplace. To switch, remove its existing registration with `claude plugin marketplace remove lxcid` or `codex plugin marketplace remove lxcid`, then add the new source. Start a new session after installation to load the plugin.

Claude Code can also load the package for a single development session with `claude --plugin-dir ./plugins/devloop`.

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
