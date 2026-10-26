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
