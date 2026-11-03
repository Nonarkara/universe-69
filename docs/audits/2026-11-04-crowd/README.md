# The crowd test — skinned humans at population — 2026-11-04

Task: finish what the skinned-humans session left open — measure the viewer
under a big population instead of asserting the 40-body budget holds, and put
the numbers on the record.

## How the crowd was made

No live state was touched. A bounded lab arc (`engine.genesis(seed=69)` plus
`tick_world`, the same code path as `tools/lab.py`) grew EDEN to 169 people at
year 114 — within the pen's documented peak range (STUDY.md: live EDEN peaks
255/229/240; the current engine grows slower than the older sweeps the
2,866-peak figure came from). The state was served on a development instance
(`UNIVERSE69_PORT=6975`, `UNIVERSE69_DATA` in agent scratch), never on :6969.

## Measured (desktop Chromium, 1440×900, this workbench Mac)

- inside EDEN at human scale: **59.9 fps median** (16.7 ms, p95 17.5 ms) with
  169 people — exactly **40/40 skinned figures**, 256 draw calls, 2.08 M
  triangles; the rest of the crowd stays instanced as designed
- VR table view (both worlds): 59.9 fps median
- 2D terrarium (`index.html`) with the same population: 59.9 fps median
- no page errors or console errors in any run
- one-screen law: `scrollHeight == innerHeight` at 1024×768 and 390×844
- `tools/shoot.py --interact` full pass at 390/1024/1440: zero clipping, zero
  errors, every reader paginates completely, pagination and person-card stress
  pass (`viewer-report.json`)

The instanced layer holds 1,000 people per world, 3.9× the documented live
peak; the skinned layer is budget-capped regardless of population.

## Retained

- `crowd-169.json` — the full measurement (fps, scene stats, scroll checks)
- `viewer-report.json` — the three-viewport interact report
- `vr-inside-1440.png`, `vr-table-1440.png`, `vr-table-1024.png`,
  `vr-table-390.png`, `study-1440.png` — the viewports and the figure study

## Not verified here

- Meta Quest frame rate in a headset (no Quest on the workbench)
- the 24-figure headset budget (XR-gated code path, reviewed not run)
- anything about the live run on the 2016 MacBook — the engine is untouched
  and the MacBook only needs `git pull`
