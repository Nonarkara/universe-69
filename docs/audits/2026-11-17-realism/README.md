# 2026-11-17 — EDEN lodgings get volume; the dome's sky gets its night

Two viewer-only drawing changes in `web/index.html` (byte-identical in
`docs/index.html`), no engine change, no trajectory moved:

1. **Lodgings read as buildings.** The resort's condos and capsule hotels
   were a flat 2×2 tile with a colour band. They are now volumes under the
   same top-left light the rest of the world uses: a CABANA roof plane with a
   sunlit top sliver and a fascia shadow, a front face in shade with a lit
   west edge and a deeper east jamb, and a contact shadow hugging the base.
   Windows, pods and doors sit on the front face; the night windows
   (`edenNight`) moved to the same coordinates, so what is lit at night is
   the face the day painter drew. Same footprint, same alcoves, same palette
   tokens — no new colours, no new chrome.
2. **The painted sky has a night.** GRAPHICS.md §6 item 3 — "a separate
   exterior night-sky artwork is still absent" — is closed for EDEN's dome:
   the horizon band the daylight painter paints with clouds becomes a star
   field and a small moon (pale disc, crater seas in half shade) at dusk and
   night, deterministic `hash2` positions, a few stars breathing on the slow
   tick. It lives on the dome's wall band, where the daylight mural lives,
   and nowhere else — no stars over the sand.

## Evidence (captured from the real interface)

Served the updated `web/` tree at `127.0.0.1:6991` through a read-only proxy
to the live instrument (`/state`, `/world`, `/events` forwarded to
`127.0.0.1:6969`; everything else from `web/`). The captures below are the
real page, real record, no test substitutes; each file's clock label
(`#hud6 .clock`) was read back after the shot and matches the frame's part.

| file | viewport | part shown |
|---|---|---|
| realism-night-390x844.png | 390 | NIGHT |
| realism-day-390x844.png | 390 | DAY |
| realism-night-1024x768.png | 1024 | NIGHT |
| realism-day-1024x768.png | 1024 | DAY |
| realism-night-1440x900.png | 1440 | NIGHT |
| realism-day-1440x900.png | 1440 | DAY |
| realism-island-night-1440x900.png | 1440, island rung (key 1) | NIGHT |
| realism-island-day-1440x900.png | 1440, island rung (key 1) | DAY |
| realism-band-night.png | 1440, clip of the dome's sky band | NIGHT |
| lodge-zoom.png | 1440, clip of the north-wall lodgings | NIGHT (display phase) |

MSH reading of the captures: chrome cost unchanged (no element added or
moved; the masthead, instrument strip, record and headings are pixel-identical
to the pre-change layout at each width); task visibility unchanged (the
record line, gauges and buttons read the same at 390/1024/1440); hierarchy
unchanged (worlds still largest, first); the change is inside the canvas only.
At 390 the phone's stacked layout holds; at 1024 the lit lodgings read on the
top row; at 1440 the roof plane / shaded face / lit edge read directly in
`lodge-zoom.png`, and `realism-band-night.png` shows the star band and moon
inside the dome's wall.

## Honest negatives

- **The display light cycles four times per model YEAR, not per day**
  (GRAPHICS.md §1; the clock label still reports the actual model part).
  `realism-day-1440x900.png` carries a DAY clock but a dark display phase —
  the lit windows in it are the night painter doing its designed work during
  an in-universe dark phase, not a bug. The island-day capture landed in a
  lit phase and shows the roof plane in daylight.
- The 1440 frames were captured at `deviceScaleFactor=1` (not 2) because the
  part clock flips every 2.5 real seconds and a dsf-2 shot straddled it; the
  390/1024 frames are dsf 2. Noted so nobody compares pixel counts.
- **Not fixed:** §6 item 1 (crowd interpenetration at extreme density) and
  item 6 (no occlusion from the world's own geometry) remain open. This
  change repaints the lodgings; it does not sort them against people.
- No figure was quoted from the new drawing; nothing here is a measurement
  of the model. The live record read Y628, EDEN 176 / LAGOON 27 at capture
  time; the pages show whatever the record says on the day you read them.

Batteries: `test_style` 75 OK, `test_contract` 20 OK, `test_vr` 36 OK,
mirror identical. The palette is unchanged; `test_style` recomputes the
contrast table and passes.
