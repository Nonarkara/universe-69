# UNIVERSE 69 — Design

Two sealed worlds, observed side by side, running continuously on this laptop.
The Observers (you + Claude) never intervene; they only provision (EDEN) and record.

Naming: Universe **6** = EDEN, Universe **9** = LAGOON. 6 + 9 → Universe 69.

## Time

- 1 tick = 1 simulated day. 1 tick every **2.0 real seconds**.
- → 1 real day ≈ 43,200 sim-days ≈ **118 sim-years ≈ 5–6 generations**.
- Day 0 is anchored to a wall-clock epoch. On restart/wake the engine computes
  `target_day = (now − epoch) / 2s` and fast-forwards. The universes age even
  while the process is dead — Tamagotchi semantics, no drift.

## Universe 6 — EDEN (after Calhoun's Universe 25)

A 48×48 sealed pen. Food hoppers and water are always full. Climate is perfect.
No predators, no disease, no work. Two founding pairs (lab IDs, e.g. `E-0001`).

The only scarce resource is **social space** (Calhoun's actual variable):

| Research finding (Universe 25)            | Mechanic                                                    |
|-------------------------------------------|-------------------------------------------------------------|
| Phase A "strive" → B "exploit"             | Normal pairing + conception while crowding < 35% of nominal capacity (900) |
| Phase C "stagnation", behavioral sink      | Above 35%: conception scales down, violent deaths appear     |
| Maternal neglect                           | Infant abandonment probability ∝ crowding                    |
| "Beautiful ones"                           | Children born during stagnation can be *socially incompetent*; on adulthood they withdraw and never pair |
| Phase D "death", no recovery               | Once yearly deaths > births for 3 years, the competent cohort ages out; incompetence is fixed at birth, so collapse is irreversible even as space frees |
| Extinction (day ~1588 for the mice)        | Pen empties; event logged                                    |
| LD&R "Ice Age" cyclicality                 | 30 sim-years after extinction the Observers reseed the pen; `iteration += 1` |

## Universe 9 — LAGOON (Blue Lagoon / first Sapiens world)

A 96×96 world: woods, grassland, a lagoon with fish, beaches. Wildlife stocks
(plants, game, fish, predators) regrow logistically and deplete when harvested.
Two founding pairs with organic names. Nothing is given; everything is earned.

| Research finding                           | Mechanic                                                    |
|--------------------------------------------|-------------------------------------------------------------|
| Foraging economics                          | Adults gather daily; yield depends on tech, season, stock levels; shortfall → hunger → starvation (weakest first) |
| Predation, accidents, childbirth mortality  | Daily hazard rates; children more vulnerable; weapons/healing lore reduce them |
| Seasons + disasters                         | 360-day year with winters; storms, droughts, harsh "ice age" winters, all logged |
| Blue Lagoon innocence                       | The founders don't know how life begins; a discovery event in the first years unlocks reproduction |
| Sapiens: cognitive revolution / Dunbar 150  | Without **shared lore**, a settlement over its social limit splits or feuds; lore raises the cooperation ceiling |
| Sapiens: agriculture = "luxury trap"        | Farming raises carrying capacity and birth rate but adds workload and disease exposure |
| GG&S: domestication → germs                 | Animal domestication unlocks epidemics (can kill 15–35%)    |
| GG&S: surplus → specialists → tech          | Tech ladder: fire → stone tools → fishing → shelter → preservation → shared lore → agriculture → domestication → granary → healing lore → metallurgy → writing. Discovery odds scale with population and need |
| Expansion                                   | Overfull settlements fission; new bands found new settlements — the map fills as the camera zooms out |

## Sex, boredom, and disease (EDEN)

Mating in EDEN is free and pedestrian — no pair-bonds, no cost — until it
isn't: (1) **ennui** — hedonic adaptation slowly dulls fertility in a world
where pleasure costs nothing; (2) **STD outbreaks** — free mating at density
carries one price; outbreaks cut fertility, kill some adults, and leave the
next generation *wary* (a ~20-year cultural-memory fertility dampener that
fades when that generation ages out — "the pen forgets"). All logged.
LAGOON keeps pair-bonds (widows re-pair); there, only famine suppresses
fertility.

## Death, postmortems, and lessons (the Edge-of-Tomorrow loop)

Every death is tallied by cause. When a universe dies, a **postmortem** is
recorded (data/postmortems/): peak, generations, technologies, cause-of-death
table, dominant cause, and whether it was preventable.

- **LAGOON learns.** Reseeded founders inherit lessons mapped from past
  dominant causes — starvation → *preserve* (starting food cache, faster
  preservation/fishing), predators → *vigilance* (−40% predation, faster
  tools), epidemic → *cleanliness* (half outbreak odds), feud → *unity*
  (faster shared lore). Survivors of a near-wipe (one cause killing >20% in a
  year) imprint the same lesson without going extinct — instinct passed on
  with no written language, the way fear of snakes is.
- **EDEN cannot learn.** Each reseed restarts under identical, perfect, fatal
  conditions, and each postmortem records the same verdict: nothing within
  the walls could have prevented it. That asymmetry is the experiment.

## Bands and tribes

Everyone starts together — bonding is survival. Past the cooperation ceiling
(~80 without shared lore, more with it), settlements fission into *named
tribes*: peacefully after lore exists, as a deadly feud before it.

## Rendering (web/index.html)

- Two canvas panels side by side, `image-rendering: pixelated`, flat 16-color
  palettes, monospace HUD. No gradients, no shadows, no decoration.
- Camera per universe starts tight on the founding pairs and widens with the
  population's bounding radius.
- People are single chunky pixels: child / man / woman / elder / withdrawn.
- Bottom ticker: the shared event log (discoveries, disasters, phases, deaths
  of note, extinctions, reseedings).

## Processes

- `sim/server.py` — engine + HTTP on **localhost:6969** (serves UI, `/state`,
  `/world`, `/events`). Saves `data/state.json` every minute and on shutdown.
- LaunchAgent `com.universe69.sim` keeps it alive 24/7 (KeepAlive + RunAtLoad).
  When the lid is closed the Mac sleeps; on wake the engine fast-forwards.
- Uploader thread pushes a snapshot to the web mirror every ~2 minutes.
- Web mirror: static viewer on Vercel at **universe.nonarkara.org** reading the
  pushed snapshot.
- Chronicle: `tools/chronicle.py` writes a mechanical daily digest to
  `data/chronicle/`; a scheduled Claude job writes the narrative chronicle.

## Honest limitations

- Humans modeled with human demography (20-year generations, single births),
  so EDEN's arc takes sim-centuries — days of real time, not hours.
- Both universes are stochastic; a founding pair can die out early. That is a
  valid result (it happened to real founder populations); reseeding is logged,
  never hidden.
- This is a model of *dynamics from the literature*, not a claim about people.
- Determinism holds per `(seed, day)` **within one engine version**. Editing
  `sim/engine.py` changes every number derived from the previous version, and
  the live run's history becomes irreproducible from that point on. Re-derive
  figures from the shipped code; never quote one from an old log.
- The renderer reads a flat, positional payload from `engine.summarize()` with
  no type protection. `tests/test_contract.py` pins that contract from both
  sides so a rename fails the suite instead of the browser.

## Verifying the model

`tools/lab.py` runs an arc locally in seconds and prints a verdict:

- did EDEN's pen actually empty (and therefore write a postmortem and reseed),
- did LAGOON survive, and which technologies and lessons it reached.

The verdict, not the eye, is the acceptance test for a change to the engine.
Run it before and after any model change, and treat a change in the verdict as
a change in the experiment.
