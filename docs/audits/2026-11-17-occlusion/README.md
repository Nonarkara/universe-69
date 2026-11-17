# 2026-11-17 — the world's own geometry hides whoever stands behind it

One viewer-only drawing change in `web/index.html` (byte-identical in
`docs/index.html`), no engine change, no trajectory moved: GRAPHICS.md §6
item 6, partially closed.

Huts (LAGOON) and lodgings (EDEN) were painted in the baked ground layer,
under the people — so a person always drew over them, even standing behind
them. They are now lifted out of the baked layer into `render()`'s
per-frame pass and merged into the people's own back-to-front order
(painter's algorithm, y-keyed beside the people: hut key `h[1]+1.05`,
lodging key `Y+2`, person key `a.y+a.nudgeY`). A person behind a roofline
is lost to it; a person in front still stands over it. The same culling the
baked painter used is kept: off-view structures are skipped, and a hut site
the record puts on water is still not drawn.

Scope, honestly: **trees, the buffet bars and the camp assets are not
occluders yet** — they stay baked; a person under a tree crown still reads
over it. §6 item 1 (crowd interpenetration at extreme density) is untouched;
this is depth ordering between people and buildings, not co-location.

## Evidence (captured from the real interface)

Live frames came from the updated `web/` tree served at `127.0.0.1:6991`
through a read-only proxy to the live instrument (`/state`, `/world`,
`/events`, `/chronicle` forwarded to `127.0.0.1:6969`; everything else from
`web/`). Witness frames came from the deployed frozen snapshot
(`/Users/admin/repos/Nonarkara/vr.nonarkara.org`, served at
`127.0.0.1:6992`), because the live record moves faster than a camera can
be aimed: actor 599 walked from (133,97) to (146,107) between setting the
camera and the shot. The snapshot's positions are static, so its frames are
verifiable. Every file's clock label (`#hud6 .clock`) was read back; for the
final six, it was read before **and** after the shot and matched.

| file | viewport | clock label in the frame |
|---|---|---|
| msh-occl-day-390x844.png | 390 | Y630 · DAY · POP 183 |
| msh-occl-night-390x844.png | 390 | Y630 · NIGHT · POP 183 |
| msh-occl-day-1024x768.png | 1024 | Y630 · DAY · POP 183 |
| msh-occl-night-1024x768.png | 1024 | Y630 · NIGHT · POP 183 |
| msh-occl-day-1440x900.png | 1440 | Y630 · DAY · POP 183 |
| msh-occl-night-1440x900.png | 1440 | Y630 · NIGHT · POP 183 |
| msh-occl-dusk-1440x900.png | 1440 | Y630 · DUSK (kept under its visible label) |
| msh-occl-dawn-1440x900.png | 1440 | Y630 · DAWN (kept under its visible label) |
| occl-island-1440x900.png | 1440, island rung | Y629 · NIGHT · POP 177 |
| occl-camp-1440x900.png | 1440, camp rung | Y629 · DAY · POP 177 |
| occl-hearth-1440x900.png | 1440, hearth rung | Y629 · DUSK · POP 177 |
| occl-witness-frozen.png | 1440, frozen Y617 | Y617 · DAY · POP 123 |
| occl-behind-frozen.png | 1440, frozen Y617 | Y617 · DAY · POP 123 |
| occl-eden-facade.png | 1440, frozen Y617 | Y617 · DAY · POP 123 |

The two `dusk`/`dawn` 1440 frames were first captured under DAY/NIGHT
evaluate-readings but rolled the part clock between the read and the shot
(the part clock flips every ~2.5 real seconds). They are kept and named for
the label actually visible in the pixels, not for what was intended.

### The witness (frozen snapshot, LAGOON hut at tile 144,89)

Sort keys read straight from the page, hut key = 90.05:

| actor | feet key | order vs hut | in the frame? |
|---|---|---|---|
| 592 (drink), 600 (play), 597 (play) | 89.0–89.1 | before the hut | 592, 597 on the hut tile: **absent** — lost to the cone; 600 at x=146 stands clear east of it and is visible |
| 599 (play) | 90.0 | before the hut | **absent** — its whole sprite sits inside the cone's column |
| 561, 585, 593 (mate) | 90.0 | before the hut | visible — east of the cone, no pixel overlap |
| 595 (work), 579 (work), 589 (work) | 90.81–91.1 | after the hut | visible, painted **over** the hut's base — see `occl-witness-frozen.png` |

`occl-behind-frozen.png` is the behind-ordering frame (the cone paints over
the on-tile people; the frame is clean where they would stand).
`occl-witness-frozen.png` is the in-front ordering (the same hut's base
does not cover the people south of it). `occl-eden-facade.png` is the EDEN
side: actors 42/47 (keys 44/45) draw before the lodging at alcove (19,44)
(key 46), but they stand at x=21 against a facade edge at 21.06 — a
sub-pixel clip, so they read as standing clear of the block. No still
on-tile person existed in that frozen frame; said plainly rather than
staged.

## MSH reading of the captures

Chrome cost: unchanged — no element added, moved or resized; the masthead,
instrument strip, headings and record line are the same at 390/1024/1440 as
before the change. Hierarchy: unchanged — worlds still largest, first; the
`?` veil and its foot buttons untouched. Task visibility: the record, gauges
and buttons read identically at all three widths; at 390 the phone's
stacked layout holds and both panels stay legible. The change is inside the
canvas only — the canvas owns its pixels.

## Honest negatives

- Trees, buffet bars, camp assets (granary, pen, records bench) and the
  hearth stone ring are not occluders yet; a person under a crown or behind
  a bar still reads over it.
- §6 item 1 remains open: people who are not on the same tile but whose
  sprites overlap at extreme density still interpenetrate; this change only
  orders people against buildings.
- The EDEN witness shows ordering, not a legible clip (sub-pixel, above).
- The live record read Y629–Y630, EDEN 177–183 / LAGOON 16–23 at capture
  time; the frozen witness is Y617 · DAY · POP 123. The pages show whatever
  the record says on the day you read them.
- `config.js` 404s in the local mirror (it exists only in the deploy tree);
  the page proceeds with `SNAP=null`. Pre-existing, benign, not this
  change.
- No figure here is a measurement of the model. Nothing about the engine,
  the census or the event log changed; engine untouched at `2026.11.12.6`.

Batteries: `test_style` 75 OK, `test_contract` 20 OK, `test_vr` 36 OK,
mirror identical. The palette is unchanged; `test_style` recomputes the
contrast table and passes.
