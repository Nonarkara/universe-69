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

## The founders (engine 2026.10.27.3)

Both universes receive **the same people**: same names, same heritable
temperaments, generated from one shared founder seed. The world is the only
variable. The first iteration is **two pairs**, young and innocent; both
worlds must discover how new life begins (EDEN sooner — there is nothing
else to do). Every reseed after an extinction sends **eight pairs**.

## Minds and bodies: one Stone-Age brain, two worlds

The organising idea is a mismatch. LAGOON is the world the human brain was
built for: hunger, status, belonging and purpose all find an outlet in
work. EDEN is a resort that answers every need except those. Sources are in
`BOOKS.md` (the owner's books) and `RESEARCH.md`; parameter values are
calibration, checked with `tools/lab.py`.

| Finding | Mechanic | Where |
|---|---|---|
| Behavioural traits ~half heritable (Bloom; Pinker *Blank Slate* ch.19) | `ef` (self-control) and `ag` (aggression) per person: mid-parent + mutation. Men express `ag` +0.08 (a distribution shift, never a rule) | `minds.inherit` |
| The prefrontal cortex matures last (Bloom; Pinker ch.3) | Expressed self-control ramps to full by ~22 | `minds.self_control` |
| Purpose comes from being asked something (Frankl; *Homo Deus* ch.2) | `pu` drifts toward what the world asks: LAGOON asks 0.35 plus work, EDEN asks nothing; dependents, a partner, a place add to it | `minds.tend_purpose` |
| A forager's appetite in abundance | EDEN intake rises as purpose falls → BMI climbs toward obesity; idle muscle wastes. LAGOON BMI is paid for in work and lost to famine | `minds.tend_body` |
| Anomie: nothing regulated, nothing asked (Durkheim, *Suicide*) | A competent EDEN adult with purpose < 0.25 may withdraw for good; self-control is the brake | `tick_eden` |
| Universe 25's withdrawn were three kinds (RESEARCH.md [2][3]) | Placeless losers pool listless in the middle of the floor and are attacked there; the beautiful ones (born into the sink) groom alone in a corner; lone women retreat to the top row of cabanas. All feed at the hopper nobody else uses, and never join a circle, a couple or a fight | `withdraw`, `withdrawn_home` |
| Revenge, the moralization gap (Pinker *Better Angels* ch.8) | A killing gives the victim's kin a grudge (decays ~8%/yr); revenge when restraint fails | `lagoon_violence` |
| Young unpaired men kill (Pinker ch.2, ch.10) | LAGOON homicide hazard for men 16–30, ×2 unpaired, × temper × (1.2 − self-control) | `lagoon_violence` |
| Leviathan: a third party with standing (Pinker ch.2–3) | Band 0.1, tribe 0.35, chiefdom 0.65 arbiter (+0.15 with writing): damps violence, exiles or executes killers | `organise` |
| Band → tribe → chiefdom (Diamond ch.14) | At 50 and (with a granary) 300 people, with hysteresis | `organise` |
| Collective effervescence (Durkheim, *Elementary Forms*) | With lore, each settlement dances at midsummer for its totem; cohesion +0.5, decays 0.25/yr; a hungry year skips it | `hold_rites` |
| Covering as the first cultural act (Peterson on Genesis 3) | After innocence ends, modesty rises (LAGOON to 0.85; EDEN to 0.5 as the pen fills); the renderer covers that share of adults | `modesty` |
| Invention needs planners with company (Pinker ch.3; Diamond ch.13) | Tech discovery × (0.5 + 2 × share of adults with `ef` > 0.6); the discoverer is the most self-controlled of a few | `tick_lagoon` |
| Two clocks | Mean and tail of `ef` recorded yearly in `mind`, apart from tech and arts | `record_mind` |

Re-derived with this engine (`tools/lab.py`, seeds 69/7/123/5, 150 years):
LAGOON's violent share of deaths runs 0.6–7.8%, lowest where a chiefdom
formed (Pinker's forager range is 4–30%; famine dominates deaths here).
After 80 years from seed 69 the EDEN adults average BMI ≈ 32 with purpose
≈ 0.2, against LAGOON's ≈ 22 and ≈ 0.8.

## Engine 2026.10.27.2, second pass: routines, biology, boats, fire

Sources: `BOOKS.md` (second reading pass, sweeping every book by keyword
index — still not cover to cover), `RESEARCH.md`. Values are calibration.

| Finding | Mechanic |
|---|---|
| Calhoun: the scarce thing was socially meaningful roles (RESEARCH.md §1); Bestor ch.6: seats are a fixed count, refilled only on a holder's death | EDEN **posts** (bar staff, lifeguards, keepers) — a fixed list, filled once, vacated only by death or withdrawal. A post holder works shifts at their post |
| Every activity has a place | EDEN: sleep in one's **condo** (households) or **capsule hotel** (singles); the placeless sleep on **mats in the open hall**, jjimjilbang style; eat at the bars, talk on the boardwalks, lounge on the south beach. Aimless walking only for the placeless — the symptom |
| Calhoun's restless males; "pansexual" mounting (RESEARCH.md §1) | Placeless men in the sink roam the floor and press sex on whoever is near |
| More rooms held pathology off (Calhoun's later universes, RESEARCH.md [4][5]) | When crowding nears the sink, the **resort expands** 8 tiles on every side, with new lodgings and posts; at most twice (48 → 64 → 80). From seed 69 the sink begins in year 83 (about year 42 without expansion) and the death phase in year 103 |
| Primates bond by grooming; humans by gossip (Harari; Dunbar) | **Grooming** pairs in both worlds: kin and partners at LAGOON's hearths, anyone near in EDEN |
| Reproductive biology (Howell 1979 for forager spacing; Diamond ch.4 for settled spacing) | Fertility by age (0 before 16, falls after 30, 0 at 50), suppressed by low body fat and by nursing (3 years in LAGOON, 2 once farming, 1.5 in EDEN); 14% of conceptions miscarry; 1.4% of births are twins |
| Human birth needs help (the obstetric dilemma) | In LAGOON a mother or another woman kneels with the labouring woman. In EDEN she delivers alone, as Calhoun's mothers did |
| Drives and the prefrontal cortex (Bloom; Pinker *Better Angels* ch.9 on discounting) | LAGOON choices weigh hunger, fatigue, injury, care, company, sex and curiosity; delayed-reward actions (building, farming, the boat) are weighted by expressed self-control, immediate ones (eating the store) against it |
| Fire and the watch | With fire, one adult a day sits watch for each camp (the most vigilant take most turns); a watched camp halves predation, fire cuts it 30% |
| Vigilance is selected (Bloom on innate fears) | Heritable `vg` lowers predation risk; recorded in `mind` beside self-control |
| Stories make lore; lore explains with will (Harari, *Nexus* ch.2; Durkheim) | Talk at the fire accumulates stories; shared lore is discovered sooner the more there are. With lore, each new kind of disaster leaves a **myth** that explains it |
| Crowding puts people in boats (Diamond, Austronesian expansion) | When the island holds more than ~0.85 × 95, the camp builds a **boat** at its west beach (400 person-days, visible); a party of young adults, partners and children **sails across the strait** over days, lands, and leaves the boat on the far beach. The mainland is untouched land: fresh groves and naive game |
| Seasons | LAGOON has four (spring, summer, autumn, winter) with droughts, storms and ice-age winters; EDEN is always spring |

Re-derived with this engine (seeds 69, 7, 123, 5, 11, 42, 300, 8; 150
years): LAGOON died out at least once in 3 of 8 runs, against 6 of 8 on
the previous engine; peaks ran 39–406, highest where a boat landed. LAGOON time budget after year 60 (seed 69): foraging 24%, walking
20%, minding children 13%, play 13%, sleep 8%, talk 7%, sex 3.5%,
grooming 3%.

## Engine 2026.10.27.3, the merge: one record a day

This engine is the merge of two lines of work — the routines/biology/boats
pass above and the record-keeping pass from the other branch. Both are kept.
Three model changes, none of them a new mechanism:

| Change | Why | What it does to the numbers |
|---|---|---|
| Famine is **one line a day**, not one line per death | A lean season is one event. Ten deaths in a day are one sentence, not ten | The event log's famine lines change wording and count. Cause-of-death totals do not |
| A fall is a separate cause, `accident`, from old age | The two were collapsed into one bucket, so a world of young people dying of falls reported as "age" | `cod` gains an `accident` bucket. Any figure that summed `cod` across causes changes; re-derive it |
| Farm fields are dug only on **dry land** | Water is not a field | LAGOON's farm tiles move off the shoreline. Farm count is unchanged; farm *positions* are not |

The engine also records its own version in every postmortem, so a published
figure can be traced to the code that produced it.

**Rolls are preserved.** The old per-death famine coin flip is still drawn
and discarded, so every later random draw in the day lands in the same
place it did before. The trajectories differ only where the three changes
above change an outcome.

**Figures that changed.** Any number derived from the 2026.10.27.2 engine
is not reproducible from this one. The 150-year seeds (69, 7, 123, 5, 11,
42, 300, 8) quoted above were re-derived on 2026.10.27.2 and have **not**
been re-derived on 2026.10.27.3 — treat them as stale until
`tools/lab.py` re-runs them.

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
  population's bounding radius. The viewer may take it, follow a person, or
  **walk in** (arrows/WASD, `I`, or WALK): a person-height camera that
  introduces everyone nearby by name, activity and body.
- People are drawn as **life-drawing sketches** (owner's brief, 2026-10-27):
  ink line over a flat skin wash, realistic proportion (~7.5 heads), body
  from the model — width from BMI, muscle from strength, ribs in famine, a
  belly for obesity or pregnancy, a bandage and limp for injury. Adults are
  drawn as bodies are; children never get genital detail. Far away a figure
  is a body's mass, never a stick.
- EDEN is dressed as the Truman Show's resort: beach floor, buffet bars for
  hoppers, striped cabanas for nest boxes, a horizon painted on the dome
  wall, and the real sea just outside it.
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
