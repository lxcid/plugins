# AGENTS.md

Instructions for coding agents working in this repo.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
type(scope): summary

Body: why the change, not what. Wrap as prose.
```

- Types: `feat`, `fix`, `docs`, `chore`, `build`, `ci`, `refactor`, `test`, `style`, `perf`.
- Summary in imperative mood, lower case, no trailing period, under 72 characters.
- Scope is optional. For artifacts under `docs/intents/<slug>/`, use the slug as the scope, for example `docs(init): add spec`.
- Breaking changes take `!` after the type or scope and a `BREAKING CHANGE:` footer.
- One logical change per commit. Mechanical changes such as a reformat go in their own commit.
- Run `moon run root:format-check` before committing.
