# AGENTS.md — UNIVERSE 69

The open [agents.md](https://agents.md) standard. Every coding agent that touches
this repo reads this file first. It is tracked in git on purpose: it travels with
the clone to the 2016 MacBook that actually runs the simulation.

---

## What this project is

Two sealed pixel universes living continuously on one old laptop, observed but
never helped.

- **Universe 6 — EDEN**: John Calhoun's *Universe 25* rebuilt for humans. Free
  food, perfect climate, free mating, bounded space. The only scarce resource is
  *social space*.
- **Universe 9 — LAGOON**: the first-sapiens world. A lagoon, woods, game,
  predators, seasons — nothing given, everything earned.

The Observers never intervene. LAGOON inherits *lessons* from its dead
iterations. EDEN cannot: each reseed repeats the same fatal conditions, and
that asymmetry **is** the experiment.

Read these before changing anything:

- `RESEARCH.md` — the literature the model maps onto (Calhoun 1968–73, Harari,
  Diamond, *Love Death & Robots*). Cite it; do not invent mechanisms.
- `DESIGN.md` — the research finding → mechanic mapping table. A change to the
  model is a change to a row in that table, and the table must be updated with it.

---

## The house rules

### 1. The runtime lives on the 2016 MacBook, not here

This machine is the **workbench**. The 2016 MacBook is the **instrument**.

- Never run a long-lived simulation here and call it the live run.
- Work here, then commit and push. The 2016 MacBook pulls and restarts.
- Anything that changes the engine changes the trajectory of a run that is
  already 114+ years old. Say so explicitly when you do it.
- `data/state.json` is the live world state and is gitignored. It lives only on
  the 2016 MacBook. Never commit it.

### 2. The engine must stay pure, standard-library, and dependency-free

No packages. No build step. No framework. `sim/engine.py` imports only the
standard library. This is a feature — the simulation has to keep running on a
2016 machine for years.

### 3. State is a plain dict that round-trips through JSON

Every new field must:

- be JSON-serialisable,
- have a default in `engine.migrate()` — **the universes have been running since
  before some fields existed; they must not die of it**,
- survive `save_state` → `load_state` unchanged.

A schema change without a `migrate()` default is a bug that kills a live run.

### 4. Determinism is a promise, and engine edits break it

`tick_world` is deterministic per `(seed, day, part)` *within one engine version*.
Change the engine and every number derived from the previous version becomes
unreproducible. When you change behaviour:

- record the engine version in the state and in postmortems, so any published
  number can be traced to the code that produced it;
- re-derive figures from the shipped code, never quote them from a log or a
  previous bake;
- say in the docs that a figure changed and why.

### 5. Tests are mandatory for model changes

There is a `tests/` suite run with `python3 -m unittest discover -s tests`.
Any change to `sim/engine.py` must keep it green and should add a case that
pins the new behaviour. The renderer reads a specific field contract from
`engine.summarize()`; `tests/test_contract.py` pins that contract, so breaking
the viewer fails the tests rather than the browser. The **RESEARCH** button in
the viewer is the reading of the shelf: the long story of mankind the books
agree on, then every hypothesis they imply as a number the model can be caught
out on. `sim/research.py` holds that table and only ever *reads* — a new
hypothesis must not be able to move a world.

### 6. Iterate with `tools/lab.py`, not with the live machine

`tools/lab.py` runs a full multi-century arc without the wall-clock delay
and prints the arc table. Runtime depends on population; allow minutes.
Use it to test a change.
Never wait on the 2016 MacBook to discover what a model change did.

---

## Design law — MSH (Spatial Hallucination)

**This law is binding on all UI work in this repo.** The canonical full text is
[`docs/design-laws/MSH.md`](docs/design-laws/MSH.md) (187 lines). The binding
core is repeated inline below so an agent that skips the pointer still gets it.

> **SH is when an interface invents a reason for things to occupy space, instead
> of arranging them around how people read, choose, and act.**
>
> The test for every region: *why is this here? why this size? why this far from
> that?* "The grid put it there" and "it looks balanced" are failed answers.
>
> **The laws.** Space must have a job. Chrome earns its pixels — a brand name
> does not earn a giant top bar. Content determines size; the task determines the
> composition. Compose the first screen before extending the page. Hierarchy must
> survive the viewport. Relationships determine distance. Whitespace is allowed;
> unexplained space is not.
>
> **Do not solve SH** by adding another spacer, decorative panel, badge, slogan,
> stock image, or row of identical cards.
>
> **Evidence required before declaring a pass:** capture the real interface at
> 390, 1024, and 1440 px wide. Record chrome cost (height and % of viewport),
> task visibility, geometry failures, hierarchy, and preservation.
>
> **The standing order: when you find SH, massacre.**

### House style for this product

- **Full resolution, one palette (owner's decision, 2026-10-28, superseding
  the 8-bit lock).** The worlds are painted at the screen's own resolution —
  naturalistic but restrained, a lit terrarium, not a game; no
  `image-rendering: pixelated`, no tile blow-up. Colours come from one
  designed palette, TERRARIUM, as tokens on `:root` that the canvas reads;
  text clears WCAG AA. Type: Jost (console) and Source Serif 4 (reading).
  No Inter/Poppins, no decorative gradients, no emoji icons, no
  glassmorphism. **One screen, no scroll:** long content (record, research,
  help, the book) is read in pages with Prev / Next. See GRAPHICS.md §1.
- **The house style is executable, not advisory.** `tests/test_style.py` pins
  the palette and its contrast, the full-resolution ground, the one-screen
  page and its pagers, the age table (heads to height), the sex
  differences in width and stature, the anatomy rig, the body fields in the
  sprite key, the adult-only gate, the couple drawn as one picture, and the
  walk with a planted foot. A renderer change
  that breaks the style fails the suite, not the owner's eye. If you mean to
  change the style, change that file in the same commit, where it will be
  read.
- **People are the exception (owner's decision, 2026-10-27):** they are drawn
  as life-drawing ink sketches with realistic proportion, so a viewer can see
  whether someone is fat, starving, strong, weak or hurt. Never stick figures,
  never blobs. Adults are drawn as bodies are; children never get genital
  detail. Since 2026-10-28 every figure is **skeleton-driven**: the pose
  solver places hands and feet, an anatomy rig (`buildRig`, two-bone `ik2`
  per limb) with proportions by age and sex keeps the bones their length, and
  the skin — capsule limbs with muscle bellies, a torso from shoulders to
  waist to hips, hands, feet, a skull with a jaw and a hair silhouette — is
  painted around it. See DESIGN.md, "Rendering", and GRAPHICS.md §2.
- The viewer is a *documentary camera*, not a surveillance map: it finds
  something worth watching (a birth, a brawl, a hunting party) and closes in on
  it, then pulls back to the largest camp. Its zoom ladder is three rungs —
  island, camp, hearth — at about 6, 18 and 48 CSS px of adult height. Do not turn it into a dashboard of
  charts that a human was never going to read.
- The two universes are always shown **together on the first screen**: side
  by side on a wide screen, stacked one above the other under ~700 px. The
  comparison *is* the product; splitting them across pages or behind a tab
  destroys the experiment.
- A day is **four parts** — dawn, day, dusk, night — and the light turns with
  them. The tick is a part, not a day.

### Anti-regression

- The renderer is the artefact. Preserve the sprite cache, the pose solver, the
  camera behaviour, the particle systems and the ticker when refactoring.
- Never fit by clipping, hiding overflow, or shrinking readable text.
- The project ships to GitHub Pages from `docs/`. `docs/` and `web/` are kept
  byte-identical on purpose — the mirror reads a gist snapshot instead of the
  local server. If you change the viewer, change **both** and keep them equal.

---

## Where this is going

The user's brief, in their order:

1. **The 2D screen, perfected.** The viewer must make the inhabitants legible
   — what they are doing, who they are, where they belong, and what the
   record says. This round.
2. **Immersive 3D worlds**, with real zoom, and the ability to **go inside a
   universe as one of the people in it.**
3. **Meta Quest.** The next build target after (2) — WebXR, in a headset.

The framing to hold on to: a *fridge*. In *Love, Death & Robots* "Ice Age",
a couple finds a whole civilisation growing inside their freezer and can only
watch. Universe 69 is two sealed worlds observed through a window — never
helped, never entered by the Observers. The rendering should feel like
looking into a lit terrarium, not like playing a game.

Two rules that follow from the framing, and that the current viewer already
honours: **the camera is a documentary eye, not a game camera** (it finds
something worth watching and closes in, and the viewer may take it over); and
**sex is not a dirty thing that needs a guardrail here** — the dirtiness is
social, and in these universes it may or may not be so at all.

## Layout

```
sim/engine.py      the model — pure stdlib, deterministic per seed+part
sim/minds.py       the people: bodies, minds, fertility, names
sim/research.py    the hypotheses the books imply, and the run that tests them
sim/server.py      tick loop, HTTP viewer, snapshot uploader
web/index.html     full-resolution terrarium renderer (identical to docs/index.html)
docs/              GitHub Pages mirror + the canonical design law
tools/lab.py       bounded local harness without wall-clock delay
tools/sweep.py     vary the pen's design and report what each one does
tools/shoot.py     capture the viewer at 390/1024/1440 and drive it
tools/chronicle.py mechanical event digest
tests/             unittest suite (engine behaviour + viewer data contract)
DESIGN.md          the research finding → mechanic table
BOOKS.md           the owner's shelf, read
RESEARCH.md        the verified secondary literature
GRAPHICS.md        how the drawing works, what it does not, and what changed
STUDY.md           what the running universes did, and how to re-derive it
data/              state, events.ndjson, chronicles, postmortems (local)
```

## Commands

```sh
python3 -m unittest discover -s tests     # the suite
python3 tools/lab.py --days 60000          # a whole arc
python3 tools/lab.py --days 60000 --json out.json
python3 tools/sweep.py --study calhoun     # vary the pen
python3 tools/shoot.py http://127.0.0.1:6969/ --tag shot   # the viewer
./run.sh                                  # foreground server on :6969
python3 tools/chronicle.py                # digest new events
```

`UNIVERSE69_PORT` and `UNIVERSE69_DATA` move a development instance off the
live port and out of the live data directory. Use them: never point a
development server at `data/`.

## Honesty rules

- Report what succeeded, what failed, what was skipped, and what is unverified.
- Never present a figure that was not re-derived from the shipped code.
- The model is a model of *dynamics from the literature*, not a claim about
  people. Keep the framing honest in code comments, docs and UI copy.
