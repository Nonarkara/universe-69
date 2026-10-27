# UNIVERSE 69

Two sealed pixel universes living continuously on an old laptop, observed but
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
  10 min). The vanity name `universe.nonarkara.org` has **no DNS record** —
  it needs a CNAME to `nonarkara.github.io` in Cloudflare, plus the custom
  domain set in the repo's Pages settings.

## Time

1 sim-day every 2 real seconds → ~118 sim-years (5–6 generations) per real
day. The clock is anchored to a genesis epoch: if the laptop sleeps or the
process dies, the engine fast-forwards the missed days on wake, like a
Tamagotchi that kept living in the dark.

## The rules of the game

The Observers never intervene. When a universe dies, a **postmortem** is
written (`data/postmortems/`): what happened, how, the dominant cause of
death, whether it was preventable. Thirty quiet years later the world is
reseeded — and in LAGOON the new founders carry the **lessons** of the dead
iterations as wordless instinct (faster to preserve food if starvation won,
warier of the woods if predators won, cleaner around the herds if sickness
won). Survivors of a near-wipe learn the same way, without going extinct
first. EDEN is reseeded under identical conditions every time, because
Calhoun's finding was precisely that nothing inside the pen can save it.

## Running

```sh
./run.sh                  # foreground
python3 tools/chronicle.py  # digest new events into data/chronicle/
```

The live run lives on the 2016 MacBook (a LaunchAgent keeps it alive 24/7).
This repo is the workbench; the 2016 Mac is the instrument.

## Working on the model

The engine ticks roughly 1,000 sim-days per second, but the live run advances
one sim-day every two real seconds. Do not tune the model against the live
run — use the lab bench:

```sh
python3 tools/lab.py --days 60000          # a whole arc, in about a minute
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
RECORD` is a console: every event, filterable by universe and by
LIFE / WORLD / END.

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
sim/engine.py      the model (pure stdlib, deterministic per seed+day)
sim/server.py      tick loop, HTTP viewer, snapshot uploader
web/index.html     chunky-pixel renderer (also deployed to docs/)
docs/              GitHub Pages mirror (reads the gist snapshot) + design laws
tools/lab.py       fast local harness — run a century in seconds
tools/chronicle.py mechanical event digest
tests/             unittest suite (engine behaviour + viewer data contract)
data/              state, events.ndjson, chronicles, postmortems (local)
```

No dependencies, no build step, no framework. 8-bit honesty throughout.
