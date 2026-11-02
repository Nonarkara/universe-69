# Bounded runtime diagnostic — 2026-11-03

**The main hotspot is repeated social candidate eligibility scanning.** This is a 50-day continuation diagnostic on the workbench, not live data, a new-genesis century or a MacBook throughput measurement. No production source, parameter or model tuning was performed.

## Input and execution

Loaded the exact retained [seed 69 .8 final world](../../2026-10-30-agency/arcs/seed-69/final-world.json.gz), validated/migrated it under frozen engine 2026.11.03.1 and called `engine.tick_world` directly for 200 parts. No server import, service change, wall-clock waiting or clock rebasing. Apple Python 3.9.6 on arm64 Darwin; concurrent century jobs were active. Every imported model source and all 13 recorded simulation source files stayed byte-identical during both runs.

This input is the **old cohort and terrain**: iteration 1, fseed 69; EDEN seed 489, LAGOON seed/terrain_seed 492 and terrain_version 2. Current genesis uses terrain_version 3. The inherited state must not be confused with the new-genesis frozen-century results. Starting engine tags are 2026.10.30.8; the first tick records the transition to 2026.11.03.1.

| | Before migration/run | After 200 parts |
|---|---:|---:|
| Global day (both worlds) |36000|36050|
| EDEN population |243|243|
| LAGOON population |25|25|
| Iteration (both) |1|1|
| Max generation (both) |6|6|

## Timing and CPU attribution

| Measurement | Profiled 200 parts /50 days | Unprofiled 60 parts /15 days |
|---|---:|---:|
| Mean tick wall time |523.50 ms|60.82 ms|
| p95 tick wall time |1119.95 ms|93.07 ms|
| Maximum tick wall time |2440.89 ms|268.35 ms|

p95 uses nearest rank. These durations include scheduling/contention; the profiled column additionally includes substantial instrumentation overhead. The matching first 60 profiled ticks average 311.20 ms versus 60.82 ms unprofiled (observed ratio 5.12×). Different horizons/action mixes make the full 200 and 60 columns unsuitable as a pure overhead comparison. No result establishes throughput or a safe operating pace on the 2016 MacBook.

`cProfile` uses `time.process_time` as its timer: 93.591s attributed process CPU across 103,638,452 calls. Top 10 by self CPU (cumulative includes callees and must not be summed):

| Function | Calls | Self CPU seconds | Cumulative CPU seconds |
|---|---:|---:|---:|
| `<method 'get' of 'dict' objects>` |80,386,916|30.722|30.722|
| `encounters.py:28 available` |5,901,989|29.313|51.995|
| `encounters.py:43 _compatible` |3,086,383|7.467|64.956|
| `encounters.py:72 <listcomp>` |18,582|2.045|67.076|
| `needs.py:1798 <listcomp>` |9,682|1.396|3.140|
| `<built-in method builtins.any>` |410,233|1.363|45.584|
| `needs.py:793 <dictcomp>` |53,600|1.184|1.184|
| `needs.py:536 meters` |53,600|0.911|5.802|
| `needs.py:412 observe_sites` |55,657|0.854|3.151|
| `engine.py:1098 tick_eden` |200|0.848|80.194|

The cumulative path is `tick_world → tick_eden → needs.update_social → encounters.offer/candidates → _compatible → available`. Candidate scanning consumes 67.108s cumulative in this CPU profile; `update_social` contributes 44.486s nested within that path. The source checks compatibility before sight distance, so many far-away candidates still incur eligibility reads. These are measured locations/counts, not permission to remove guards or change the frozen model. Instrumentation can distort relative costs, especially very frequent small calls; no unprofiled CPU-share claim is made.

## Profiling parity

The first 60 profiled parts and an independent unprofiled 60-part process produced **identical persisted world and event hashes**. Both use `PYTHONHASHSEED=0`; RNG/state is not mocked. Canonicalization uses actual `engine.save_state`, omits its universe runtime caches, sorts JSON keys and ignores only `epoch`/`wall` timestamp metadata. Clock counters, bodies, decisions, pregnancies, resources, lineage and other persisted fields remain in the comparison.

World SHA256: `e85a8591040cb9d84e70af51b1598284ee151f4d509f1e662034486cf0432d32`.

Event SHA256: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.

No events were emitted in this short window, so event parity here covers matching empty logs, not every birth/disaster/death branch. This bounded result does not prove profiling equivalence for all possible states. No extrapolation to survival or extinction is made.

## Reproduction and retained evidence

```sh
/usr/bin/python3 docs/audits/2026-11-03/runtime/profile_runtime.py --out /Volumes/Data/agent-scratch/u69-nov3-runtime
```

[Results](results.json) contain 200 raw tick wall samples, both source manifests, input hashes, population checkpoints, top 10 self/cumulative functions and parity hashes. [CPU profile](engine-200parts.prof), [readable top 10](profile-top10.txt), [terminal log](run.log), [manifest](manifest.json) and [runner](profile_runtime.py) are retained. The input already exists in its historical audit and is not duplicated. Temporary persisted comparison states are not committed; the runner regenerates them. This diagnostic is distinct from the parent’s current-genesis centuries.
