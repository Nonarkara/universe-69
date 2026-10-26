# UNIVERSE 69

Two sealed pixel universes living continuously on an old laptop, observed but
never helped. Universe **6 — EDEN** is John Calhoun's Universe 25 rebuilt for
humans: free food, perfect climate, free mating, bounded space. Universe
**9 — LAGOON** is the first-sapiens world: a lagoon, woods, game, predators,
seasons — nothing given, everything earned.

- **Research basis:** [RESEARCH.md](RESEARCH.md) (Calhoun 1968–73; Love, Death
  & Robots "Ice Age"; Harari's *Sapiens*; Diamond's *Guns, Germs, and Steel*)
- **Model mapping:** [DESIGN.md](DESIGN.md)
- **Live local view:** http://localhost:6969
- **Live web mirror:** https://universe.nonarkara.org (snapshot every 10 min)

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
sim/engine.py      the model (pure stdlib, deterministic per seed+day)
sim/server.py      tick loop, HTTP viewer, snapshot uploader
web/index.html     chunky-pixel renderer (also deployed to docs/)
docs/              GitHub Pages mirror (reads the gist snapshot)
tools/chronicle.py mechanical event digest
data/              state, events.ndjson, chronicles, postmortems (local)
```

No dependencies, no build step, no framework. 8-bit honesty throughout.
