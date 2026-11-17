# 2026-11-18 — the close shot can supply a portrait again

GRAPHICS.md §6 item 2, first clause, on the current build: *close shots
and manual zoom provide individual detail.* A crowded establishing shot
still cannot supply portraits — that clause stands, and so does the
"very crowded populations require further visual review on the
instrument" clause, which is instrument-bound and remains open (see
below). This audit closes only the close-shot / portrait legibility
question, on the **frozen** EDEN record, scratch copy, never deployed.

No product change was made for this review. Chrome untouched, zero DOM
delta — a single 1440×900 viewport was used on purpose; no MSH
re-shoot is owed for a change that does not exist.

## What was witnessed

Scratch assembly: `web/index.html` (the current build, with the
2026-11-18 crowd-cache fix) + the frozen snapshot (Y617 · DAY · POP 123)
served on `127.0.0.1:6999`, `fetchJSON` frozen so the record could not
re-prune between capture and click. Camera set to manual hearth-rung
(`th = 1.15`, adult ≈ 84 CSS px of body height) centered on the person
nearest the hopper crowd (id 17, at (50, 23), act seeking-a-partner,
age 16). Clock read before and after: `Y617 · DAY · POP 123`, zero
pageerrors.

- `close-before-click.png` — the hearth rung resolves individuals: body
  build (one wide, one thin, one seated), skin tones, garment colour,
  pose, face direction. Bodies are life-drawing ink, not blobs; the
  drawn-size sprite keys (ds ≥ 3 → 20 variation variants) hold up at
  this zoom — no smear, no stale shared sprite across differentiable
  people.
- `close-card-open.png` — clicking the person selects and follows them
  (id 17 is Obadiah: "seeking a partner · 16 years · generation 4 ·
  2.5 hunger · Nest box at 43,5 · heavy · purpose 57% · self-control
  45% · temper 56% · seems restless"). The selection ellipse and the
  floating name tag render; the card preserves a live portrait-sized
  area of the scene instead of painting a redundant portrait (by
  design — see `paintCard`), and the person stays legible next to it.

## Honest negatives

- **Frozen record only.** Y617 is a crowded-ish hopper scene, not a
  death-phase heap. The item's own remaining clause — *"Very crowded
  populations still require further visual review on the instrument"* —
  is untouched by this audit. The live run stands at Y643 ·
  `EXPLOIT` · POP 207 (read read-only from `/state` on 2026-11-18;
  LAGOON Y643 · `agriculture` · POP 17) — no very-crowded state exists
  on the instrument, and none was fabricated for this review. The
  synthetic-graft extremes remain labeled synthetic in the crowd-cache
  audit and are not re-quoted here.
- One click, one person, one world, one viewport. Nothing is claimed
  about LAGOON portraits, about the island rung, or about the VR
  viewers (`vr.html` keeps the skinned-body near-field for close work,
  gated to 24 headset / 40 desktop bodies — untouched here).
- The card is text; "portrait legibility" was judged on the live scene
  area the card preserves, which is the shipped design, not a defect
  worked around.
- Clock verified before and after; one HUD context (`DAY`), not the
  whole light cycle.

## Pointers

GRAPHICS.md §6 item 2 is annotated with this review. Engine untouched
at `2026.11.12.6`; no trajectory moved; docs-only record. Batteries
green before this change set (`test_style` 79 / `test_contract` 20 /
`test_vr` 36 — docs-only, viewer files unchanged).
