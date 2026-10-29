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


## Island and people — 2026-10-30

New LAGOON worlds use a Sri Lanka-inspired tropical coastal analogue: shared
forest food patches, fish at actual shores, moving game, finite freshwater
banks and cultivable land. People must reach and work their resources; a new
camp cannot create another copy of a depleted patch. Wet/dry seasons change
renewal. Existing saves retain their original terrain and seasonal regime.
The map is procedural, not a surveyed replica; see RESEARCH.md for sources
and the model's limits.

The anatomy rig keeps age/sex proportions and fixed bone lengths. Walking
stride follows actual leg size and distance travelled, with a shared stance
law and frame-rate-independent movement. Sleeping arms now reach their pose,
bedrolls fit their bodies, and age changes invalidate the sprite cache.

Engine `2026.10.30.4` changes future trajectories through personal procedures,
actual practice and local camp works. The `.3` contact-based resource sharing remains. The `.2` personal memory, maturation and nursing
corrections remain in force;
the earlier `2026.10.30.1` resource changes remain in force. The century-per-day clock
preserves previously completed time when its pace changes. Existing
`UNIVERSE69_SEC_PER_PART` overrides still take precedence; remove an old
explicit override to use 0.6 seconds. A faster clock does not guarantee
survival or civilization: the current ladder ends at writing.

Each extinction now has an independent report in `data/history-books/` and
a **Runs** view inside Research. It does not wait for both worlds to die.
Counts describe a cumulative iteration; inherited lessons remain hypotheses,
not proven remedies. Explicit restarts archive the ledger with the old state.
This observer change does not change engine trajectories.

The larger digital-human objective remains in progress; see
[the capability audit](docs/audits/2026-10-30/capabilities.md).

People now remember locally seen resource locations and quantities, learn
from physical uses, and scout when known supplies are missing. They retain
stale beliefs about distant patches and camp stores instead of reading those
reserves instantly. Capacity and forgetting are explicit model assumptions;
this is spatial resource learning, not general human cognition. Newborns and
reseeded founders do not inherit another person's memories.

Completed conversations/grooming now pass bounded resource reports with the
original observer/date, sender and relay path. Retelling does not refresh old
information or grant personal harvesting experience. Reports can be stale;
technology knowledge still remains world-shared, and general cognition is
unimplemented. Both worlds use the same contact policy.


Historical technology is now a discovery record. Individuals learn procedures
through contact, observation and actual practice; new children do not inherit
them automatically. The old-save capability assumption is explicitly labelled.
Physical fires, prepared food and completed works belong to camps. See
[the procedure audit](docs/audits/2026-10-30-skills/README.md) for final verification
and limitations. This remains a finite simulation, not human-level cognition or
a guarantee that a great civilization will emerge.
