---
id: writing-style
version: 2
section: Writing Style
---

## Writing Style

### Comments

- **Default to no comment.** Only when the _why_ is non-obvious — a hidden constraint, subtle invariant, workaround for a specific bug, behavior that would surprise a reader.
- Don't restate _what_ the code does; identifiers do that.
- Don't reference the current task, fix, or callers (`// used by X`, `// added for the Y flow`, `// handles the case from issue #N`). That belongs in the PR description and rots.
- **One comment, one decision.** Explain the non-obvious reason for the code beside it. Let that explanation wrap naturally. Split independent explanations and place each beside the code it explains. Move broader background to the relevant guide; retain the local context needed to change the code safely.
- **No banner or decorative blocks.** Avoid comments that serve only as visual headings or repeat the name of the code below them.
- Keep public API documentation where developers using the API will find it, including directly above the function or type definition when appropriate.

### Documentation prose

Write docs, issue bodies, and PR/issue comments for a human reviewer, not for density.

- Short sentences, one idea each. Plain wording is not weaker wording: keep the exact claims, names, and invariants, and drop only the compression.
- Don't stack qualifications into em-dash chains or nested parentheticals. Give each qualification its own sentence, or promote the set to a list.
- When prose enumerates cases, obligations, or layers, use a list. A reader should check items off, not parse them out of a paragraph.
- Status headers state a document's current standing only. Revision narration ("revised after review pass N…") is churn; git history already carries it.

### Shell output

- Single space between args; never pad to align value columns. Padded whitespace reads as a typo and costs reader doubt.
