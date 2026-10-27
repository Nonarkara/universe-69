# STUDY — measurements from the running universes

Every number below was produced by running the **shipped** engine in this
repository, not quoted from a log, a paper, or an earlier bake. Each section
names the command that reproduces it. If the engine changes, re-derive: a
figure that no longer comes out of the code is no longer a finding.

Engine state at the time of writing: seed 69, `DAYS_PER_YEAR = 360`,
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

## 3. The arc of Universe 6, measured

```sh
python3 /tmp/eden_arc.py     # or: python3 tools/lab.py --days 120000
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

**The live run is about to complete its first cycle.** The 2016 MacBook's
universe stands at year 115. The pen empties at year 234 — about 43,000
sim-days away, which at one sim-day every two seconds is roughly **one day
of real time**. The first EDEN postmortem and the first reseeding are close.

## 4. The two universes diverge, and the reason is worth knowing

Running the current engine from genesis does **not** reproduce the live run's
history, even though the engine is deterministic per `(seed, day)`.

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
