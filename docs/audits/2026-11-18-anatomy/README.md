# 2026-11-18 — far-tier eye, lower detail gates

Owner direction 2026-11-18: "I want people to have more precise anatomy of
people too."

The honest reading, grounded in the rig rather than taste: every figure is
already a life-study drawing (§4), faces exist but are zoom-gated, and below
the `s>=3.5` detail rung the eye was painted as a **pale sclera ellipse with a
sub-pixel dark dot** — at the hearth rung (`s≈2.6`, an adult is ~84 CSS px
and the eye is ~1.1 px) that reads as nothing, or worse, as a smear. This
change makes the far tier legible as **bold ink**, which is what a figure
study does at distance. No new landmarks were invented; no range gained a
face it could not carry.

## What changed (viewer-only, `web/index.html` ≡ `docs/index.html` ≡ deploy `2d.html`)

1. **Far-tier eye (2.2 ≤ s < 3.5).** In `drawEyeProfile` and `drawEyeFront`,
   the non-`detail` branch (previously: pale `#f4f0e4` sclera, dot of
   `max(0.12, hh*0.6)` px) now paints a **bold dark almond**
   (`max(ew*1.15, hr*0.115)` × `max(hh*1.1, hr*0.075)`, fill = INK),
   keeping the lid≤0.02 closed-lash branch and the s≥3.5 detail branch
   (sclera/iris/pupil/catch-light) **untouched**.
2. **Fingers** gate `s>=4` → `s>=3.0`.
3. **Toe separation hint** gate `s>=4` → `s>=3.2`.

The `test_style` pin ("the eye is layered, not a dot": `drawEyeProfile`
must contain `iris` and `pupil`) holds because the layered tier is
untouched and still present in the function body.

## What did not change

- Engine (`2026.11.12.6`) and every trajectory.
- The `s>=3.5` detailed eye (sclera/iris/pupil/catch-light/lower lash),
  brows, nose, mouth, ears, stubble, age lines, facial highlights, cheek
  tension.
- Children-never-genital-detail, adult-only external anatomy gate, couple-one-
  picture, planted-foot walk, heads-tall pins.
- Faces do not exist below `s=2.2` — by design, and this change does not
  create them there.
- Chrome: **zero DOM delta** — canvas paint only; MSH chrome cost is
  unchanged from before (no before/after measurement performed or claimed).

## Evidence

- `face-big-before.png` / `face-big-after.png` — the same synthetic fixture
  bodies (age 30, bmi 22, strength 7, profile and front, `s = 2.6 / 3.5 /
  5.0`), actual `drawSketch()` on the live instrument's renderer, head crop
  magnified 8× nearest-neighbour. Synthetic fixtures, **not** simulation
  records. Pixel diff between the two renders: 1,920 of 2,880,000 channel
  values differ; max delta 86; the change is confined to the eye region and
  is ~1–2 px at true scale — the honest magnitude of this fix.
- Fast gate: `python3 -m unittest tests.test_style tests.test_contract
  tests.test_vr` — **135 tests, OK** after `docs/index.html` was re-synced
  (the two mirror failures before the sync were the expected contract).
- MSH three viewports (read-only against the live instrument): 390×844
  **12/12**, 1024×768 **11/11**, 1440×900 **11/11**, zero browser errors,
  engine `2026.11.12.6`.
- `tools/shoot.py --diagnostic-only` re-rendered coherently (all fixtures
  coherent, no pageerrors).
- Live instrument after the change: EDEN Y656 · POP 238 (the world, not the
  drawing, moved).

## Honest limits

- At `s=2.6` an eye is ~1 px. This change makes that pixel **ink** instead
  of pale — it does not and cannot make the face "detailed" there. Real
  precision (iris, catch-light) remains a close-rung property (`s>=3.5`,
  and subtle nostrils/ears/stubble at `s>=4`).
- The island rung (`s≈0.19`) is a map by design (§6 item 4); nobody gains
  anatomy there.
- No claim is made about very crowded populations' legibility (§6 item 2
  remains open; the live instrument is in EXPLOIT, POP 238, and no
  death-phase heap exists; the armed watcher holds the capture).
