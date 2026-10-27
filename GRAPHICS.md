# GRAPHICS.md — how the universes look, and how they don't

The renderer is `web/index.html` (byte-identical to `docs/index.html`, which is
what GitHub Pages serves). This file is the working documentation of it: what
the drawing is made of, what it does well, what it still does badly, and what
changed and when.

**Update this file in the same commit as any change to the drawing.** A
renderer change without a line here is a renderer change nobody can review.

---

## 1. The house rules (from the owner's brief, 2026-10-27)

- Chunky pixels. `image-rendering: pixelated`, no smoothing, no gradients in
  the world layer, no shadows-as-decoration, no drop shadows, no skeuomorphism.
  The visual language is 8-bit honesty.
- Flat palettes, three tones per material, light from the north-west.
- Monospace HUD for the *worlds*; the annotation layer is set at device
  resolution so the type stays readable against chunky pixels.
- **People are the exception.** They are drawn as life-drawing ink sketches
  with realistic proportion — an adult is about 7.5 heads — so a viewer can
  see whether someone is fat, starving, strong, weak or hurt. Never stick
  figures, never blobs, never a circle with a dot. Adults are drawn as bodies
  are; children never get genital detail at any zoom.
- Two universes, always side by side. The comparison *is* the product.
- The camera is a documentary eye: it finds something worth watching, closes
  in on it, then pulls back. It is not a surveillance map and not a game
  camera.

---

## 2. How the picture is made

Five layers per universe, drawn in this order every frame.

| Layer | What it is | How often it is rebuilt |
|---|---|---|
| `base` | The terrain: water, shallows, foam, sand, grass, woods, canopy, the painted sky and beach in EDEN | Once per terrain (LAGOON), once per pen size (EDEN) |
| `semi` | The things the world changes: worn paths, farm fields, huts, walls, the snow of a hard winter | Once per poll |
| `frame` | The seasonal grade (snow, ice) | Once per poll |
| people | One sprite per person, blitted from the sprite cache | Every frame |
| `overlay` | Type, captions, the card of the person you are watching, drawn on a separate canvas at device resolution | Every frame |

The world canvas is `S × PX` pixels for an `S × S` tile map, `PX = 12`. The
camera crops a rectangle of that canvas and stretches it to the panel. Because
the panel is wider than it is tall, the crop is rectangular; the camera's
`h` is in world tiles and `hx` is derived from the panel's aspect.

### The sprite cache

`figureSprite(actor, act, bucket, moving, s, dress)` returns a canvas keyed by
everything the drawing reads: activity, body parameters, sex, dress, the
withdrawn kind, the animation bucket, whether the actor is walking, which way
they face, a variation index (only when zoomed in far enough for it to show),
and the zoom bucket. A cached figure is therefore never someone else's body.

The cache is capped (420 sprites at close zoom, 1400 far away) and cleared when
it overflows. Clear it too eagerly and the frame cost doubles; never clear it
and a long run leaks.

### The pose solver

`solvePose(act, phase, moving, view)` is the single source of truth for a
figure's joints. It returns joint offsets in a 32-unit figure space — the
shoulder line, the hip line, knees, ankles, elbows, wrists, the head tilt, and
flags for the tool, the basket, the carried load and whether the pose is
sitting or lying.

`drawSketch` turns those joints into ink. It is deliberately *not* a skeleton
with inverse kinematics: the solver states where the joints are, and the
drawing decides how the body looks.

### The camera

`pickShot` scores what is happening — a hunting party, a fishing party, a
foraging party, the crowd at a hopper, the beautiful ones apart — and moves
the camera to the best of it, then pulls back to the whole world. The viewer
can take the camera at any time: drag to pan, wheel to zoom, click a person to
follow, WASD to walk in at eye height.

---

## 3. The walk cycle

A walk is not a sine wave. The pose solver builds it from two phases:

- **Stance** (62% of the cycle): the foot is on the ground and the body passes
  over it. The knee is nearly straight and slightly ahead.
- **Swing**: the foot travels forward and lifts on an arc, the knee bends
  forward and then extends to plant.

The body rises over each planted leg and drops as the next one lands (two
bobs per cycle). The hips travel toward the leg that is carrying the weight;
the shoulders travel the other way, because the spine counter-rotates. The
arms swing against the leg on the same side.

This is the same set of ideas that motion-capture training sets encode — a
*contact* phase with a planted foot, a *swing* phase with a bent knee, and
weight transfer between the two — applied by hand to a 32-unit figure.

---

## 4. The figure

The drawing is ink over a flat wash of skin, the way a figure study is drawn.

- **Trunk.** Neck root at the top, trapezius sloping out to the shoulders,
  ribcage narrowing to the waist, iliac crest flaring to the pelvis, the
  crotch closing the shape. One soft pass down the far side gives it volume,
  because the light comes from the north-west.
- **Limbs.** Rooted *inside* the silhouette (the shoulder joint under the
  deltoid, the hip joint inside the pelvis) so the joints read as joints.
  Each limb is one tapering contour with the muscle bowed on the outer side,
  a joint cap, and a loose second pass over the main line.
- **Head.** A skull and a jaw, not an egg. Hair as strokes; the back of the
  head is a filled shape; the face is only drawn when the figure is close
  enough for a face to be legible.
- **Hands and feet.** A hand is a palm with a thumb and finger strokes; a foot
  is a wedge with a heel and a toe that meets the ground.
- **The body is the record.** Width follows BMI, muscle follows strength, ribs
  show in famine, a belly shows obesity or pregnancy, a bandage marks an
  injury, and a limp changes the leg.

### The pair

Couples retain the individual body sprites and activity poses. The unfinished
combined-pair renderer was removed during audit: it grouped unrelated people
by tile, reused another couple's appearance, shifted flipped images downward,
and discarded BMI, strength, injury and pregnancy differences. Individual
sprites preserve the body's record and the existing pose solver.

---

## 5. What does not work (yet)

This is the honest list. Each line is a defect, not a design.

1. **Crowds interpenetrate.** There is no depth sorting beyond `y`, and two
   people on the same tile are drawn over each other with no occlusion. In
   EDEN's death phase (1,600 people) the pen becomes a wall of overlapping
   figures. *Fixing this needs a per-tile sort and a decision about which
   figure wins the tile — not just a bigger sort buffer.*
2. **A crowded establishing shot cannot supply portraits.** It fits the
   population bounds at the current aspect; the documentary close shots and
   manual zoom provide individual detail. Very crowded populations still
   require further visual review on the instrument.
3. **EDEN's night is an overlay, not a redraw.** The painted sky and the lit
   windows are the same daytime image with a blue wash and a warm glow over
   it. A real night sky with stars, and windows that are actually lit, would
   be better.
4. **The wide shot is unreadable.** At the whole-world zoom a person is two
   pixels. That is deliberate (it is a map, not a portrait) but it means the
   wide shot carries no information beyond "where the crowd is".
5. **Firelight does not reach.** The fire's glow is a radial gradient on the
   world canvas; it does not brighten the *people* standing in it, so the
   figures at the fire are as dark as the figures in the woods.
6. **No occlusion from the world's own geometry.** Huts, trees and cabanas are
   in the baked layer, so a person always draws over a hut, even when they
   are standing behind it.
7. **Children are drawn as small adults.** Their proportions use the stage
   table, but the detail (ribs, navel, belly) is scaled, not redrawn.
8. **The animation budget is 12 buckets per activity.** At close zoom a
   two-handed gesture reads as a loop of twelve positions, not as motion.

---

## 6. Changelog

Every change to the drawing gets a line here, newest first.

- **2026-10-28 — audit and MSH repair.** Both worlds remain side by side at
  390, 1024 and 1440 px. World headings reserve space above the cameras and
  align the comparison; identity, time/population, then activity/conditions
  form a reading order. The record stays below the picture. Research has one
  reading scroll and separate Model tests / The books views, readable claims,
  explicit verdicts, keyboard containment, escaped snapshot text and a working
  CLOSE button. Adult-only anatomical detail is gated on a known age of at
  least 18, with that distinction included in the sprite key. Establishing
  shots fit population bounds; close shots follow
  their subjects instead of lingering on empty ground. Captions stay within
  their scene. The broken combined-pair draft was removed; individual body
  sprites, the cache, pose solver, particles and camera controls remain.
  Evidence and remaining limits: `docs/audits/2026-10-28/README.md`.

- **2026-10-28 — the figures were rebuilt.** The trunk was a slab; it is now a
  real torso (trapezius, ribcage, waist, ilium, crotch) with a neck, and a
  soft shadow pass for volume. Limbs now root inside the silhouette instead of
  sprouting from its edge. Hands have palms and thumbs, feet are wedges with
  heels, and the head has a jaw. Props were floating in mid-air: the forage
  basket now hangs from the hand that carries it.
- **2026-10-28 — the walk was a slide.** The feet moved on a sine wave, which
  skates. It is now a stance/swing cycle with a planted foot, a knee that
  bends and extends, a body that rises and falls, hips that travel over the
  standing leg, shoulders that counter-rotate, and arms that swing against
  the leg on the same side.
- **2026-10-28 — the shadow swallowed the figure.** It was scaled by the zoom
  level, so at close zoom it was several body-widths across and the ground
  under a crowd went black. It is now the size of the body that casts it.
- **2026-10-28 — combined-pair draft (withdrawn in audit).** The draft tried
  to render two actors as one picture. Its identity and pairing regressions
  prevented shipping; the individual activity sprites remain.
- **2026-10-27 — the record strip, the mirror banner and the intro card** came
  in from the other branch; the short-landscape CSS was fitted to the strip.
