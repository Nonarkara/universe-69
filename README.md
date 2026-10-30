# UNIVERSE 69

Two sealed universes living continuously on an old laptop, observed but
never helped. Universe **6 — EDEN** is John Calhoun's Universe 25 rebuilt for
humans: free food, perfect climate, free mating, bounded space. Universe
**9 — LAGOON** is the first-sapiens world: a lagoon, woods, game, predators,
seasons — nothing given, everything earned.

- **Research basis:** [RESEARCH.md](RESEARCH.md) (Calhoun 1968–73; Love, Death
  & Robots "Ice Age"; Harari's *Sapiens*; Diamond's *Guns, Germs, and Steel*)
- **Model mapping:** [DESIGN.md](DESIGN.md)
- **Measurements:** [STUDY.md](STUDY.md) — what the running universes actually
  did, and the commands that re-derive every number in it
- **Live local view:** http://localhost:6969
- **Live web mirror:** https://nonarkara.github.io/universe-69/ (snapshot every
  10 min). `universe.nonarkara.org` is an optional vanity hostname; its
  current DNS and Pages deployment were not verified in this code audit.

## Time

Dawn, day, dusk and night take 0.6 real seconds each: 2.4 seconds per
simulated day, **100 simulated 360-day years per real day**. A millennium
takes ten real days at this pace. Eight pairs found each world at day zero;
their descendants replace them through actual births, aging and deaths. The saved cumulative clock
catches up after sleep or restart. `UNIVERSE69_SEC_PER_PART` changes the pace
without replaying completed time.

## The rules of the game

The Observers never intervene. When a universe dies, a **postmortem** is
written (`data/postmortems/`): what happened, how, the dominant cause of
death, whether it was preventable. Thirty quiet years later the world is
reseeded — and in LAGOON the new founders carry the **lessons** of the dead
iterations as wordless instinct (faster to preserve food if starvation won,
warier of the woods if predators won, cleaner around the herds if sickness
won). Survivors of a near-wipe learn the same way, without going extinct
first. EDEN is reseeded under identical conditions every time, because
the two worlds have different experimental conditions. The phase names
describe the current model; they do not force a collapse.

## Running

```sh
./run.sh                  # foreground
python3 tools/chronicle.py  # digest new events into data/chronicle/
```

The live run lives on the 2016 MacBook (a LaunchAgent keeps it alive 24/7).
This repo is the workbench; the 2016 Mac is the instrument.

For the planned new run, pull the audited commit on the MacBook, stop its
LaunchAgent, then run `./run.sh --genesis` in the checkout. This explicitly
archives the previous run before starting the new founders. Stop that
foreground instance before loading the LaunchAgent again. Do not run two
instances against the same data directory. Use `STUDY.md` for the recorded
restart procedure and model-version caveats.

Development instances must set both `UNIVERSE69_PORT` and `UNIVERSE69_DATA`,
with scratch data under `/Volumes/Data/agent-scratch/`; never use live `data/`.

## Working on the model

The live run advances through dawn, day, dusk and night: one part every
0.6 real seconds, 2.4 seconds per simulated day. Test changes with the
lab bench; century runs can take minutes, depending on population:

```sh
python3 tools/lab.py --days 60000          # a whole arc
python3 tools/lab.py --days 60000 --quiet  # just the verdict
python3 tools/lab.py --days 60000 --json arc.json
```

`lab.py` prints the year-by-year arc of both universes and a verdict: did EDEN
actually empty the pen, did LAGOON learn its lesson, which technologies were
reached. That verdict is the thing to check after any change to the engine.

`tools/sweep.py` varies the pen itself — the number of nest boxes, their
size, the pen's capacity, where the behavioural sink begins — because
Calhoun's conclusion is that the outcome tracks the *design* of the pen:

```sh
python3 tools/sweep.py --study calhoun     # Universe 25 as Calhoun built it
python3 tools/sweep.py --study boxes       # vary the number of nest boxes
python3 tools/sweep.py --study crowding    # vary where the sink begins
```

```sh
python3 -m unittest discover -s tests   # the suite
```

## Watching

The viewer is a camera you can take: **wheel** zooms, **drag** pans, **click a
person** follows them, **escape** gives the camera back to the documentary
eye. The lower-third card names whoever you picked — age, generation, their
nest box, their partner, and why they are the way they are. `THE OBSERVER'S
RECORD` keeps events filterable by universe and by LIFE / WORLD / END.
The record, Research, Book and First Run archive use Prev/Next pages, arrow
keys and swipes. Both worlds remain on the first screen: side by side on
wide screens, stacked on phones.

24/7 via launchd:

```sh
cp com.universe69.sim.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.universe69.sim.plist
```

A scheduled Claude task (`universe69-chronicle`, nightly) writes the
narrative Observer's Record from the event log and pushes the chronicle to
this repo.

## Layout

```
AGENTS.md         the standing instructions for every agent (design laws live here)
sim/engine.py      the model (pure stdlib, deterministic per seed+day+part)
sim/server.py      tick loop, HTTP viewer, snapshot uploader
web/index.html     full-resolution terrarium renderer (also deployed to docs/)
docs/              GitHub Pages mirror (reads the gist snapshot) + design laws
tools/lab.py       fast local harness — bounded arcs without wall-clock delay
tools/chronicle.py mechanical event digest
tests/             unittest suite (engine behaviour + viewer data contract)
data/              state, events.ndjson, chronicles, postmortems (local)
```

The simulation has no external dependencies or build step. The viewer uses
the TERRARIUM palette, Jost for controls and Source Serif 4 for reading.
`GRAPHICS.md` and `tests/test_style.py` define the rendering contract.


## Current model

New LAGOON worlds use a Sri Lanka-inspired tropical coastal analogue: shared
forest food, shore fishing, moving game, finite freshwater and cultivable land.
People must reach and work their resources; camps cannot duplicate a depleted
patch. Wet/dry seasons change renewal. Existing saves retain their original
terrain and seasonal regime. This is a procedural analogue, not a surveyed
island replica; see RESEARCH.md for sources and limits.

People use an anatomy rig with age/sex proportions and fixed bone lengths.
Walking stride follows actual leg size and distance travelled, with a planted
stance law and frame-rate-independent motion. Sleeping poses and bedding fit
the body; age changes invalidate the sprite cache.

People remember locally observed resources, retain stale beliefs about distant
supplies, scout and exchange bounded reports with original dates and relay
paths. Newborns do not inherit personal memories. Procedures belong to people:
observation, instruction and actual practice differ. A witnessed expert can be
sought at their last seen location; both teacher and learner choose against
their own needs. Fires, prepared food and completed works belong to camps.
Historical technology labels record discoveries, not universal competence.

Engine `2026.10.30.7` uses genuine reproductive exposure days and individual
variable cycles. One clinical-pregnancy outcome is allocated after the model
ovulation day closes. Duplicate contact parts and reloads add no extra trials.
Actual father/trait records survive later social changes. Invitations never
assign the recipient's action; pending poses are neutral, and actual contact
controls the joint adult picture. Labour appears before delivery and helpers
choose independently. Existing pregnancies survive migration. **This changes
future trajectories.** The six-day benchmark, maximum-exposure approximation,
cycle prior and physiology modifiers remain explicit model assumptions.

## Time, records and limits

The default clock is **100 model years per real day**, with four parts per day
and 360 days per model year. Pace changes preserve previously completed time.
An existing `UNIVERSE69_SEC_PER_PART` override still wins; remove an old override
to use the default 0.6 seconds per part. A faster clock guarantees neither
survival nor civilization; the predefined technology ladder ends at writing.

Each extinction has its own report in `data/history-books/` and a **Runs** view
inside Research. It does not wait for both worlds to die. Counts describe a
cumulative iteration; inherited lessons are hypotheses, not proven remedies.
Explicit restarts archive the ledger and old state.

The digital-human objective remains in progress. This is a finite model of
candidate dynamics, not general human cognition or a validated population
forecast. In the frozen `.7` century runs, LAGOON seeds 7/25 reach maternal
generation six with 30/29 people; seed 69 retains five older men. EDEN stops at
generation two in all three cases. Younger cohorts support further study;
positive headcount alone does not prove demographic viability.

## Verification

The [reproductive-cycle audit](docs/audits/2026-10-30-fertility/README.md)
contains primary-source boundaries, controlled/cross-runtime probability checks,
the three source-bound century runs and natural checkpoint screenshots. The
phone header keeps the selected name while full activity remains in the card
and canvas caption, recovering scene space without removing information.

Earlier versioned evidence remains available:

- [Capability boundaries](docs/audits/2026-10-30/capabilities.md).
- [Personal procedures and local works](docs/audits/2026-10-30-skills/README.md).
- [Purposeful instruction](docs/audits/2026-10-30-instruction/README.md).
- [Actual encounters and the historical fertility failure](docs/audits/2026-10-30-encounters/README.md).
