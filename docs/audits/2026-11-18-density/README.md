# 2026-11-18 — crowds stop standing inside each other

One viewer-only drawing change in `web/index.html` (byte-identical in
`docs/index.html`), no engine change, no trajectory moved: GRAPHICS.md §6
item 1, closing the last open clause — separation between people who are
**not** on the same tile but whose drawn sprites still overlap.

The same-tile fan (`d02775f`, radius uncapped 2026-11-01, crowds > ~9
shrink toward 0.4×) kept the record's one-body-per-tile rule honest.
What it could not see is two people on *neighbouring* tiles whose sprites
land on top of each other — and what it leaves behind in a crowd that
spills past its tile edge, which is exactly what an uncapped radius does.
The fan decides who is drawn and how big; this pass decides where the
pixels land. It runs **after** the fan and **before** the y-sort:

```
var crowd={};                // the fan (unchanged)
(function separateOverlapping(){ … })();   // new
list.sort(function(a,b){ return (a.y+a.nudgeY)-(b.y+b.nudgeY); });  // the y-sort
```

Mechanics, for the record:

- **Display only.** The one write back to the record's actor is
  `a.nudge` — the same display offset the fan already uses. `positions`,
  `actors`, the save file and the snapshot are untouched; nothing here is
  a measurement of the model.
- **Eligibility:** still (`!moving`), uncoupled (`!coupled[a.id]`) people,
  excluding anyone lying down — `A_SLEEP` (17), `A_MATE` (8) — and anyone
  with `stage===0` (infants). The fan and the sleeping mats carry the
  prone; this pass never repositions them. `drawAct` is honoured when
  present, so a person *acting* asleep is excluded even if `act` has
  moved on.
- **Overlap test:** torso half-width `0.13·STATURE[ab]·FAT_W[fat]·crowdScale`
  and height `1.68·STATURE[ab]·crowdScale` per person; a pair is
  overlapping when the x-gap is below the summed half-widths **and** the
  y-gap is below `0.92·min(h₁,h₂)`. Bodies at different depths (a person
  1+ tile behind another) are never touched.
- **Separation:** 1-tile grid buckets; up to 3 deterministic relaxation
  sweeps, re-bucketing after each sweep so the cells stay honest. Each
  overlapping pair is pushed apart symmetrically in x by
  `min(0.75, (w₁+w₂)−|dx|)/2 + 0.015)` per side; a dead-stack pair
  (|dx| < 1e-4) resolves by actor id parity. Maximum travel is a tile
  and a half per sweep per pair. Pair order is by actor id, so the result
  is reproducible frame to frame.
- Scratch state lives in a local array of plain objects — the actors
  are read once and written once (`nudge`); there are no per-frame
  property adds/deletes on the actors themselves.

## What the frozen record says (the defect, measured)

Probed on the frozen EDEN record at `Y617 · DAY · POP 123` (deployed
snapshot, read-only preview on `127.0.0.1:6992`), replicating the fan
exactly and then counting genuine cross-tile pairs:

| probe | value |
|---|---|
| max same-tile occupancy | 3 (tile 50,23); eight tiles at 2 |
| cross-tile overlapping still-person pairs | **20** |
| pair coordinates | dx ≈ 0–0.3, dy ≈ 0.1–1.1 |
| cluster tiles | (50,23)/(49,23)/(50,24) — the hopper crowd, ids 17, 43, 57, 25, 74 — and (24,48)/(24,49) — ids 31, 45, 48, 54 — plus (50,52) — ids 26, 27 |
| acts involved | A_FARM 5, A_PLAY 15, A_WORK 18, A_WATCH 20, A_DRINK 22 |

(LAGOON's frozen record holds 17 people at the same clock; no pair there
ever met the test — the defect is EDEN's hopper crowd, and it scales
with local density, not with population.)

After fan + separation, on the same frozen record
(`probe_density2.py`, replicating the full pipeline):

| probe | value |
|---|---|
| residual overlapping pairs | **0** |
| sweeps to convergence | 3 |

## Evidence (captured from the real interface)

Frozen frames: deployed snapshot served read-only at `127.0.0.1:6992`
(before, the 6b build) and a scratch copy at `127.0.0.1:6994` (after;
never deployed). Live frames: updated `web/` served at
`127.0.0.1:6991` through the read-only proxy to the live instrument.
Every frame read `#hud6 .clock` before and after the shot and matched
in every case; zero pageerrors in every capture.

| file | viewport | clock label in the frame |
|---|---|---|
| dens-before.png | 1440, EDEN node 50/23.6 th 2.2 | Y617 · DAY · POP 123 |
| dens-after.png | same, after | Y617 · DAY · POP 123 |
| dens-after-recheck.png | same camera, after the inline-scan optimisation | Y617 · DAY · POP 123 |
| dens2-before.png | 1440, EDEN node 24/48.5 th 2.2 | Y617 · DAY · POP 123 |
| dens2-after.png | same, after | Y617 · DAY · POP 123 |
| msh-density-day-camp-390.png | 390 | Y641 · DAY · POP 210 |
| msh-density-night-camp-390.png | 390 | Y641 · NIGHT · POP 210 |
| msh-density-day-camp-1024.png | 1024 | Y641 · DAY · POP 210 |
| msh-density-night-camp-1024.png | 1024 | Y641 · NIGHT · POP 210 (after retry) |
| msh-density-day-camp-1440.png | 1440 | Y641 · DAY · POP 210 |
| msh-density-night-camp-1440.png | 1440 | Y641 · NIGHT · POP 210 |
| msh-density-day-island-1440.png | 1440, EDEN rung | Y641 · DAY · POP 210 |
| msh-density-night-island-1440.png | 1440, EDEN rung | Y641 · NIGHT · POP 210 |

The MSH set was taken at the live state (Y641 · POP 210; LAGOON POP 16
in the same frames): camp at 390/1024/1440 DAY+NIGHT and island at
1440 DAY+NIGHT. The 1024 NIGHT frame rolled the part on every first
attempt (the part clock flips every ~2.5 s of real time) and was
re-taken with a 60-attempt loop; only the verified frame is kept.

**The dens-after witness.** The hopper crowd — drawn interpenetrating
in dens-before.png, one mass with limbs — reads as five distinct figures
in dens-after.png: the pair in blue and cream shoulder-to-shoulder and
adjacent, not nested; the seated man in yellow shifted out clear of
them; the standing pair in brown and white upright with their faces
clear. dens2-after.png is the same fix at the second cluster: a
nursing mother, a woman in brown, a seated man, a standing man and a
boy — five people — where dens2-before.png was a five-body tangle, and
the prone infant in the corner (excluded, lying) is untouched in both.

## Cost, measured honestly

Poll traffic (`/state` every few seconds) pollutes whole-batch timings,
so the protocol is single-render timing: warm up, then 90 individual
`render()` calls, report min and median per world. EDEN at 123 stills,
Y617:

| build | EDEN min / med | LAGOON min / med |
|---|---|---|
| 6b build (no pass), `:6992` | 0.3–0.4 / 0.4–0.5 ms | 0.9–1.0 / 1.1–1.3 ms |
| pass removed in scratch (A/B), `:6995` | 0.2–0.3 / 0.4 ms | 0.8–1.3 / 1.1–1.3 ms |
| this build, `:6994` | 1.2 / 1.5 ms | 1.0–1.2 / 1.4 ms |

The pass costs **≈ +0.8–1.0 ms per EDEN frame** at the frozen record's
density (123 people, 20 overlapping pairs, 3 sweeps) and **≈ +0.1–0.2 ms**
on LAGOON. The A/B build with the pass removed renders at the 6b
build's speed, so the delta is the pass, not noise. The cost scales with
local overlapping pairs (roughly quadratic in cluster size within a
cell neighbourhood), not with population; the re-bucket per sweep and
the inline 3×3 scan keep it allocation-light.

The frame-loop backoff (`costAvg > 26` → 15 fps) was already borderline
on this machine before the change (`costAvg` read 26–28 in a poll-free
window); the pass adds ≤ 1 ms to a per-frame render that is orders of
magnitude under the 66 ms backoff budget, and is not the limiter. No
measurement of the model is implied or was taken.

## MSH reading of the captures

Chrome cost: unchanged — no element added, moved or resized; the
masthead, instrument strip, gauges and record line are identical at
390/1024/1440 as before. Hierarchy: unchanged — worlds still largest,
first; the `?` veil untouched. At 390 the phone's stacked layout holds
and the sleeping rows read clean; at 1024 and 1440 both world panels
and the island view are unobstructed. The separation is entirely inside
the canvas — the canvas owns its pixels.

## Honest negatives

- **The live death phase is still unaudited.** Iteration 6 is still
  growing (Y641 · EXPLOIT · ALWAYS SPRING · THE CROWD AT THE HOPPER);
  the witness for this change is the frozen Y617 record, the only
  extremity of density on disk. Iteration 5's emptying was the witnessed
  one, and it no longer exists as a frameable state. Whether the pass
  reads well against a 1,000-body heap is unknown; the cost does scale
  with cluster size, and the 15 fps backoff would absorb it.
- **Lying bodies are not separated.** A_SLEEP/A_MATE figures and
  infants are excluded — repositioning a body on its mat would be a lie
  about where the record put it. A carpet of prone bodies at the hopper
  in the island rung (visible in msh-density-*-island-1440.png) is the
  mats' story, not this pass's; no claim is made that lying ink never
  overlaps.
- **Pairs reachable only past a one-tile neighbourhood are never
  touched.** The bucket window is ±1 tile and bodies more than two bins
  apart can never meet the overlap test anyway (half-widths sum to
  ≤ ~0.65 tiles at life size), so this is exact, not heuristic — except
  that no guarantee is offered for a future crowdScale change.
- **A_MOVING figures are not separated.** A walker cutting through a
  standing crowd may overlap it on the frame it passes; the fan never
  moved movers either, and hiding the collision would misreport motion.
- **20 → 0 is one record.** A different snapshot density moves both
  numbers; nothing here generalises beyond the frozen Y617 probe and the
  two before/after frame pairs.
- Live vs frozen: the live instrument read Y641 · POP 210 (LAGOON 16)
  throughout; the frozen record is Y617. The pages show whatever the
  record says on the day you read them.
- The display light turns four times per model year; a DAY label can
  sit under a dark phase and vice versa (STUDY.md). The clock label
  reports model time, not the phase.
- `config.js` 404s in the local mirrors (it exists only in the deploy
  tree); the pages proceed with `SNAP=null`. Pre-existing, benign, not
  this change. The scratch servers (`:6994`, `:6995`) and the read-only
  preview (`:6992`) are stopped.
- Engine untouched at `2026.11.12.6`; no world's trajectory moved;
  nothing here is a measurement of the model.

Batteries: `test_style` 77 OK (new pin
`test_cross_tile_crowds_are_separated_before_the_ysort` fails loudly on
a silent revert of the pass or of its placement before the y-sort),
`test_contract` 20 OK, `test_vr` 36 OK, mirror identical. `test_style`
recomputes the contrast table and passes; the palette is unchanged.
