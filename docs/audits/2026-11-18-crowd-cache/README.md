# 2026-11-18 — the crowd cache stops wiping itself

Viewer-only sprite-cache fix in `web/index.html` (byte-identical in
`docs/index.html`), no engine change, no trajectory moved, nothing quoted
from the drawing. It answers the one open question the density audit
left behind: *"what happens at a 1,000-body heap?"* — the live death
phase's extremity of density, which does not exist yet as a record on
disk.

The witness is a **synthetic extremity**: bodies grafted onto the frozen
EDEN record (Y617 · DAY · POP 123) in a scratch copy, never deployed,
labeled synthetic throughout. It answers *"does the drawing pipeline
scale with local density"* honestly without pretending to be a measured
Universe 6 at 1,323 people.

## Why: the density audit's open question

`docs/audits/2026-11-18-density/` closed GRAPHICS.md §6 item 1 and noted,
honestly, that the witness there was one record — the frozen 123 — and
that cost scaled with local cluster size. What a *bigger-than-record*
pile would do was unknown. Measuring it (this machine: headless
Chromium, dpr=1, 1440×900, EDEN, frozen record, camera node (50, 23.5),
th 4.5, single `render()` calls, 30–90 samples each, min/median) exposed
a superlinear blowup far steeper than the fan or the separation pass
could explain — and the blowup had a cause.

Once the pass is blamed or acquitted, the painting dominates:

| build at 423 bodies | min / med (ms) |
|---|---|
| geometry only (nodraw scratch: update + fan + pass + y-sort, no painting) | 5.7 / 6.2 |
| same-tile fan removed, cross-tile pass kept (nofan) | 528.2 / 546.7 |
| cross-tile pass removed, fan kept (nopass) | 136.2 / 146.2 |
| full, pre-fix | 139.4 / 152.7 |

Removing the fan quadrupled the cost — not because the fan is free, but
because without it every body draws at full size with full key space.
That is the key-space clue.

## The defects found

1. **`figureSprite` keyed its cache on the nominal scale, never on the
   drawn size.** The cache key varied limb variation (`vk`) and walk
   bucket (`bk`) against `s`; the crowd actually drawn may be
   `s · crowdScale` (down to 0.4× under the fan). A 0.4× body in a
   67 px sprite got the same twenty variants and the same four-tile wall
   resolution as a close-up — a key space of ~20,000 against a
   "wipe-everything-when-over-cap" safety valve (caps 420/1400) that
   emptied the cache wholesale several times per frame. The comment
   above the gate even read *"crowds share sprites and stay cheap"* —
   the gate just never read `crowdScale`. Fix: `var ds = s*(a.crowdScale||1)`
   — `vk` reads at drawn size ≥ 3 / ≥ 2 / ≥ 1.5 (20 / 4 / 2 variants),
   `bk` rounds to quarter buckets below 2.5; caps raised to 2048/4096 as
   a true safety valve (labeled as such in the code).
2. **`fit()` wiped the whole `spriteCache` unconditionally** — and
   `fit()` runs on every HUD reflow via ResizeObserver, which is exactly
   what happens when POP text wraps as a crowd grows. Fix: sprites bake
   in canvas pixels, so they die only when canvas size changes —
   `spriteBakeKey` compares both canvases' `width×height` and wipes only
   on a real change. HUD reflows that don't resize canvases no longer
   rebuild the world's sprites mid-phase.

## Numbers (EDEN, frozen record, min / median of single renders)

| total bodies | pre-fix | drawn-size fix | both fixes (shipped) |
|---|---|---|---|
| 123 (0 synthetic, baseline) | 1.1–1.2 / 1.4 | — | **1.2 / 1.4** (unchanged) |
| 223 (100 synth) | 27.7 / 93.6 | — | **2.9 / 3.5** (≈ 27–30×) |
| 423 (300 synth) | 139.4 / 152.7 | 87.6 / 180.7 | **87.5 / 174.9** (bimodal, see below) |
| 723 (600 synth) | 1053.5 / 1132.0 | 255.7 / 275.8 | **267 / 280.7** (≈ 4×) |
| 1323 (1200 synth) | 2081.8 / 2137.0 | 420.2 / 457.5 | **406.2 / 470.4** (≈ 5×) |

Local breakdown of the fix's value: the drawn-size key gate is the whole
story for 223/723/1323; the `fit()` hardening does not move the headless
timing medians measurably on this machine (its win is removing
*per-reflow* re-bakes, which the single-task timing loop never sees).
Both are kept: either alone leaves a rebuild path live.

Cache counters after the fix, 723 bodies, 105 renders (separate evaluate
calls): sprites created ≈ 595 total (vs a cache that previously
**shrank** render-over-render — 299 → 232 → 226 → 152 — as it was wiped
and rebuilt). A mid-probe counter dip (239 → 57) turned out to be
**poll pruning**: the scratch page re-fetches the frozen snapshot every
~600 ms and `syncActors` deletes any actor absent from the record —
including every synthetic body. The timed loops ran inside one task
boundary, so poll traffic never touched them; separate-evaluate counter
probes did see it. Documented because it cost this session debugging
time and would cost the next one more.

Witness capture: `crowd-after-fix.png` — 1440×900, EDEN node (50, 23.5),
th 4.5, 423 bodies (123 record + 300 synthetic), zero pageerrors, clock
read `Y617 · DAY · POP 123` before and after the shot. The regulars
stand at full size; the synthetic spiral draws at 0.4× with shadows,
z-order, no smear and no sprite churn. The
`MIRROR UNREACHABLE · RETRYING` banner in that frame is the scratch
harness's `fetchJSON` freeze (polls reject on purpose so the injected
bodies survive), not a product defect.

## Cost, honestly

- **123 baseline: unchanged.** Nothing was touched that a 123-body frame
  exercises differently.
- **223/723/1323: ≈ 27–30× / 4× / 5× faster.** All still faster than
  pre-fix by an order of magnitude at every synthetic size.
- **423 remains bimodal** (min 87.5 / median 174.9). Unexplained after
  the cache fix. Likely one genuine canvas re-bake (HUD reflow →
  ResizeObserver → canvas-size change → one wholesale sprite rebuild)
  landing inside the 60-sample window, plus the plain fill-rate cost of
  a 423-body pile at this zoom. Not chased further; the 15 fps backoff
  absorbs it and no claim is made that 423 closes to baseline.
- At ≥ 723 in frame the `costAvg > 26 → 15 fps` backoff engages by
  design; these zooms frame a global heap no auto-camera rung produces
  (both worlds auto-frame the camp/hearth close).
- **LAGOON: untouched.** No claim made or implied about its cost; its
  numbers were not re-measured for this change (no code path it uses was
  modified — the gates are crowd-scale-dependent and LAGOON's frozen
  population is 17).
- Painting at 723+ is fill-rate floor, not cache churn: at 423 bodies
  the fan already pulled everyone to 0.4× and the shared small sprites
  hold; the rest is per-pixel cost of ~700 overlapping warm bodies and
  the shadow pass. That is what §6 item 4 means by design stance, and it
  is why the auto camera never zooms out that far.

## Honest negatives

- **The live death phase is still unaudited.** The extremity here is a
  synthetic graft on the frozen record; no live 1,000-body state has
  been witnessed. The density audit's "live death phase remains
  unaudited" clause stands.
- Synthetic bodies all share `act: A_PLAY` and one bucket; pose diversity
  of a real death phase is undercounted.
- One record, one machine, headless Chromium dpr=1. The caps live in
  canvas pixels, not body counts, by design — other machines and DPIs
  will re-bake at different zooms.
- **A canvas-size change still re-bakes every sprite** — correct
  behaviour (sprites bake at canvas pixels); only the *unconditional*
  wipe is gone. If HUD reflow ever produces a canvas-size change, the
  crowd pays one re-bake. Bounded, honest, and the pin asserts exactly
  this contract.
- No visual change is claimed beyond "no regression": the painters are
  byte-identical; only key quantization changed. Crowds already drawn
  correctly stay pixel-correct; crowds drawn *stale* are fixed.
- Chrome is untouched: no element added, moved or resized — zero DOM
  delta, so no MSH re-shoot was taken for this change. Captures at
  1440×900 show the chrome identical to the density audit's frame set;
  zero pageerrors in every stress run.
- The drawing change carries no measurement of the model; the engine is
  untouched at `2026.11.12.6`; no world's trajectory moved.

## Batteries

`test_style` **79 OK** — two new pins:
`test_crowd_members_share_one_sprite_per_visible_difference` (drawn-size
key gate) and `test_fit_wipes_the_sprite_cache_only_when_the_canvas_size_changes`
(the `spriteBakeKey` contract; the pin matches the shipped declaration
`var spriteCache={}, spriteCount=0, spriteBakeKey="";`). Pinning rules:
a silent revert of either fix fails loudly.
`test_contract` 20 OK, `test_vr` 36 OK, mirror byte-identical
(`web/index.html` ≡ `docs/index.html`). The scratch mirrors (`:6996`,
`:6997`) and every injected build remained scratch; nothing synthetic
was deployed.
