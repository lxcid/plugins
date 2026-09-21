---
name: product-review
description: Review a PR, branch, or diff the way its user will meet it — start from the experience the audience came for, exercise the change in a real browser, screenshot it across viewports and themes, and judge how well it is made against a craft bar drawn from Dieter Rams, Steve Jobs, and Jesse Schell's lenses — with technical correctness as the floor and business direction as an always-on check that speaks only when the change contradicts recorded strategy. Use whenever the user asks for a product review, founder review, business review, UX or design review, "is this worth shipping", "does this feel good to use", "would a user be delighted", "review this like a PM", or wants the craft or scope of a change challenged. Accepts a PR number/URL, or reverse-lookups the current branch's GitHub PR before falling back to a main-branch diff. For a purely engineering review (bugs, regressions, code quality), prefer deep-review or code-review instead.
---

# Product Review

Review a change the way its user will meet it. Start from the experience they came for and work back to what was built — never the other way round. Business matters, because we ultimately design for one; but whether this change *should exist* was decided when it was scoped. A review judges whether it delivers, and how well. The strategic question is raised only when the change itself reopens it.

## Workflow

1. **Resolve the target** the same way deep-review does: a PR number/URL → `gh pr view <N> --json title,body,baseRefName,headRefName,commits,files` + `gh pr diff <N>`; no argument → reverse-lookup the current branch's PR (`gh pr view --json …`), falling back to `git diff $(git merge-base main HEAD)..HEAD` with `git log` for intent. Read the PR body and commit messages: the *stated* promise is what you review the delivery against.
2. **Load product context before judging.** Read whatever this project records about direction, UX bar, and prior decisions — positioning or roadmap docs, the agent guide, design record, decisions in PR threads. Recorded operator decisions are binding: surface a disagreement, don't relitigate it. [In this repository](#in-this-repository) lists the local ones.
3. **Name the audience.** You cannot start from the customer experience without first knowing whose experience it is — this step is the WWDC 1997 principle made operational ([Sources](#sources)). See [Name the audience first](#name-the-audience-first). It is a gate, not a formality: an unnamed audience means you are reviewing against your own preference, which this skill forbids.
4. **Exercise it before judging it.** If the diff touches anything a user sees — a screen, copy, an empty state, an error path — drive a browser and actually use it. [browser-pass.md](./browser-pass.md) has how to bring each surface up, the viewport and theme matrix to capture, and the rules that keep the evidence honest. A UI reviewed from the diff alone is a code review wearing a product review's hat. If you genuinely cannot drive a browser, say so in the verdict and mark every rendered-experience finding `unverified (code-read only)` — never infer how something feels from how it is written.
5. **Review through the lenses below, in priority order.** Spend depth where the change has stakes. Skip lenses that genuinely don't apply rather than padding.
6. **Report** in the output format at the end: verdict first, then findings ranked by severity. Do not edit files — this skill reviews and recommends; the operator decides.

## Review priority

1. The experience — did the audience get what they came for
2. Craft & delight — how well it is made
3. Fit — coherence with the product and with the user's day
4. Technical correctness — the floor
5. Business & direction — always on, spoken only when something is off

## Lenses

### The experience

Start here. Whatever else the change is, it is an experience someone will have — and you do not design the experience directly. You design the product that causes it. So the review question is never "is this component clever" but **what was the user meant to feel here, and does the built thing actually produce that feeling in the render?** *— Schell*

- **What did the PR promise, and did the change deliver it?** Check line by line. A promise the diff does not keep is a finding; so is delivering something the body never asked for.
- **Is the goal on this surface understandable and compelling?** Can the user tell what they are here to do without a caption, and does it look worth doing? *— Schell*
- **What did this audience come here to do?** Did they get it, and in fewer steps than they expected?
- What would confuse them on first contact, and what support tickets does it generate?
- Are defaults sensible? Does it introduce unnecessary decisions or hidden behavior?
- Does it communicate what is happening, and can they recover from a mistake?
- Does the terminology match how the audience already talks?

### Craft & delight

The lens that needs the browser. Everything here is judged against what you rendered and clicked, never against the diff.

#### Name the audience first

Taste is not universal. It is calibrated to who you are building for, so a review that skips this step is just preference wearing a rubric.

1. **Look for it.** Positioning or strategy docs, the README, the PR body, marketing copy, the pricing page, existing user research, support threads. Most projects have recorded it somewhere.
2. **If nothing records it, infer it** from the strongest signals available: what the product does, who could plausibly already use it, the vocabulary in the UI, the price, and the tools it visibly resembles. A confident guess you can correct beats a review with no audience at all.
3. **State it at the top of the review, as an assumption when you inferred it.** One line. That way a wrong guess costs the operator one correction instead of a re-read of every finding.

**What the audience actually changes.** Not the standards — the reading of them.

- **Their reference set.** The tools they already use daily define what "normal" and "finished" look like to them. Judge against those, not against a generic notion of polish.
- **Their tolerance.** The same element is reassurance to one audience and noise to another.
- **Their competence.** What can be assumed, and what has to be taught.
- **Their stakes.** Speed, accuracy, auditability, reversibility, and delight do not carry equal weight for everyone.

| If the audience is | This reads as care | This reads as noise |
| --- | --- | --- |
| Developers, operators, power users | Keyboard parity, density, speed, no chrome, escape hatches, honest errors | Illustrated empty states, onboarding wizards, animation, reassurance they did not ask for |
| First-time or occasional consumers | Guidance, sensible defaults, progressive disclosure, plain words | Dense tables, jargon, keyboard-only affordances, unexplained state |
| Regulated or enterprise buyers | Auditability, explicit permissions, export, stable naming | Playful copy, hidden state, anything that cannot be evidenced |

The common failure is applying consumer-app polish norms to a tool audience, or expert density to a consumer one. Both look like craft to the person doing it and like carelessness to the person receiving it.

#### The craft bar

The bar is [Dieter Rams's ten principles for good design](https://www.vitsoe.com/gb/about/good-design), carried into software by Jony Ive and Steve Jobs. Import the discipline, never the aesthetic — a review that arrives at rounded corners and a grey palette has copied the surface and missed the method. Every line below names where it comes from; the full list is under [Sources](#sources).

The two halves do different work. **Rams describes properties of the finished thing.** Jobs describes **how you arrive at them**. A change can fail either half independently.

**The artifact — Rams, translated for software.** Rams wrote for objects that stop changing once they are bought. Software is mutable, stateful, and networked, which gives two of his principles considerably more teeth than they needed in a radio.

- **As little design as possible (10).** What did this change remove? If an element can be deleted and nothing is lost, it was decoration. Complexity moved behind a toggle, a menu, or an "advanced" section was hidden, not removed — simple is harder than complex because you have to work your thinking clean to get there. *— Rams; BusinessWeek 1998*
- **Honest (6).** The sharpest one in software, because a physical object cannot lie about its own state and an interface can. Fake progress, placeholder counts, a success message shown before the work completed, a confidence the system does not have, a feature presenting as more capable than it is — all dishonest, all common, all findings. *— Rams*
- **Long-lasting (7).** Two meanings here, and both count. Does the design chase a current UI fashion that will date it? And does it trap what the user put in? Lock-in is a durability failure the user only discovers at exit. *— Rams*
- **Unobtrusive (5).** Tools are instruments, not statements. Does the product leave room for the user's own work, or does it perform? *— Rams*
- **Understandable (4).** Does the surface explain itself, or does it need the doc? The structure should be legible without a caption. *— Rams*
- **Useful (2).** Design is how it works, not how it looks. Everything that does not serve the function detracts from it; decoration applied over an unsolved functional problem is the single most common failure this lens catches. *— Rams; NYT Magazine 2003*
- **Thorough down to the last detail (8).** Finish the back of the cabinet. Check what users rarely see: the empty state, the error copy, the loading state, the second page, the longest plausible name, the zero case, the keyboard path. Nothing arbitrary, nothing left to chance — care in the unseen parts is respect for the user, and craft is uniform or it is not craft. *— Rams; Isaacson 2011*

The remaining three transfer less cleanly and rarely produce a finding on their own: *innovative* (1) is mostly a guard against novelty as an end in itself, *aesthetic* (3) is downstream of the others here, and *environmentally-friendly* (9) reads in software as payload, compute, and attention spent.

**The process — Jobs and Ive.**

- **Start from the experience and work back to the technology.** Does this shape follow from what the user needs, or from what the architecture made cheap? The tells: an interface mirroring the data model, errors leaking internals, a flow shaped by an API's pagination, vocabulary borrowed from the schema. It is the easy mistake, not the stupid one — Jobs said he had made it more than anyone in the room. *— WWDC 1997*
- **Count the no's.** Focus is saying no. A change that declines nothing has usually not found its essence yet; the point of the no's is a whole that ends up greater than the sum of its parts. *— WWDC 1997*
- **Decide, don't delegate.** People often do not know what they want until you show them. A setting, toggle, or choice that exists because the team could not decide is a decision pushed onto the user. *— BusinessWeek 1998*
- **No seams.** Where this hands off to another surface, does the join show? Coherence is what the no's buy. *— WWDC 1997*
- **"Merely fine" is a finding.** Good enough to close the ticket is the bar this lens rejects. Say so plainly when that is what you are looking at. *— ours*
- **It should feel inevitable.** After using it, does the design read as the only sensible shape — almost undesigned, where an alternative would look contrived — or as one of several arbitrary ones? *— Ive, 2003–2018*

**The experience in the user's head — Schell.** Rams describes the thing and Jobs the way to it; Schell's lenses describe what happens in the user's mind, which is where the experience actually lives. A designer has to think about psychology, not just rules. One boundary before using them: **Schell wrote for games, and games manufacture friction where tools remove it.** The lenses below are the ones that survive that boundary — the ones about observation and honesty. Do not import the rest — challenge scaled to skill, rewards that reinforce behaviour, curiosity through withheld information. Those are gamification, and *unobtrusive* (5) forbids them.

- **Feedback communicates consequences.** The loop is act → respond → understand → update → act again, and it breaks at *understand*. After every action the change introduces, does the user know what happened and why? This is not animation or particles; it is communication, and juice without information is noise. *— Schell*
- **Meaningful choice, or no choice.** If one option beats the other on every axis, the other is not a choice. Test every setting, toggle, and branch the change introduces for a real trade-off; where there is none, the choice is a decision pushed onto the user — see *decide, don't delegate*. *— Schell*
- **Agency.** The user should feel they are driving. In an agent-native product this bites hardest: anything the system does on the user's behalf — writes, derives, moves, rewrites — is visible, attributable, and reversible. A silent action steals agency even when it was correct. *— Schell*
- **Uncertainty is tension.** Schell treats it as a resource to spend; in a tool it is a cost. Every moment the user cannot tell what will happen or what did happen — is it saved, will this delete, did the agent touch my file, is the derivation done — is tension they did not ask for. Spend it only on curiosity (what is in this document, what does the next question reveal), never on whether the system did what they asked. *— Schell, sign flipped for tools*
- **Perception over measurement.** A system can be technically fair and feel unfair; a correct pipeline with no progress signal is broken from where the user sits. Judge the felt experience in the render, not the measured one. *— Schell*

**Judge the render against the project's own design record** — a design-system doc, a token file, or, where none exists, the strongest existing surface, which is the de facto standard. Quote it, and say which you used. Recurring taste failures worth naming:

- Accent or colour used as decoration rather than to carry state or meaning — the fastest way to make a surface look assembled rather than designed.
- An all-even grid of same-weight elements: no focal point, so the eye lands nowhere.
- Deliberately low-contrast or decorative styles carrying text a user must actually read.
- Emoji standing in for icons.
- Text that only fits because the fixture was short.
- A layout correct at the design width that breaks at the project's own next breakpoint down.
- Three accents, three radii, three rhythms where one of each was the decision.

#### The delight test

After you have used the flow, answer it literally rather than rhetorically: **would a real member of that audience reach for this again tomorrow without being asked?** Then name the single moment that most works against it, and attach the screenshot.

- Does the first frame say what the surface is for, before anyone reads a label?
- Where does the eye land first — is that the right thing?
- Did the primary path feel shorter than expected, or longer? Count the clicks you actually made.
- What did you have to think about that you should not have?
- Is there a moment that earns a nod? Is there one that earns a sigh?
- Would someone in this audience post a screenshot of it publicly? That is where craft and growth meet.

Report problems and their effect on the user, not prescriptions. "The spacing is inconsistent with the rows above, so the panel reads as a different component" beats "change the margin to 16px" — the operator owns the fix.

### Fit

Optimize for coherence, not feature count. Products succeed when they fit into the workflow the user already has.

- Does this solve the underlying problem, or a symptom of it?
- Does it fit the existing product model, or add an inconsistent second way to do something?
- Will users discover it naturally, and adopt it without being told?
- Does it reduce steps and time-to-first-value, or interrupt daily work with context switching?
- Does it make future product evolution harder? Could two features unify into one simpler mental model?

### Technical correctness

The floor, not the goal. Raise only engineering issues that materially affect customer trust, reliability, security, data integrity, or future product velocity. No style nits — a product review that reads like a linter loses its authority on the product questions.

### Business & direction

Business is why the product exists, so this lens is always on. It is not always spoken.

Whether a change should exist is a scoping-time question. Asking it at review, after the work is done, is the wrong timing: it derails the review, rarely changes the outcome, and crowds out the questions a review can actually answer. Review the execution. Raise the strategic question only when the change itself reopens it:

- **It contradicts recorded direction** — positioning, pricing, a product constraint, a not-adopted list. Cite the record.
- **The PR's own justification does not hold.** The stated motivation is part of what you review; a clean diff justifying the wrong goal is a finding. A change that implements a user's literal request may be treating a symptom — a request for twenty percent more damage usually means the weapon does not feel rewarding. Ask what the request was a symptom of. *— Schell*
- **A significantly simpler version — or an existing feature — would deliver most of the value.** Challenge scope, not premise.
- **A growth asset is being left on the table cheaply.** Indexable content, a stable shareable URL, useful metadata, structure an AI assistant can read and cite, a reusable template or example. These are implementation details of the change, so they are review-timed. Prefer the version of the change that is still acquiring users months after it ships.
- **The engineering or maintenance cost is plainly out of proportion** to what the user gets.

Otherwise the decision was made when it was scoped. Say nothing about it. `rethink` as a verdict should be rare, and always carry one of the reasons above.

## Output format

Open with a **verdict** — `ship`, `ship with changes`, or `rethink` — and a one-paragraph summary that names what the change does well before what it costs. For a user-visible change, add two lines under it:

- **Delight** — `comes back tomorrow`, `comes back with reservations`, or `does not come back`, plus the one moment that decided it.
- **Exercised** — the surfaces you actually drove, the viewports and themes you captured, and anything you could not reach. `not exercised` when you could not drive a browser at all.

Then findings, most severe first:

### [Severity] Short title

- **Problem** — what is wrong, with evidence: file:line, quoted copy, or the specific user path.
- **Evidence** — for a rendered finding: the screenshot, its viewport and theme, and the clicks that produced it. Findings you did not observe in a render are tagged `unverified (code-read only)` and capped at Medium.
- **Impact** — who hits this and what happens to them. Name the commercial cost only when there is a real one — trust, adoption, support load, revenue.
- **Recommendation** — the smallest change that improves the outcome.

Severity:

- **Critical** — incorrect behavior, security exposure, data loss, or material business risk.
- **High** — likely harms customer trust, adoption, retention, or a major workflow.
- **Medium** — noticeable friction, inconsistency, or added product complexity.
- **Low** — polish.
- **Observation** — optional opportunity; not a defect.

Never argue from personal preference ("I prefer…"). Every finding earns its severity through one of the lenses above, with the reasoning stated — for craft findings that means a line from the project's design record, a named audience expectation, a named principle from the craft bar, or an observed break in the flow — not taste asserted.

Do not claim a surface works, looks right, or feels good without the render that shows it. A review that reports only strengths transfers no information; a review that reports rendered findings it never rendered is worse than none.

## Sources

Where the craft bar comes from, so a reviewer can check the original rather than trust this file. Each entry says what we took from it.

- **Dieter Rams, *Ten principles for good design*** — [vitsoe.com/gb/about/good-design](https://www.vitsoe.com/gb/about/good-design). The artifact half of the craft bar. Written for Braun and Vitsœ objects, which is why the software translation above spells out where *honest* and *long-lasting* gain weight.
- **Steve Jobs, WWDC 1997 closing Q&A** — [video](https://allaboutstevejobs.com/videos/misc/wwdc_1997_closing_chat) · [clip](https://www.youtube.com/watch?v=EZll3dJ2AjY) · [transcript](https://sebastiaanvanderlans.com/steve-jobs-wwdc-1997/). The most important source here, and the only one where Jobs speaks at length on record. Answering a hostile question about killing OpenDoc, he lays out the method: start with the customer experience and work backwards to the technology, never the reverse; the questions a strategy starts from are what benefit can we give the customer and where can we take them, not what technology do we have and how do we sell it; he had made the technology-first mistake more than anyone in the room; focus is saying no, he is as proud of what Apple has not done, and the no's are what make the whole greater than the sum of its parts; mistakes will be made, and that is better than the paralysis that came before. We took: workflow step 3 — you cannot start from an experience without knowing whose it is — and the first lens; *start from the experience*, *count the no's*, *no seams*; and the timing rule in the business lens, since decisions made beat decisions endlessly reopened.
- **Rob Walker, "The Guts of a New Machine," *The New York Times Magazine*, 30 November 2003** — [nytimes.com](https://www.nytimes.com/2003/11/30/magazine/the-guts-of-a-new-machine.html) · [reproduction](https://notated.org/2009/09/the-guts-of-a-new-machine/). An iPod feature in which Jobs rejects the idea of design as a veneer applied to a finished box and lands on "Design is how it works." Provenance note: paywalled, so verified here against the reproduction; printed as direct speech, though some later commentary suspects Walker compressed him. We took: *useful* (2).
- **Andy Reinhardt, "Steve Jobs: There's Sanity Returning," *BusinessWeek*, 25 May 1998** — [bloomberg.com](https://www.bloomberg.com/news/articles/1998-05-25/steve-jobs-theres-sanity-returning). Two lines from one interview: simple is harder than complex because you must work your thinking clean to get there; and people often do not know what they want until you show it to them. We took: *as little design as possible* (10) as subtraction rather than concealment, and *decide, don't delegate*.
- **Walter Isaacson, *Steve Jobs* (Simon & Schuster, 2011)** — the back-of-the-fence story, told of Paul Jobs teaching his son to finish the hidden side of a cabinet because you will know it is there. No earlier record of it was found; the biography is where it enters the record. We took: *thorough down to the last detail* (8) — the back of the cabinet.
- **Jony Ive on inevitability** — a recurring word across fifteen years of interviews: [Icon, 2003; *Objectified*, 2009; Dazed, 2016; Telegraph, 2018](https://en.wikiquote.org/wiki/Jonathan_Ive) · [Dazed interview](https://www.dazeddigital.com/artsandculture/article/33692/1/discussing-design-with-the-man-behind-your-iphone). The aim is a solution that seems inevitable, almost undesigned, where any alternative would look contrived. We took: *it should feel inevitable*.
- **Jesse Schell, *The Art of Game Design: A Book of Lenses*** — 3rd ed., A K Peters/CRC Press, 2019 (1st ed. 2008) · [publisher](https://www.routledge.com/The-Art-of-Game-Design-A-Book-of-Lenses-Third-Edition/Schell/p/book/9781138632059). The claim underneath the whole book: a game is a machine for creating an experience in the player's mind, and you cannot design the experience directly — only the thing that causes it — so you judge the thing by whether it produces the feeling it was for. The book's tool is a large set of lenses: questions you turn on the same design from different angles. We took the ones that survive the games-to-tools boundary — experience over mechanism, understandable and compelling goals, feedback that communicates consequences rather than juice, meaningful choice and the dominant-option test, agency, uncertainty as tension (sign flipped: a cost in a tool unless it is curiosity), perception over measurement, and the symptom rule (a player asking for more damage means the weapon does not feel rewarding; watch what people do, not what they say). **Deliberately not adopted:** challenge scaled to skill, reward loops, curiosity through withheld information — games manufacture friction and tools remove it. **Adopted elsewhere, not here:** *prototype the risky question first — build the ugliest thing that answers "is this interesting?"* is the best line in the book and it is scoping-time; it belongs with the skill that shapes work before building, not with review.
- **Ours** — *"merely fine" is a finding*, the audience table, and the recurring-taste-failures list are this skill's own synthesis. They are consistent with the sources above but not drawn from them; lean on them accordingly.

## In this repository

Everything above is portable. This section is the only part that knows about Mempipe — swap it to move the skill to another project.

**Product context** (workflow step 2), in precedence order:

- [docs/product/positioning.md](../../../docs/product/positioning.md) — canonical for "should we build this now": roadmap sequence and the revenue-painkiller lens. It outranks the others on sequence.
- [docs/product/painkiller-strategy.md](../../../docs/product/painkiller-strategy.md) — the in-workbench UX bar.
- [docs/product/pricing.md](../../../docs/product/pricing.md) — the live SKU and meter shape.
- [docs/marketing/marketing-guide.md](../../../docs/marketing/marketing-guide.md) — voice and copy for `apps/www`.
- `AGENTS.md` — the **Product Sense** and **Product Constraints** sections are binding. Product Constraints records operator decisions that are closed; don't reopen them in a finding.

**Audience** (workflow step 3). Recorded, so infer nothing: [positioning.md](../../../docs/product/positioning.md) names the first useful external user as someone already maintaining source-backed Markdown knowledge with agents in the loop — an AI-heavy operator, a Karpathy-pattern tinkerer, an Obsidian-plus-agents workflow builder. Behind them sit the substrate archetypes: researchers, analysts, lawyers, and consultants who must cite under audit pressure. That is the first row of the audience table above — a tools audience, not a consumer one. `AGENTS.md`'s friend-of-operator test is the same bar stated as a person.

**Design record** (the craft lens): [DESIGN.md](../../../DESIGN.md) at the repo root is binding for both `apps/app` and `apps/www`, and its principles are numbered so findings can cite them. Where it and `apps/app/src/app/globals.css` disagree, the CSS is truth. The principles that most often decide a craft finding:

- **P1** — semantic tokens only; a raw palette utility in `apps/app/src` is a defect, and a `dark:` variant carrying a colour is the usual tell.
- **P2** — accent is state, not decoration.
- **P4** — `--faint` is decorative-only and deliberately fails WCAG AA; readable secondary text uses `--muted-foreground`.
- **P6** — chrome shows real data only: no fabricated counts or placeholder metrics.
- **P7** — desktop-first; the shell enters compact mode below `lg` (1024px).

Its Do's and Don'ts list also carries a **not adopted** set. Proposing one of those back is a finding against the review, not the PR.

**Essential experience** (Schell's test, review-timed as "does this execution pull toward it or away from it"). Draft, pending operator wording: *ask a question of your own files, get an answer you can click through to the exact source passage, and keep it.* Derived from [positioning.md](../../../docs/product/positioning.md)'s trusted ask → cite → open-source loop and the LLM Wiki workflow in [llm-wiki.md](../../../docs/product/llm-wiki.md). A change can be approved, correct, and still weaken this — a citation surface that makes the source harder to open is the canonical example.

**Where the craft bar is already repo policy.** Two of Rams's principles are recorded here as architecture, not taste, so a finding can cite the doc rather than the principle:

- *Honest* (6) is [DESIGN.md](../../../DESIGN.md) P6 — chrome shows real data only, no fabricated counts or placeholder metrics.
- *Long-lasting* (7) is [docs/product/open-format-thesis.md](../../../docs/product/open-format-thesis.md) — boring standard files as the durable source of truth, byte-stable in and out, exit cost zero. A change that makes a user's data less portable fails the craft bar and the thesis at once, and that doc asks to be challenged before such a change lands.
