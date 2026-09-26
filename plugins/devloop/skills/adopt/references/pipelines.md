---
id: pipelines
version: 1
section: Pipelines
---

## Pipelines

Work in this repository is organised into pipelines under `docs/pipelines/`. Each one holds a unit of work end to end: `intent.md` states the problem, `spec.md` records the decisions, `plan.md` tracks the build.

Before implementing anything, read `docs/pipelines/README.md` and the `intent.md` of the pipeline you are working in.

- Do not start work on a pipeline unless its intent is `approved` or `in-progress`. The operator approves intents; approval is the gate, and closed pipelines stay closed.
- Do not edit an `intent.md` to match what was built. It states the problem, and it keeps stating the problem after the solution changes. If the build shows the intent is wrong, stop and bring the evidence to the operator.
- Your goal is the outcome in the intent, not the steps in the plan. Verify against the intent before handing off; the operator confirms `done`.
- Record decisions in the pipeline's `spec.md`. There is no separate decision tree.
- Answer every open question in the intent with a decision that names it before handing off. Never add your own questions to the intent: decide questions about how to do the work, and ask the operator about what the work is.
- Do not reverse or materially change a decision the operator wrote or approved. Bring the evidence to the operator instead. You may depart from a spec's preference by recording a decision that says why.
- Before implementing, list the binding decisions from earlier pipelines with the command in the README's spec section. They constrain your work even though another pipeline made them.
- Mark a decision `Binding:` only when you can name the later pipeline that could violate it without noticing.
- The plan is yours. Revise it whenever the build shows it is wrong, keep `plan.md` current as you build, and mark what was verified by which command separately from what is merely asserted.
