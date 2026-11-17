# 2026-11-17/18 — the woods hide whoever stands behind them

One viewer-only drawing change in `web/index.html` (byte-identical in
`docs/index.html`), no engine change, no trajectory moved: GRAPHICS.md §6
item 6b, closing the last open occlusion item. Evidence captured
2026-11-17; the pass was finalised and documented 2026-11-18.

The tree crowns left the baked LAGOON ground layer and are painted
per-frame in `render()`'s people pass, merged into the people's own
back-to-front order, exactly as huts/lodgings (item 6) and bars/assets/
hearth (item 6a) were lifted before them. Person key first as before
(`a.y+a.nudgeY`):

| occluder | key |
|---|---|
| tree crown (LAGOON) | `tyd+0.35+tr*0.75` — the shadow's south edge |

Mechanics, for the record:

- The baked LAGOON painter no longer paints trees. It keeps the scrubs,
  the shore palms and the mangrove clumps (low, or thin at the water's
  edge) and nothing taller may hide a person. The collection in `render()`
  uses the baked painter's own predicate and position formula verbatim
  (`v===1 && hash2(x*3,y*5)>0.42 || v===0 && hash2(x*7,y*11)>0.985`; crown
  seed `hash2(txd,tyd)`), culled to the viewport with a 2-tile margin wider
  than the largest crown, and pushes `{y:tyd+0.35+tr*0.75, tree:[…]}` into
  the same `occl[]` the huts and assets ride. `tb=groundStep(ts)` is
  computed once in `render()` so the per-frame painter honours the same
  detail thresholds the baked pass used.
- The new standalone painter is `drawTree(g, x, y, r, seed, tb)`: a shadow
  thrown to the bottom right (only at `tb>=3`), a crown in shade, the lit
  side of the crown toward the light (only at `tb>=10`) — the same three
  strokes the baked layer used to make in one batch, honouring the same
  thresholds. It is reached only through the merge's `drawOccl` dispatch.
- EDEN has no trees (its terrain is a resort island's sand and cabanas);
  item 6b is LAGOON-only by construction.

## Cost, measured before the change (the reason 6b was scoped out once)

The baked ground is a cached offscreen canvas — the painter runs only on
cache miss — so visibility had to be measured before lifting trees, not
assumed:

| probe (in-page, live instrument, LAGOON) | value |
|---|---|
| whole-map tree count (baked predicate) | 613 crowns |
| whole-map paint, one pass of all crowns | 12.43 ms (upper bound, never reached at any named rung) |
| whole-map predicate collection alone | 0.35 ms |
| camp rung: crowns visible in viewport | 36 |
| camp rung: shadow+shade+lit paint per frame | 0.3 ms |
| LAGOON `render()` typical | 2.32 ms |
| EDEN `render()` death phase (202 bodies) | ~32 ms — the page had already backed off to 15 fps (`costAvg≈42`) before this change |
| frame loop backoff | unchanged (`costAvg>26` → 66 ms) |

Lifting every crown wholesale would have been ~12 ms a frame and was never
on the table; only the viewport's 36 (typical) cost anything. The change is
amortization-neutral for the bake and additive ≤0.3 ms per frame at the
camp rung. No measurement of the model is implied; none was taken.

## Evidence (captured from the real interface)

Live frames came from the updated `web/` tree served at `127.0.0.1:6991`
through the read-only proxy to the live instrument; frozen frames came from
the deployed snapshot served at `127.0.0.1:6992`; the witness A/B came from
a **scratch copy at `127.0.0.1:6993` that was never deployed**. The eight
MSH frames read `#hud6 .clock` **before and after** the shot and matched in
every case; the rung frames read it once at shoot time. The 1024 NIGHT
frame rolled the part on every first attempt (the part clock flips every
~2.5 s of real time) and was re-taken with a 60-attempt loop; only the
verified frame is kept.

| file | viewport | clock label in the frame |
|---|---|---|
| msh-6b-day-camp-390.png | 390 | Y640 · DAY · POP 207 |
| msh-6b-night-camp-390.png | 390 | Y640 · NIGHT · POP 207 |
| msh-6b-day-camp-1024.png | 1024 | Y640 · DAY · POP 207 |
| msh-6b-night-camp-1024.png | 1024 | Y640 · NIGHT · POP 207 (after retry) |
| msh-6b-day-camp-1440.png | 1440 | Y640 · DAY · POP 208 |
| msh-6b-night-camp-1440.png | 1440 | Y640 · NIGHT · POP 208 |
| msh-6b-day-island-1440.png | 1440, EDEN rung | Y640 · DAY · POP 208 |
| msh-6b-night-island-1440.png | 1440, EDEN rung | Y640 · NIGHT · POP 208 |
| occl-island-1440x900.png | 1440, EDEN rung | Y636 · NIGHT · POP 204 (at shoot) |
| occl-camp-1440x900.png | 1440, LAGOON rung | Y636 · DAY · POP 204 (at shoot) |
| occl-hearth-1440x900.png | 1440, LAGOON rung | Y636 · DUSK · POP 204 (at shoot) |
| occl-trees-frozen.png | 1440, node 144.7/90.0 th 2.4 | Y617 · DAY · POP 123 |
| occl-trees-front-frozen.png | th 2.0 | Y617 · DAY · POP 123 |
| occl-trees-front2-frozen.png | th 2.6, node 140.9/110.3 | Y617 · DAY · POP 123 |
| occl-trees-front3-frozen.png | th 2.6, node 143.9/90.9 | Y617 · DAY · POP 123 |
| occl-trees-wide-frozen.png | th 3.4 | Y617 · DAY · POP 123 |

### The witness: a controlled A/B, and an honest account of the record

The frozen snapshot (`Y617 · DAY · POP 123`; LAGOON's own head shows
POP 17) was probed for its natural witnesses first. The probe results,
recorded rather than staged:

- 17 still people, 613 trees, 224 huts.
- Behind-order hits (still person north of a crown's key, overlapping it in
  x): 592/597/591/595/589/579 — **all on the hut-crowded tile (144–145,
  89–92)**, where the drawn occluder is ambiguous between hut and crown.
  With a no-hut margin of 3.2 tiles enforced and a strict ±0.8-tile x
  window, the count of clean behind candidates is **zero**.
- Front-order candidates: 586/594 at (141,111) vs tree (140.34,109.29) —
  no pixel overlap at the aims tried (th 2.0/2.6); 591 at (144,92) — also
  on the hut-crowded tile.

The mechanism is the same code path as items 6 and 6a (one merge, one
key, one dispatch), and that path has witnesses. For the trees
specifically, the witness offered is a **controlled A/B inside a scratch
copy of the viewer** (`/tmp/u69w/abserve`, served at `127.0.0.1:6993`,
never deployed, server stopped after capture): one display-only line inside
`render()` shifts actor 591 (watch, act 20) onto a clean crown at
(20.3, 8.28), key 9.23 — no hut within 3.2 tiles in any direction, verified
by probe. Everything else is the deployed page and the frozen record:
same load, same manual camera (`tx 20.6, ty 8.85, th 2.4`), same part clock
read before and after each shot (`Y617 · DAY · POP 123` twice), only the
display y changed by 0.8 tiles:

| file | 591 display pos | key | what the frame shows |
|---|---|---|---|
| ab3-behind.png | (20.3, 8.55) | 8.55 < 9.23 | drawn before the crown: west half and head lost to the crown's body, legs and the east edge of the torso read out below and to the right. The part of 591 the crown covers is simply not on screen. |
| ab3-front.png | (20.3, 9.35) | 9.35 > 9.23 | drawn after the crown: the full figure stands over the crown's south lobe — head, chest and legs painted on the foliage, foliage never crossing the body. |

The record on disk is untouched (591's on-record position is (144,92));
the shift exists only in the scratch copy's display path, and the scratch
server is stopped. An earlier offset aim (ab2, x=20.6) put 591 at the
crown's right edge and is superseded by the centered pair; it shows the
same mechanism with less coverage. The frozen frames above show the merge
inside the hut-crowded camp — crowns interleave correctly with hut cones
(crown-over-cone where south, cone-over-crown where north) and with the
camp's assets — but they are not offered as the tree witness.

The four-legged figures visible in the near-view frames are the record's
own wildlife — herds of deer and the big cats drawn in `render()` from
`u.animals` (see `drawAnimal`), eased toward their modeled positions — not
decoration and not a new element.

## MSH reading of the captures

Chrome cost: unchanged — no element added, moved or resized; the masthead,
instrument strip, headings and record line are the same at 390/1024/1440
as before the change. Hierarchy: unchanged — worlds still largest, first;
the `?` veil untouched. Task visibility: the record, gauges and buttons
read identically at all three widths; at 390 the phone's stacked layout
holds — both panels stay legible and the low-crown row crops nothing that
a person needs. Crowns now correctly hide or yield to people at every
width; the NIGHT frames show the same interleaving under the grade (the
grade is painted after the people and the fire after the grade, by design).
The change is inside the canvas only — the canvas owns its pixels.

## Honest negatives

- **No clean natural witness exists in the frozen record.** The woods'
  still people cluster on the hut-crowded tile; the behind-order hits are
  attributable to hut or crown ambiguously; with a hut-free margin enforced
  the clean-candidate list is empty. The controlled A/B above is the
  witness; the absence is recorded, not staged.
- Live vs frozen: the live instrument read Y640 · DAY/NIGHT across the
  session (POP 207→208); the frozen record is Y617. The pages show whatever
  the record says on the day you read them.
- The display light turns four times per model year; a DAY label can sit
  under a dark phase and vice versa (STUDY.md). The clock label reports
  model time, not the phase. The part clock flips every ~2.5 s of real
  time; 1024 NIGHT had to be re-taken 60 times to catch a stable NIGHT.
- `config.js` 404s in the local mirrors (it exists only in the deploy
  tree); the pages proceed with `SNAP=null`. Pre-existing, benign, not
  this change. Both scratch servers and the deploy preview are stopped.
- Scrubs, palms and mangroves stay baked (low; a person behind one still
  reads over it). The camp perimeter wall ring stays baked (6a's reason).
- §6 item 1 remains open: cross-tile sprite overlap at extreme density;
  the live death phase is still unaudited.
- Engine untouched at `2026.11.12.6`; no world's trajectory moved; nothing
  here is a measurement of the model.

Batteries: `test_style` 76 OK (the new pin
`test_tree_crowns_occlude_in_the_people_order` fails loudly on a silent
revert of the merge or the painter), `test_contract` 20 OK, `test_vr` 36
OK, mirror identical. `test_style` recomputes the contrast table and
passes; the palette is unchanged.
