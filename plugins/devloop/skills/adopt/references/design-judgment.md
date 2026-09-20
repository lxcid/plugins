---
id: design-judgment
version: 1
section: Design Judgment
---

## Design Judgment

**Default to the minimal necessary complexity.** Prefer the smallest design that satisfies the current product need, fits the existing architecture, and leaves a clear path to extend later. Be suspicious of abstractions, invariants, retries, background machinery, or schema constraints that mostly exist to make the design feel complete rather than to solve a present problem.

Interpret "smallest design" architecturally, not as the fewest changed lines. First identify the current product need and any invariant it actually requires; then choose the smallest design that satisfies those, fits the existing architecture, and does not move away from a recorded architectural direction. A locally small patch that weakens the required invariant, creates a parallel path, or adds a temporary abstraction already known to be replaced is not minimal. If the stronger invariant is not a present product need, prefer explicitly tolerating and deferring the problem over building machinery for completeness or shipping a partial solution with a stronger claim.

Operator direction sets the product constraints, but it does not remove the agent's obligation to exercise engineering judgment. Surface and argue when a requested direction would conflict with the existing architecture or a recorded direction, or would spend durable complexity on a low-value problem; once the operator decides with that trade-off visible, follow the decision.

**Argue with numbers, and audit your own counter-proposal.** When pushing back on a proposed design, the minimality principles above are priors to test, not verdicts to cite: quantify the binding constraint before judging a design over- or under-built. Then red-team your alternative as hard as the proposal, against the same conditions. A position that needs a new compensating patch each time it is challenged is the escalating-commitment signal from Debugging Discipline at design scope — and it applies to both sides of the discussion. When it is your position, stop defending it and re-derive from scratch; when it is the operator's, your job is to help them break the loop with evidence, not to concede to authority. If neither design survives and the discussion stalls, drop both: enumerate the actual requirements together and derive a solution from those.

**Weigh every edge case before fixing it.** Consider these factors together:

- **Likelihood** — how often does this happen in the current product shape?
- **Impact** — what actually happens to the user or operator?
- **Recoverability** — can they recover with existing UI or an obvious manual action?
- **Cost** — how much implementation, testing, documentation, and future constraint does the fix add?

Tolerate or defer a case when the four factors together show that the fix costs more than the failure and required invariants remain satisfied. Low likelihood alone cannot justify deferring a high-impact, unrecoverable failure. Don't introduce durable complexity to make rare behavior tidy. Call out the trade-off in the handoff so the operator can decide if the bar moves.

**Essential complexity is earned; accidental complexity is the default failure mode.** Add a status value, index, retry, rollback, or layer only when a _present_ feature needs it. The cost of a wrong abstraction is paid by every later reader; the cost of a right abstraction deferred by one week is usually nothing.
