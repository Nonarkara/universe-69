# STUDY — measurements from the running universes

**Current version boundary.** Engine `2026.10.30.3` adds actual-contact
resource reports, preserving original age/provenance without granting supplies
or personal harvest experience. All older arcs are historical until re-derived.

**Earlier boundary.** Engine `2026.10.30.2` changes resource choices
through local perception, personal stock/location memory and exploration.
It also corrects fight-scoring age units and requires physical maternal
proximity/connected land for nursing; both worlds can change trajectory.
Results for `2026.10.30.1` below remain historical, not forecasts for this
new trajectory. The 100-year-per-real-day target clock is unchanged.

**Earlier boundary.** Engine `2026.10.30.1` changes food/water availability,
wildlife replenishment, conception and the default clock. All earlier results
below are historical; none is evidence for the new trajectory. The model is a
Sri Lanka coastal-ecology analogue, not an exact island map, physical-scale
survey, demographic prediction or guaranteed civilizational ladder.

## Contact-based knowledge — 2026.10.30.3

Final frozen-source seed 69 experiment: 36,000 model days (100 years), eight
founding pairs/world, Python 3.14.6, 691.7 seconds on the workbench. Raw arc,
compressed exact console bytes, source hashes and checks are retained under
`docs/audits/2026-10-30-social/`.

| World | Year 100 population / peak | Generation | Retained reports / people holding them | Recorded outcome |
|---|---:|---:|---:|---|
| EDEN | 456 / 525 | 6 | 20 / 17 | 239 withdrawn; no extinction/reseed |
| LAGOON | 34 / 38 | 5 | 0 / 0 |Six technologies, one camp, preserve lesson; no extinction/reseed |

Retained reports appear in 87 of 100 distinct annual EDEN observation years,
reaching 3 hops and
at most 99 stored reports in a sample. LAGOON retains reports in samples for
years 52, 90 and 91 (at most 2 reports, 1 hop), but none at year 100. These are
point-in-time memories, not cumulative conversations. Direct observation can
replace a report, so zero retained reports does not prove no communication.
Integration tests prove actual contact transfer in both worlds; controlled
LAGOON cases prove a received report changes the later resource destination
without granting supplies or harvest experience. The raw arc repeats its
identical year-100 terminal row; distinct-year counts exclude that duplicate.

All existing sampled EDEN columns (apart from new knowledge fields) match the
prior version. This is sampled demographic/control evidence, not a claim about
unrecorded state or other seeds. LAGOON's choices/population change; no human
benefit or isolated intelligence gain is inferred. The registry reports
12 supported / 1 contradicted / 4 undecided (H-EDEN-POSTS is contradicted).
No natural human-universe fall occurred in this century; forced lifecycle
checks cover reset/provenance rules. All 285 tests pass on Apple Python 3.9.6.

The default 100 model years/real day remains a target, not measured MacBook
throughput. Current tech knowledge is still world-shared, and the ladder ends
at writing. Source changes alter future trajectories; this is not a complete
digital-human model or a guarantee of civilization.

## Personal resource experience — 2026.10.30.2

Seed 69, 36,000 model days (100 years), eight founding pairs in each world,
from the final source hashes in `docs/audits/2026-10-30-experience/bake-inputs.json`:

| World | Year 100 population | Peak | Highest generation | Recorded outcome |
|---|---:|---:|---:|---|
| EDEN | 456 | 525 | 6 | 239 withdrawn; phase exploit; no extinction/reseed |
| LAGOON | 36 | 36 | 6 | Six technologies, one camp, preserve lesson; no extinction/reseed |

LAGOON reached fire, shelter, preservation, stone tools, fishing and predator
hunting. Lore, agriculture, seacraft and writing were not reached in this arc.
The predefined registry reported 12 supported, 1 contradicted and 4 undecided;
the contradicted claim was complete EDEN post occupancy, not a software test.
Registry support is not scientific validation. No human-universe fall occurred;
forced lifecycle tests cover fresh founders and the separate inherited-tag rule.

The run took 604.9 seconds on the workbench using Python 3.14.6. This is not
2016 MacBook throughput. All 268 tests pass on Apple Python 3.9.6; 22 new causal
cases cover local knowledge, outcomes, exploration, reload, maturation and
nursing. The initial 120-day canonical EDEN comparison matches the previous
release; later EDEN changes are expected from the maturation/nursing fixes.

Population and generation figures have changed from the prior release because
this version alters information, choices and physical/age contracts. The prior
source/provenance remains a separate historical audit. This combined
comparison does not isolate memory's population effect and is not a claim
about historical human growth. Reproduce with:

```sh
python3 tools/lab.py --days 36000 --every 360 --json /your/scratch/arc.json
python3 -m unittest discover -s tests
```

## Audit release 2026.10.30.1

Eight founding pairs per world; four parts per day; default 0.6 seconds per
part = 100 model years per real day. This is a configured pace, not a measured
speed for the 2016 MacBook. Existing saves retain their terrain/season version
and resume with a clock anchor that preserves ticks already due. Engine edits
change their future trajectories.

Food patches now belong to habitat locations rather than camps. Freshwater
banks, fetching, carried water, camp reserves and thirst make drinking distinct
from fishing in saltwater. Both resources deplete and replenish once per shared
place. Dry paths gate resources and animal encounters. Wildlife cannot respawn
from nothing. The retained food-sensitive fertility coefficients are hypotheses,
not a fit to a universal forager growth target.

The first audit arc was superseded after a causal nursing-channel bug: milk
supplied food until age three but supplied water only until six months. The
corrected model credits milk-water through the same nursing window, charging
the mother; no yield, mortality threshold or growth coefficient was tuned.
Private site/child cache keys were also made JSON-safe without changing their
lookup order or trajectory.

The final frozen-source, seed-69 measurement covers **36,000 full days =
144,000 parts = 100 model years**:

```sh
python3 tools/lab.py --days 36000 --seed 69 --every 1800 --quiet --json arc.json
```

| World | Day 3,000 population | Day 36,000 population | Peak | Generations reached | Iteration | Observed outcome |
|---|---:|---:|---:|---:|---:|---|
| EDEN | 34 | 614 | 619 | 6 | 1 | 229 withdrawn; phase label `exploit`; no extinction |
| LAGOON | 25 | 25 | 48 | 5 | 1 | Six technologies; one tribe; no extinction or greater-shore crossing |

Neither universe produced a postmortem or reseeded. **EDEN collapse remains
unobserved.** LAGOON reached fire, stone tools, shelter, fishing, predator
hunting and preservation. It did not discover lore, agriculture, domestication,
granaries, seacraft, healing, metallurgy or writing, and carried no inherited
lessons. Its final camp held 81.5 food units and 42.3 drinking units. Across the
whole terrain, including the unvisited mainland, 593 abstract deer and 0 big
cats remained; wildlife is not automatically replaced after extinction.

The recorded cause-of-death buckets were:

| Cause bucket | EDEN | LAGOON |
|---|---:|---:|
| Immediate infant loss at delivery | 893 | 12 |
| Starvation | 330 | 2 |
| Dehydration | 0 | 61 |
| Violence | 228 | 11 |
| Age | 69 | 16 |
| Accident | 0 | 7 |
| Childbirth | 0 | 2 |

The infant bucket counts immediate birth losses; infants who die later enter
their actual cause bucket. It is not a true infant-survival statistic.
Dehydration dominated LAGOON's recorded deaths, so the registry's starvation-
dominance hypothesis was **contradicted**. This is an outcome of this model's
water demand, access, transport and decision rules, not an estimate of Sri
Lankan mortality or carrying capacity. Resource units, travel reach and
thresholds remain illustrative hypotheses.

The registry returned 14 supported, 1 contradicted and 2 undecided checks; the
two unknown values are EDEN's absent sink-year/sink-gap phase dates. These
checks are not empirical validation. One seed and century do not validate a
millennium, founder genetics, or a guaranteed civilization timeline. The
technology ladder currently stops at writing.

**Validation and provenance.** All 231 tests passed on Apple Python 3.9.6
(547.846s); 22 new resource cases also passed independent review. Raw day-3,000
and day-36,000 saves were checked without migration: identities, reciprocal
bonds, clocks, claims, role holders, food/water bounds, unique shared sites,
shore adjacency, animal IDs and every adjacent annual census stock-flow all
passed. Ready-to-serve fixture events include the server's canonical year.
The final arc's captured source hashes still matched the frozen code after
completion. The raw saves, observer payloads, source hashes, logs and a clearly
superseded first arc are retained in the release audit.

Workbench arc runtime with Python 3.14.6: **1,146.888s** (about 19m7s), with
**42.8 MiB peak RSS**. This includes checkpoint observation and is not a
MacBook throughput guarantee. This audit did not inspect, reset or restart the
live instrument. The legacy yearlings/prior-births observer limitation below
also applies to this version.

## Historical audit release 2026.10.29.1

This engine changes the trajectory of an already running world. All historical tables
below belong to their named earlier engines and are **stale for this release**.
The needs/ecology fixes, world-specific names, and restored eight pairs per
world are documented in DESIGN.md. Migration preserves an existing population
and its food; an explicit restart archives the old run's state, events,
postmortems and books together.

A fresh seed-69 arc was re-derived from the reviewed engine for **60,000 full
simulated days (240,000 parts; 166 complete years plus 240 days)**:

```sh
python3 tools/lab.py --days 60000 --seed 69 --every 1800 --quiet
```

| World | Population at day 36,000 | Population at day 60,000 | Peak | Iteration | Recorded outcome |
|---|---:|---:|---:|---:|---|
| EDEN | 614 | 711 | 723 | 1 | 359 withdrawn; phase label remains `exploit`; no extinction |
| LAGOON | 231 | 435 | 439 | 1 | 13 technologies, three tribes, greater shore reached; no extinction |

Neither world reseeded or produced a postmortem. **EDEN collapse remains
unobserved**; withdrawal alone does not prove a future extinction. LAGOON
carried `preserve` and `cleanliness` and had not discovered writing. This is
one seed and horizon; no parameter was tuned to force an expected ending.

The registry returned 14 supported checks and three undecided: missing EDEN
sink-year/sink-gap phase dates and the inapplicable no-lore Dunbar check. This
is not validation: absent phase dates remain unknown in the registry even
beyond its proposed date range; withdrawal can precede a density phase label.

Raw day-3,000/36,000/60,000 saves passed identity, bond, room, role, store and
clock checks without migration; every adjacent census balanced population
change = births − deaths. Raw evidence is retained in the release audit.

Workbench runtime: **1,345.4 seconds**; a late memory sample was **41.4 MiB
RSS**, not a measured peak or a MacBook benchmark. The live instrument was
not inspected or changed.

**Observer limitation.** The legacy `infant_survival` field is only the capped
ratio of current people aged 360–719 days to births in the latest annual census
(`min(1, yearlings / latest births)`, three decimals; missing if no births).
Its cohorts do not match. It is not true infant survival and supports no
comparison to a clinical or forager survival threshold; the viewer labels it
YEARLINGS / PRIOR BIRTHS. The serialized column remains for compatibility.

## Authorized MacBook restart — pending execution

The owner authorized a fresh start on the instrument. After the MacBook
pulls engine **2026.10.30.1**, the planned restart begins with eight pairs
in each world. **This workbench audit has not reset or restarted the live
MacBook.** Its actual current population and uptime were not inspected.

The explicit reset preserves the prior run in a unique archive directory;
state, events, postmortems and history books move together. Runtime mirror
configuration remains in place. Earlier trajectories are historical and
are not presented as results from this model. Planned MacBook procedure:

```sh
launchctl unload ~/Library/LaunchAgents/com.universe69.sim.plist
python3 sim/server.py --genesis   # once up, Ctrl-C saves the fresh state
launchctl load ~/Library/LaunchAgents/com.universe69.sim.plist
```

The first run's record is kept in the viewer (help card → ABOUT → *The First Run*).

## Historical engine 2026.10.28.4 — eight pairs, real needs, animals with places (re-derived 2026-10-28)

Both worlds start from the same eight pairs. Food is gathered, carried and
eaten by persons; EDEN and LAGOON decide with one function (DESIGN.md).
Every earlier figure in this file is from an engine whose food was a
headcount formula and whose EDEN collapse was a phase script — none of them
carries over. Re-derived with:

```sh
python3 tools/lab.py --days 36000 --seed 69 --every 1800   # and seeds 123, 5
```

| Seed | EDEN y20 | y40 | y60 | y80 | y100 | withdrawn at y100 | LAGOON y20 | y40 | y60 | y80 | y100 | LAGOON peak | tech |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 69 | 78 | 207 | 419 | 650 | 683 | 277 | 46 | 95 | 101 | 164 | 288 | 322 | 12 |
| 123 | 82 | 194 | 386 | 632 | 741 | 299 | 34 | 58 | 88 | 169 | 320 | 348 | 13 |
| 5 | 70 | 156 | 361 | 584 | 739 | 264 | 32 | 62 | 108 | 181 | 222 | 275 | 12 |

What the three seeds agree on, in the first century:

- **EDEN expands and hollows.** Growth is steady (~5%/yr early) and
  flattens after year 80. From year ~50 the withdrawn rise from a handful
  to ~36–40% of the pen, and competent breeding men fall to 4–14. By year
  30 there are already ~2 competent adults per post: Calhoun's role
  saturation. Withdrawal comes from crowding wearing company down at the
  beds and bars, and incompetence from being reared in a crowded nest — the
  sink appears at ~20–30% of the pen's capacity, before the `stagnate`
  label (35%) ever fires. Calhoun's own stagnation began near 16%. No seed
  collapsed within 100 years: whether this pen dies, and when, is the next
  arc to run (`--days 60000`).
- **LAGOON lives, alongside its animals.** No extinction in any seed.
  Bands grow to 222–320 by year 100 (peaks 275–348), split into two or
  three tribes and reach 12–13 technologies; famines still cut them back
  (seed 5 fell from 263 to 181 in the decade before year 80).
  Deer hold at roughly 420–590 and big cats at 0–4, recolonising
  when they die out (animals.py). Predation is real but bounded: in 50-year
  traces (taken before hunters learned to track the nearer cat) it took 0–12 people, mostly before fire and stone tools, and
  people killed 2–4 of the cats that came for them.
- **Calibration flags:** LAGOON's growth (~3%/yr over the century) is above
  the ≤1%/yr the forager literature gives (Howell; Marlowe), so fertility
  or child survival is too generous.

## Historical baseline — 2026.10.28.1

Re-derived from the shipped engine, seed 69, for 60,000 full simulated days
(240,000 parts; calendar year 166):

```sh
python3 tools/lab.py --seed 69 --days 60000 --every 3600 --quiet
```

| World | Final population | Peak | Iteration | Outcome |
|---|---:|---:|---:|---|
| EDEN | 926 | 1,802 | 1 | Death phase; no extinction or reseed yet |
| LAGOON | 463 | 470 | 2 | Survived after one extinction; 13 technologies, two tribes, greater shore reached |

EDEN's sink began in year 86 and its death phase in year 104. This run does
**not** establish when EDEN will empty. LAGOON carried two lessons at the end.
These are model outcomes, not measurements of human societies.

The raw observer report returned 15 supported checks and two contradictions.
One was a reporting defect: the Dunbar check says *without shared lore*, yet
it judged a terminal society that already had lore. The read-only research
layer was corrected after the trajectory run; the engine was unchanged.
Re-evaluating applicability from the terminal technology list yields
**15 supported, one contradicted, one undecided**. The remaining contradiction
is EDEN's posts: 89.7% held against the implementation's 99% threshold. It
remains reported; the model was not tuned to turn it into a pass.

The raw arc/log and the separate observer correction are retained with the
release audit evidence. Earlier studies below are historical and stale.

---

Earlier-study engine state at the time of writing: seed 69, `DAYS_PER_YEAR = 360`,
`ADULT_AGE = 16 years`, `GESTATION = 270 days`.

---

## 1. Could two pairs of young people reach 2,000 in a hundred years?

**Yes — demographically, easily. And in EDEN they never do, which is the
finding.**

The experiment was run twice: once with the pen as built, and once with the
pathology removed so that only the demography remained.

```sh
python3 tools/sweep.py --study default
```

| population first reached | pen as built | pathology removed |
|---|---|---|
| 50   | year 23 | year 23 |
| 100  | year 30 | year 30 |
| 200  | year 39 | year 39 |
| 500  | year 56 | year 50 |
| 1000 | never | year 58 |
| 2000 | never | **year 67** |
| 3000 | never | year 74 |

Peak population: **752** (pen as built, year 78) against **4000+** (pathology
removed, still climbing when the run was stopped).

The demographic engine is not slow. A woman conceives with probability
1/180 per day and carries for 270 days, so each woman bears roughly a child
every 450 days — from 16 to 45, that is about 23 children. With a 16-year
maturation the population roughly doubles every two years once the second
generation starts breeding, and two pairs reach 2,000 in **67 years**.

So the ceiling in EDEN is not human fertility. It is the pen.

**And the pen's size is the whole answer.** The table above uses the pen as
built: capacity 900, 32 nest boxes. Run the same seed in a pen of Calhoun's
proportions — capacity 3,840, 256 boxes of 15 — and **2,000 people are
reached in year 75**, the population peaks at 2,866, and it holds there for
roughly 150 years before the same collapse arrives. The answer to "could they
populate 2,000?" is therefore *yes*, and it was the pen, not the biology, that
was saying no.

## 2. The pen has two capacities, and they disagree

The UI now prints both, because the disagreement is the mechanism:

> **PEN: 32 NEST BOXES · 224 PLACES · CAP 900**

`EDEN_CAP = 900` is the pen's nominal capacity. The pen actually has 32 nest
boxes of 7 places each — **224 socially meaningful places**. At the peak of
752 people that is **3.4 times as many people as there are places to have a
territory**, and 71 adults have no territory at all.

Calhoun's Universe 25 had 256 boxes and about 15 mice per box — 3,840
nominal places, and a peak near 2,200. The ratio of peak to nominal was
about 0.57. This pen peaks at 0.84 of its declared capacity, and 3.36 of its
real one.

**Which number is right is a research question, not a detail.** That is why
the pen's architecture is now a parameter rather than a constant:

```sh
python3 tools/sweep.py --study calhoun     # Universe 25 as Calhoun built it
python3 tools/sweep.py --study boxes       # vary the number of nest boxes
python3 tools/sweep.py --study crowding    # vary where the sink begins
```

### The pen's architecture barely matters

Five pens, each run to extinction and reseeding, seed 69:

| pen | peak | peak year | extinction | reseed |
|---|---|---|---|---|
| Universe 25 as built (256 boxes × 15, cap 3840) | 2866 | 92 | 279 | 309 |
| same boxes, sink at 35% | 2914 | 100 | 250 | 280 |
| same boxes, sink at 10% | 2912 | 101 | 284 | 314 |
| 256 boxes of 8 (2048 places) | 2920 | 100 | 288 | 318 |
| 128 boxes of 15 (1920 places) | 2933 | 101 | 294 | 324 |

**Every pen collapses on the same schedule.** Halve the nest boxes, shrink
each box, or move the crowding threshold from 10% to 35%, and the peak stays
within 2% of 2,900 and the extinction within 40 years of the others.

Two things follow.

First, **the model reproduces Calhoun's shape.** His Universe 25 peaked near
2,200 around day 560 and was functionally extinct by day ~1,600. This pen, in
his proportions, peaks at 2,866 in year 92 and empties in year 279 — the same
arc, stretched to human generations.

Second — and this is the uncomfortable part — **this model does not support
the critique recorded in RESEARCH.md.** Ramsden and Adams argue the outcome
tracked the *architecture*: that the design funnelled animals into contact,
and that outcomes were design-dependent rather than an iron law of crowding.
In this model the architecture is close to irrelevant. What drives the
collapse is the fertility-versus-crowding feedback, and the sink threshold
merely sets when it starts. If the critique is right, then the mechanisms
that make *architecture* matter — the funnel, the territory, the crowding of
the roles — are under-modelled here. The box system currently records who
holds a place; it does not yet make *where* the places are shape the
behaviour.

## 3. The arc of Universe 6, measured

```sh
python3 tools/lab.py --days 120000  # current harness; historical figures below were not rerun
```

| year | what happens |
|---|---|
| 0   | the pen opens: two pairs, eighteen years old |
| 1   | first child born — the exploit phase begins |
| 45  | crowding passes 35% — **the behavioural sink emerges** |
| 56  | deaths outnumber births for three years — **the death phase begins** |
| 234 | **UNIVERSE 6 HAS DIED.** Peak 752, generation 6. Postmortem written. |
| 264 | the Observers reseed the pen. Iteration 2 begins. |

The postmortem records the cause table `{infant 952, age 571, violence 384,
plague 24}` and the verdict: *nothing within the walls could have prevented
this — the pen itself is the cause.*

**On the duration.** From the peak at year 78 to the empty pen at year 234 is
156 years — about ten generations at a 16-year maturation. Calhoun's mice
went from their peak at day 560 to the last conception around day 920 and to
extinction by 1973: roughly thirteen mouse-generations. The long, slow
collapse in this model is not a bug in the demography; it is the correct
human-scaled analogue of a mouse-scaled event.

**Retired forecast.** The earlier study forecast a first extinction near
year 234 from a run then near year 115, using the former two-second day.
That forecast is stale under `2026.10.28.1`; it makes no claim about the
instrument's present state or when its first postmortem will occur.

## 4. The two universes diverge, and the reason is worth knowing

The earlier study's engine from genesis did **not** reproduce the live run's
history, even though it was deterministic per `(seed, day)` within its version.

| | EDEN | LAGOON |
|---|---|---|
| live run (day 41,149) | 485 people, year 114 | **251 people**, year 114 |
| fresh run, same engine | 480 people, year 113 | **22 people**, year 113 |

EDEN tracks closely. LAGOON does not: the fresh run stalls at 22 people with
seven technologies, while the live run reached 251 and crossed to the
continent.

The cause is that determinism holds only *within one engine version*. The
live run has been ticking through many engine rewrites and restarts since it
began; each change re-rolls the trajectory from that day on. The claim in
`DESIGN.md` — "deterministic per seed+day" — is true within a version and
false across the history of a long run.

What this costs: **no figure derived from the live run can be re-derived
later.** The fix is to version the engine and record its version in the state
and in every postmortem, so a published number can always be traced to the
code that produced it. Until that exists, treat any number taken from the
live history as a record of *that run*, not a property of the model.

## 5. What is deliberately not claimed

- These are measurements of a **model** built from the literature in
  `RESEARCH.md`, not of people.
- The numbers above come from **one seed**. The pen's design sweep exists
  because a single run is an anecdote about a single run.
- The causes of death in the EDEN postmortem are cumulative over the whole
  iteration, so "infant" dominating that table describes *how* the last
  generation failed, not the proximate cause of the pen emptying.
- **A place emptied by death is never taken again** by the people who were
  already displaced. The viewer shows this directly: amber nest boxes are
  held, green ones are vacant, and the status line reads *"61 without
  territory · 85 places vacant, never refilled"*. That is the model's
  reading of Calhoun's "death squared" — the social death precedes the
  physical one — and it is why the boxes can be a third empty while a fifth
  of the pen has nowhere to go.
