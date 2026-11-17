# 2026-11-18 — VR frame-time honesty (`?perf=1`)

Viewer-only addition to `web/vr.html` (byte-identical in
`docs/vr.html`; the deploy mirrors vr.html), no engine change, no
trajectory moved, nothing quoted from the drawing. It answers a line
GRAPHICS.md has carried since the VR build shipped: *"MacBook/Quest
frame rate must be measured on those devices before any performance
claim."* — by giving anyone with either device the instrument to take
that measurement in thirty seconds, and by keeping the page byte-cheap
when nobody asks for it.

## What was added

- **Opt-in `?perf=1` readout.** `PERF` is parsed from the query string
  (`URLSearchParams`), defaults to off. When off, the badge element is
  **never created** and `frame()` pays one boolean check per frame
  (`perfSample()` early-returns). `vr-noperf.png` shows the page exactly
  as before; no DOM node, no listener, no allocation exists until the
  flag is on.
- **Rolling median of up to 60 frame deltas** (Float32Array ring,
  ~15 Hz badge refresh) plus this frame's `renderer.info.render`
  draw calls and triangle count — the three numbers that say whether a
  scene is CPU-bound on submission or GPU-bound on fill.
- Badge: fixed-position mono pill, bottom-right above the keys hint
  (`bottom:84px`; `10px` ≤ 700 px where the keys hint hides),
  `pointer-events:none`, lagoon-green on translucent surface, ~11 px.
  Zero layout impact on the chrome; the canvas owns its pixels.

## Evidence (headless Chromium, SwiftShader — read the limits)

Captures from the deploy-assembled scratch mirror (never deployed
scratch, on `127.0.0.1:6999`):

| file | flags | reading |
|---|---|---|
| vr-perf.png | `?perf=1`, TABLE view, Y617 · POP 123/17 | `~3,494 ms · 138 draws · 1605591 tris` |
| vr-noperf.png | none | badge absent; page pixel-identical to before |

Zero pageerrors in both runs. The EDEN and LAGOON world cards, the
readout (`EDEN · Y617 · 123 people · day` / `LAGOON · Y617 · 17 people ·
day`) and the table itself render correctly — the frame is the shipped
product working.

The millisecond number is **not a hardware measurement**. Headless
Chromium rasterizes through SwiftShader — 1.6M triangles a frame on the
CPU; frame times were seconds and the 60-frame ring was still polluted
by the first frames' shader compilation (the probe read 589 ms earlier
in the same session, the capture's badge reads 3494.7 ms; SwiftShader is
simply that noisy). It is honest here as *draw calls (138)* and
*triangles (1,605,591)* for the TABLE view — those are scene-graph
counts, machine-independent to within instancing. The frame-time half
of the badge exists for real hardware and for the Quest.

## What this does not establish

- **Quest frame rate is still unverified on real hardware.** This
  change is the instrument, not the measurement. Thirty seconds of
  `?perf=1` on the headset closes it; the number either passes 72 Hz
  with margin or it does not, and either answer is publishable.
- No thermal/sustained-load behavior, no foveation interaction, no
  `renderer.info.memory` (geometries/textures live) — deliberately left
  out; the badge is for smoke checks, not profiling.
- The median is windowed at 60 frames; after a shader-compile hitch the
  reported median settles only after a minute at the table.
- LAGOON vs EDEN vs INSIDE/table views each have their own draw/tri
  profile; only the TABLE view was measured in this capture. Anyone
  with the headset should capture EDEN-inside too.

## Batteries

`test_vr` 36 OK (mirror identical; \?perf does not touch any pinned
behavior — offline, assets local, no new network reads), `test_style`
79 OK, `test_contract` 20 OK, `test_font_delivery` 3 OK. Mirror
`web/vr.html` ≡ `docs/vr.html` byte-identical; the deploy's vr.html was
synced in the same commit family. No DOM added on the default path, so
no MSH re-shoot was taken; the chrome in both captures is byte-identical
to the pre-change build.
