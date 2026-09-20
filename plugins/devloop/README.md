# devloop

Devloop uses intents as units of change within its own development workflow. The intent concept informs the process; the plugin has its own scope and conventions.

Shared plugin package for Claude Code and Codex. Version `0.0.0` contains packaging metadata only; workflow skills, commands, hooks, and agents are not implemented yet.

## Package layout

- `plugin.json`: portable Agent Plugins manifest and canonical package identity.
- `.claude-plugin/plugin.json`: Claude Code manifest.
- `.codex-plugin/plugin.json`: Codex compatibility manifest and display metadata. The portable manifest intentionally omits `extensions.com.openai` so this file supplies the OpenAI-specific settings.

Keep the name, version, description, author, homepage, and repository identical across all three manifests. Bump all three versions together when releasing changes. The repository's root `package.json` describes development tooling, not the installable plugin.

Add shared workflow content under this directory as it is implemented: `skills/<name>/SKILL.md`, `templates/`, and `scripts/`. Keep packaged resources within this directory so they remain available after either host installs its own copy. Add host-specific hook and agent configuration only when implemented and verified in that host.

Both repository marketplace catalogs point here. Each host manages its own installation, settings, and updates. Downstream project artifacts belong in that project's `docs/intents/`, outside the installed plugin, so either host can continue the same intent.
