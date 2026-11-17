# 2026-11-17 — buffet bars, camp assets and the hearth ring join the order

One viewer-only drawing change in `web/index.html` (byte-identical in
`docs/index.html`), no engine change, no trajectory moved: GRAPHICS.md §6
item 6a, closed for three more families of the world's own geometry; scope
narrowed honestly below.

The EDEN buffet bars, the LAGOON camp assets (granary, pen, records bench)
and the hearth stone ring left the baked ground layer and are painted in
`render()`'s per-frame pass, merged into the people's own back-to-front
order, exactly as huts and lodgings were one pass earlier (item 6). Sort
keys, person key first as before (`a.y+a.nudgeY`):

| occluder | key |
|---|---|
| buffet bar (EDEN) | `Y+2` (its counter footprint) |
| granary (LAGOON) | `s.y+1.85` |
| pen (LAGOON) | `s.y+4.0` |
| records bench (LAGOON) | `s.y-1.3` |
| hearth stone ring (LAGOON) | `s.y+2.41` |

The split `drawCampAssets(g, camp, state, tb)` was replaced by four
standalone painters (`drawGranary`, `drawPen`, `drawBench`, `drawHearthRing`),
and the buffet-bar block became `drawBuffetBar`; all five are reached only
through the merge now. The baked LAGOON painter no longer draws the assets,
no longer draws the hearth ring, and keeps only the perimeter wall ring
(below); the baked EDEN painter no longer draws the bars. The same culling
the baked layers used is kept; the bar cull also allows its 0.2-tile stool
halo east and the 2.5-tile south extent of its seats.

Scope, honestly:

- **The camp perimeter wall ring stays baked.** It draws as a rectangle
  outline whose north and south faces want opposite sort orders; any single
  key would wrongly paint it over the people inside the camp. A person
  behind it still reads over it. Documented here, not quietly fixed.
- **Trees stay baked,** now tracked as GRAPHICS.md §6 item 6b (their crowns
  are batched into one single-pass paint; lifting them per-frame is a real
  cost decision, not a free one).
- **§6 item 1's stale clause was reworded, not mechanised:** people who are
  not on the same tile but whose sprites overlap at extreme local density
  still interpenetrate; cross-tile depth order between people already
  existed (the people pass is y-sorted by feet). No engine change; the
  unaudited live death phase remains unverified.

## Evidence (captured from the real interface)

Live frames came from the updated `web/` tree served at `127.0.0.1:6991`
through a read-only proxy to the live instrument (`/state`, `/world`,
`/events`, `/chronicle` forwarded to `127.0.0.1:6969`; everything else from
`web/`). Witness probe came from the deployed frozen snapshot served at
`127.0.0.1:6992` — the live record moves faster than a camera can be aimed,
and the frozen frame is static, so any witness in it would be verifiable.
For the eight MSH frames the clock label (`#hud6 .clock`, the EDEN worldhead
line) was read **before and after** the shot and matched in every case;
the three rung frames (`occl-*`) had the clock read at shoot time only.

| file | viewport | clock label in the frame |
|---|---|---|
| msh-6a-day-camp-390.png | 390 | Y635 · DAY · POP 203 |
| msh-6a-night-camp-390.png | 390 | Y635 · NIGHT · POP 203 |
| msh-6a-day-camp-1024.png | 1024 | Y635 · DAY · POP 203 |
| msh-6a-night-camp-1024.png | 1024 | Y635 · NIGHT · POP 202 |
| msh-6a-day-camp-1440.png | 1440 | Y635 · DAY · POP 202 |
| msh-6a-night-camp-1440.png | 1440 | Y635 · NIGHT · POP 202 |
| msh-6a-day-island-1440.png | 1440, EDEN rung | Y635 · DAY · POP 202 |
| msh-6a-night-island-1440.png | 1440, EDEN rung | Y635 · NIGHT · POP 202 |
| occl-island-1440x900.png | 1440, EDEN rung | Y635 · DAY · POP 202 (at shoot) |
| occl-camp-1440x900.png | 1440, LAGOON rung | Y635 · NIGHT · POP 202 (at shoot) |
| occl-hearth-1440x900.png | 1440, LAGOON rung | Y635 · DAWN · POP 202 (at shoot) |

An earlier attempt at the MSH set read the clock only before the shot; its
390-pixel "DAY" and "NIGHT" frames rolled the part in the read→paint gap and
visibly show DUSK and DAWN. Those files were discarded, the set was
re-captured with before+after verification, and only the verified frames are
in this audit.

### The witness: an honest negative, not a staged one

The frozen snapshot (`Y617 · DAY · POP 123`) was probed for any still person
standing behind a drawn occluder. None exists:

- Both camps record zero granary/pen/bench progress, so **no granary, pen or
  bench is painted at all** in the frozen frame; camp Meera (137,109) reads
  `fire:false` with `work.fire 0.962` (the hearth is not drawn — it is shown
  only where the record shows fire), camp Parvati (145,91) reads
  `fire:true` and is the only site with a drawn new occluder (the hearth
  ring), with no still person behind it.
- No still EDEN actor stood in a bar's behind-column (`hits: []`).
- The sort keys above were read from the page for that probe; the key table
  is recorded rather than a frame that does not exist.

The mechanism is the same code path as item 6 (huts/lodgings), whose
witness exists (`docs/audits/2026-11-17-occlusion/`). The bars and assets
join without a pixel-level witness of their own; said plainly rather than
staged. A future pass should take the witness when the record shows e.g.
a granary under construction with someone standing behind it.

## MSH reading of the captures

Chrome cost: unchanged — no element added, moved or resized; the masthead,
instrument strip, headings and record line are the same at 390/1024/1440 as
before the change. Hierarchy: unchanged — worlds still largest, first; the
`?` veil and its foot buttons untouched. Task visibility: the record, gauges
and buttons read identically at all three widths; at 390 the phone's stacked
layout holds — EDEN's panel (bars in the corner plaza, people among the
lodgings) and LAGOON's panel (huts, granaries-to-be, the fire) both stay
legible. The change is inside the canvas only — the canvas owns its pixels.

## Honest negatives

- Trees remain baked (new item 6b); the camp perimeter wall remains baked
  (reason above); a person behind the north wall still reads over it.
- §6 item 1 remains open: cross-tile sprite overlap at extreme density;
  the live death phase is still unaudited.
- No positive witness exists in the frozen record for the new occluders
  (above). Mechanism identity and before/after-verified frames are the
  evidence offered.
- The frozen record is Y617; the live instrument read Y635 · DAY/NIGHT, EDEN
  202→203 / LAGOON 16–17 across the session. The pages show whatever the
  record says on the day you read them.
- The display light turns four times per model year; a DAY label can sit
  under a dark phase and vice versa, by design (STUDY.md; the part clock
  outpaces the light). The clock label reports model time, not the phase.
- `config.js` 404s in the local mirror (it exists only in the deploy tree);
  the page proceeds with `SNAP=null`. Pre-existing, benign, not this change.
- No figure here is a measurement of the model. Nothing about the engine,
  the census or the event log changed; engine untouched at `2026.11.12.6`;
  no world's trajectory moved.

Batteries: `test_style` 75 OK, `test_contract` 20 OK, `test_vr` 36 OK,
mirror identical. `test_style::TestTheWorldsAtWork::test_eden_is_a_resort_island`
now pins the EDEN painter's "buffet bars are painted per-frame" note and
`drawBuffetBar`'s "stools along the counter" so a silent revert fails loudly.
The palette is unchanged; `test_style` recomputes the contrast table and
passes.
