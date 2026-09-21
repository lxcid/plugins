# Browser pass

How to exercise a surface so the craft lens has something real to judge. Referenced from [SKILL.md](../SKILL.md) step 4. Everything here is portable except the last section.

## Let the audience choose what you exercise

Coverage is not the goal; the audience's actual path is. Name them first ([SKILL.md](../SKILL.md) step 3), then spend the pass where they live.

- A tool audience earns a full keyboard pass and a hard look at density, speed, and error honesty. Its phone layout may be genuinely out of scope — check whether the project says so before filing against it.
- A consumer audience earns phone-first capture, the first-run path, and the cold-start state where nothing is configured yet.
- A buyer-facing or marketing surface earns mobile, load behaviour, and the path from first frame to the one action it wants.

Say in the review which paths you chose and why. A pass that exercised the wrong flow thoroughly is still the wrong pass.

## Getting a surface up

In rough order of preference:

1. **The project's own dev server.** Find it in the launch or task config, `package.json` scripts, or the README — do not invent a command. Prefer the project's documented one-command stack when the surface needs siblings (an API, an auth service, a proxy) to render anything real.
2. **A production build served locally**, when the finding might be build-only — asset optimisation, minification, prerendering, anything the dev server papers over.
3. **The deployed environment**, when the change is already live. Reviewing deployed instead of branch means reviewing the *previous* version — worth saying out loud.

Two things to check before you start, because both silently invalidate a pass:

- **Is a server already running on that port?** If it is the operator's, drive it, don't restart it. Killing someone's dev stack mid-session is a worse outcome than any finding.
- **Does the surface need a session?** A sandboxed or in-app browser often cannot complete a cross-origin login, and you get a shell that never loads data — which reads as a bug and is not one. Use the browser that holds the real session for anything behind a login.

Note in the handoff if you started a stack, especially one with a public ingress.

## Capture matrix

Widths and themes, both derived from the project rather than assumed.

- **The design width** the work was built against.
- **One pixel below the project's main layout switch** — read the actual breakpoint out of the CSS or framework config. This is the highest-yield width for layout breaks, and guessing the framework default is how a pass misses them.
- **Tablet and phone**, weighted by audience as above.

For themes, check how the project flips before capturing: an OS-preference site needs the browser's `prefers-color-scheme` emulation, while an app carrying its own theme stamp needs its in-app switch — emulating the OS there changes nothing and you will screenshot the same theme twice. Where a project's design record requires both schemes before a surface is done, a one-theme review is an incomplete review.

## Exercising it

Reading the page is not exercising it.

1. **Walk the primary path end to end**, the way the PR body says a user would. Count your clicks.
2. **Click every control the diff introduced or changed**, then confirm the state actually changed. A toggle that restyles itself but moves nothing is a finding, and only a click finds it.
3. **Keyboard-only pass**: tab through, confirm focus is visible at every stop and lands somewhere sensible, activate with Enter/Space, Escape out of anything modal.
4. **Reach the unhappy states** — empty, loading, error, too-long content — from real fixtures. A surface only ever seen full has an unreviewed empty state.
5. **Read the console.** New errors or warnings are findings even when nothing looks wrong. Check whether they reproduce and whether they are environment noise before reporting them as defects.
6. **Judge the felt experience, not the measured one.** A correct pipeline with no progress signal is broken from where the user sits, and a fast response that arrives without acknowledgement feels slow. Note where you were unsure what would happen or what had happened — every such moment is tension the user did not ask for.
7. **Screenshot what you will cite.** A craft finding without its capture is an opinion.

Keep captures out of the repository unless it keeps reference images deliberately. Surface the ones carrying a finding so the operator sees what you saw.

## Keeping the evidence honest

Each of these is a way a review can look thorough while proving nothing.

- **Never fabricate a state.** Do not clear real data to photograph an empty state, and do not hand-edit the DOM to show what a fix would look like. Use fixtures, or report the state as unreached.
- **Park the pointer off the UI before capturing.** A stray hover state gets read as the default.
- **Capture after the surface settles.** Mid-transition invents a layout bug that is not there; before data lands hides the shift that is.
- **A passing typecheck, a clean build, and a green test run say nothing about how it feels.** They are not evidence for this lens.
- **Report what you could not reach** — a flow needing data you do not have, a state behind a flag, a provider you cannot call. An unreached state is a gap in the review, not an absent finding.
- **You are a proxy playtester, not the audience.** Exercising the surface tells you what it does; it does not tell you what a real member of the audience feels, and people reveal that by what they do — where they hesitate, what they repeat voluntarily, when they stop — not by what they say. A clean pass is evidence the change works, not evidence anyone wants it. Say which of the two you have.
- **If the surface will not come up, that is the finding.** Report the failure and what you tried. Do not fall back to reading the diff and describing how it probably looks.

## In this repository

The only Mempipe-specific part. Swap it to move this file to another project.

| Surface | How | Notes |
| --- | --- | --- |
| `apps/www` (marketing, public) | `preview_start {name: "www"}` → port 4730 | Self-contained; the built-in browser pane is fine. |
| `apps/www` production build | `moon run www:build`, then `preview_start {name: "www-preview"}` → port 4761 | For build-only findings. |
| `apps/app` (product, authenticated) | `just dev`, then `https://app.mempipe.dev` | The app alone is not enough — it needs `auth` (4700) and `api` (4720), and the Cloudflare Tunnel is the sole dev ingress. |

`just dev` needs network and Cloudflare DNS, and while it runs `*.mempipe.dev` is publicly reachable. Say so if you started it.

**Signed-in `apps/app` flows do not work in the built-in browser pane** — its cross-origin auth and api fetches are blocked. Use Claude in Chrome for anything behind a login. The pane is fine for `apps/www`, for `/sign-in` itself, and for unauthenticated routes.

Widths: **1440** (design target), **1023** (one below `lg`, where the shell enters compact mode and both side panels become overlays — [DESIGN.md](../../../DESIGN.md) P7), **768**, **375**. For `apps/www`, 375 is a primary surface. For `apps/app` workbench **pane content**, phone layout is deliberately not designed (P7), so do not file findings against it; pickers, onboarding, and `/sign-in` are centered forms and are expected to flow.

Themes: `apps/www` reads `prefers-color-scheme`, so use `resize_window {colorScheme: "dark"}`. `apps/app` reads its own `data-theme` stamp — switch it from the in-app palette command. [DESIGN.md](../../../DESIGN.md)'s checklist makes both schemes mandatory before a surface is done.

Captures go in the session scratchpad — `docs/assets/` is for DESIGN.md's reference captures, not review evidence. Send the ones carrying a finding with `SendUserFile`.
