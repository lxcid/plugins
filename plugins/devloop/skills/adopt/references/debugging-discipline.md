---
id: debugging-discipline
version: 1
section: Debugging Discipline
---

## Debugging Discipline

**A failed fix is evidence your mental model is incomplete, not yet evidence the design is wrong.** Retry smaller and more carefully. The failure mode to watch for is **escalating commitment under uncertainty**: repeated failed guesses can make a rewrite feel justified, when the fix usually exists at a smaller scope you have not located yet.

- **At a dependency boundary, read the dependency's source before changing your approach.** The source is on disk. Grep for the handler you suspect instead of theorizing from symptoms.
- **Enumerate every input that could produce the symptom before concluding any one is _the_ cause.** Stopping one doesn't stop the others. For event-driven code this means listing the full family that can fire, not the first one that looks plausible.
- **Symptom-based theories are hypotheses, not conclusions.** Before editing, name what you think is happening and what would falsify it. If the fix fails, treat the hypothesis as incomplete or unproven — narrow with a log, source-reading, or a smaller repro before editing again.
- **A failed attempt is not a licence to delete required behavior.** Replacing a broken inline editor with a cruder prompt removes the interaction instead of fixing it. Redesign when evidence says the design is wrong, not merely because the third patch failed.

### Worked example

_Not yet recorded._ The next time a fix in this repository takes three attempts, replace this with: the failed hypotheses in order, what each one assumed, where the actual fix turned out to live, and how its size compared to the attempts it replaced. A borrowed example from another codebase carries none of the weight — the point is that a reader recognizes the code.
