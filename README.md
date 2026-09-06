# intentloop-plugin

AI-native SDLC loop as committed artifacts, for coding agents. Opinionated setup, minimal and optional.

## Development

The tooling below is an opinionated setup, kept minimal, and optional: repos that adopt intentloop need none of it. Tool versions are pinned in `.prototools` and run through [moon](https://moonrepo.dev). With [proto](https://moonrepo.dev/proto) installed:

```sh
proto use                    # install pinned proto, moon, node, pnpm
moon run root:format         # format everything with oxfmt
moon run root:format-check   # what CI runs
```

Formatting uses [oxfmt](https://oxc.rs/docs/guide/usage/formatter) with default settings, plus `proseWrap: "never"` for Markdown so paragraphs stay on one line and your editor soft-wraps them.
