---
id: handoff-contract
version: 1
section: Handoff
---

## Handoff

Every task ends with a handoff. Reporting what changed is the easy half; the obligations below are the half that gets dropped, and each one exists because the operator cannot recover it from the diff.

- **What changed, and what you verified.** Name the commands you ran and their results. State plainly what you could not verify and why — an unavailable surface, a check that needs a browser, an environment you don't have. A passing type-check is not evidence that a feature works.
- **Trade-offs you took deliberately.** An edge case you tolerated, a problem you deferred, a stronger invariant you decided the present need didn't require. Say so, so the operator can move the bar if they disagree.
- **Tests you skipped.** The reason, the verification you ran instead, and the test to add if the surface grows.
- **Drift you noticed.** Documentation that no longer matches the tree, a convention the code has quietly stopped following, a stale assumption in the task itself. Surface it even when it was not your task to fix.
- **Side effects you caused.** A logic fix that changes an error state, a validation message that now reads badly, a behavior change a reader of the diff would not predict.
- **Changes you did not make.** Files in the worktree you didn't touch, and anything you left alone because it looked user-owned.

State these even when they are unflattering, and especially when nobody asked. A handoff that only reports success transfers no information.
