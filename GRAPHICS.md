# GRAPHICS.md — how the universes look, and how they don't

The renderer is `web/index.html` (byte-identical to `docs/index.html`, which is
what GitHub Pages serves). This file is the working documentation of it: what
the drawing is made of, what it does well, what it still does badly, and what
changed and when.

**Update this file in the same commit as any change to the drawing.** A
renderer change without a line here is a renderer change nobody can review.

---

## 1. The house rules (owner's brief of 2026-10-28, superseding the 8-bit lock)

**Decision, 2026-10-28.** The owner retired the pixel-world lock: "it no
longer has to look like an 8-bit game". Resolution goes up everywhere so the
owner can walk through the worlds himself. What replaces it:

- **The worlds are painted at the screen's own resolution** (devicePixelRatio
  aware), naturalistic but restrained — a lit terrarium, not a game. No
  `image-rendering: pixelated`, no tile blow-up. Coasts, shallows and wood
  edges are smooth contours over the model's grid (marching squares on a
  smoothed field per material); canopies, huts, lodgings and bars are drawn
  as forms with a lit and a shaded side under one light from the top left.
  The ground for the current view is cached on an offscreen canvas per
  quarter-octave zoom step, so a 2016 MacBook repaints it only when the
  camera crosses a step or leaves the cached margin.
- **People keep the rig** (§2 "The anatomy rig"): realistic proportion
  checked against the canon, the body as the record, never stick figures or
  blobs; children never get genital detail at any zoom.
- **One palette: TERRARIUM.** Named for what the screen is — two lit worlds
  seen from a dark room. A warm near-black console (`--surface #14130f`,
  `--surface-2 #1c1a15`), paper ink (`--ink #ede6d6`), a muted and a dim
  grey-brown for secondary text, one accent — lamplight amber
  (`--accent #e4b456`) — meaning "live / chosen", and one quiet hue per
  world: sea-glass `--eden #8ec5d6`, moss `--lagoon #a6c98a`, plus
  `--warn #ec8f74` for a reading outside its band. The world tokens
  (`--w-deep`, `--w-shallow`, `--w-sand`, `--w-grass`, `--w-floor`,
  `--w-can`, `--w-night`, `--w-fire`, …) are muted earths so the people
  are the warmest, brightest thing on screen. The canvas reads its colours
  from these tokens (`PALETTE_TOKENS`), so there is one palette, not two.
  It is our own combination, not a borrowed named scheme.

  | Text token on | `--surface` | `--surface-2` |
  |---|---|---|
  | `--ink` | 14.95 | 13.98 |
  | `--muted` | 6.73 | 6.29 |
  | `--dim` | 4.93 | 4.61 |
  | `--accent` | 9.70 | 9.07 |
  | `--eden` | 9.83 | 9.20 |
  | `--lagoon` | 10.04 | 9.39 |
  | `--warn` | 7.74 | 7.24 |

  All clear WCAG AA (4.5:1); `tests/test_style.py` recomputes this table.
- **Type:** Jost for the console (a Futura-like geometric face; system
  fallbacks Futura / Avenir Next), Source Serif 4 for reading (the book,
  the research claims; fallbacks Iowan Old Style / Palatino / Georgia). Two
  families, no Inter / Poppins / Roboto, no emoji icons, no glassmorphism,
  no gradients as decoration (the fire's and EDEN's lamplight are light,
  not ornament).
- **One screen, no scroll.** At 1440×900, 1024×768 and 390×844 the page is
  exactly the viewport (`html, body { height:100dvh; overflow:hidden }`) —
  and that is not a licence to clip: everything long (the record, the
  research, help, the book) is read in **pages** with ‹ Prev / Next ›, ←/→ in
  a dialog, a swipe on a phone, and a page indicator. No scrollbars, no
  nested scroll areas. `paginate()` lays content out once, invisibly, and
  packs it into pages of the box's height, splitting a paragraph taller than
  a page at its sentences.
- **Reading order of the first screen**, checked in the screenshots:
  (1) the two worlds — side by side, stacked under ~700 px — largest and
  first; (2) the instrument strip directly under them; (3) the record;
  (4) the chrome (one masthead line, the world headings, the dialogs' buttons).
- Two universes, always visible together. The comparison *is* the product.
- The camera is a documentary eye: it finds something worth watching, closes
  in on it, then pulls back. The viewer may take it, or WALK in at a
  person's height.

---

## 2. How the picture is made

Five layers per universe, drawn in this order every frame.

| Layer | What it is | How often it is rebuilt |
|---|---|---|
| `base` | The terrain: water, shallows, foam, sand, grass, woods, canopy, the painted sky and beach in EDEN | Once per terrain (LAGOON), once per pen size (EDEN) |
| `semi` | The things the world changes: worn paths, farm fields, huts, walls, the snow of a hard winter | Once per poll |
| `frame` | The seasonal grade (snow, ice) | Once per poll |
| sites | The food places, if the summary carries `sites` ({x,y,k,f}): berries on a bush, fish shimmer, game tracks, a hopper's level | Every frame (absent: nothing) |
| people | One sprite per person, blitted from the sprite cache | Every frame |
| light | The hour and season grade, then the fire and EDEN's lamps (additive) — painted **after** the people, so a figure at night is as dark as its ground and firelight lands on the ones in its circle | Every frame |
| strip | The eight gauges (below the worlds, DOM + small canvases) | Once per poll, or on resize |
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

### The instrument strip

One strip under the two worlds, eight cells across (four at ≤1100 px; a 2×4
grid behind a one-line bar under 700 px). Each cell is a label, then EDEN's
current value and yearly record, then LAGOON's, on **one** scale, with a
dotted reference tick where the literature gives one:

| Gauge | Reads | Tick (source) | Coloured when |
|---|---|---|---|
| Population | log pop vs time in founding doublings; Universe 25 laid under it with its phases A–D | Calhoun 1973 curve | never |
| Births−deaths /100 adults | per year | 0 | below 0 |
| Infant survival | to age 1 | 4% (Calhoun 1962), 80% (Gurven & Kaplan 2007) | below 80% |
| Breeders · withdrawn | count · % of adults | none: the extinction clock | under 10 |
| Claimants / place | per nest box or hearth | 1.0 | above 1 |
| Sink | % at the busiest food point | 25% (even), 60% (Calhoun 1962) | 60% or more |
| Food in store | days; EDEN ∞ by premise | none | under 30 days |
| Violent deaths /100k | per year, log | 1 and 524 (Pinker 2011) | above 524 |

The population x-axis is *time divided by the founders' doubling time*
(Calhoun's mice: 55 days; ours: the census year the founders first doubled),
so a mouse curve and a human curve can share one axis. Values come from
`u.gauges` (live) and `u.census` (yearly, fields from
`snap.calhoun.census_fields`; old 4-field rows read as null). Clicking a cell
opens a one-line note with the sources, ending "Model readings, not findings
about people." Ink on the house palette; colour only for a reading outside
its band; no gradients.

### The camera ladder

Three rungs, named by how tall an adult stands on screen: **island** (6 CSS
px), **camp** (18) and **hearth** (48). `rungH(key, r)` turns a rung into the
camera's half-height for the panel's real size. The establishing shot is the
camp rung on the largest camp (`largestCamp`: the densest 3×3 block of 6-tile
cells), not the bounding box of everyone — that box put the sea between two
camps in the middle of the picture. Close shots and a clicked person go to the
hearth rung; when nothing remarkable is happening the close shot is where
most people are, not one person picked by the clock. EDEN's automatic eye is
kept inside the pen (the beach and lawn outside it are dressing). The first
shot, and any shot more than three view-heights from the last, is a cut
rather than a glide. Keys 1/2/3 jump to a rung; the wheel still zooms freely.

### The pose solver

`solvePose(act, phase, moving, view)` is the single source of truth for a
figure's joints. It returns joint offsets in a 32-unit figure space — the
shoulder line, the hip line, knees, ankles, elbows, wrists, the head tilt, and
flags for the tool, the basket, the carried load and whether the pose is
sitting or lying.

### The anatomy rig

`drawSketch` no longer draws the solver's joints directly. `buildRig` maps
them onto a skeleton with this body's own proportions — pelvis, spine, chest,
neck, head, clavicles, shoulders/elbows/wrists, hips/knees/ankles, each with
one parent (`RIG_PARENT`) — and `ik2` solves each arm and leg as two bones of
fixed length: the solver says where a hand or foot goes, the skeleton decides
how the limb gets there, and a planted foot stays planted.

Proportion by age (`AGE_BAND`, `HEADS`, `STATURE`, `LEG_FRAC`, `ARM_FRAC`),
from the anthropometric canon: 4 heads at birth, ~5 at two or three, ~6 at
six, ~7 at twelve, 7.5–8 adult; the hip joint climbs from 38% of stature to
just over half. Shoulders and hips are equal in both sexes until puberty;
then a man's shoulders are ~1.25× his hips and a woman's hips about her
shoulders' width; a woman stands ~7% shorter. Arm and leg thickness is a
fraction of stature and is a little lighter in women.

The standing adult is checked against the Loomis canon, computed from the
renderer's own tables in `tests/test_style.py`: crotch at half height, knee a
quarter of the way up, elbow at the waist, wrist at the crotch. **Standing is
a stance, not a crouch** (`P.rest`): the leg is exactly hip-to-ankle long so
a standing leg is straight, the pelvis is level but for a small contrapposto
(the hip rides up over the weight leg, the shoulders tilt the other way), the
spine upright with a slight S, the arms hanging beside the trunk — clear of
the hip by the carrying angle — with a soft elbow. Walking bends only the
swing knee; when a planted foot would be out of reach the pelvis comes down
instead of the foot leaving the ground.

The skin is painted around the bones under one light from the top left, in
two tones of the person's own skin. Each limb is two capsules joined at the
joint, swelling over the muscle belly and narrowing at the knee, elbow,
wrist and ankle; `paintForm` fills it in shadow and lays the lit body over
it toward the light. The trunk is **two masses**: a ribcage (an egg, widest
at the chest, under a level shoulder line at the clavicles) and a pelvis (a
wedge from the iliac crest to the crotch), each lit separately so the waist
between them stays in half-shadow; a woman's breast is part of the ribcage's
silhouette, not a shape stuck on. Interior lines are gone except where one
form overlaps another and where the body is the record (famine ribs, the
fold of a fat belly). Hands are small mittens along the forearm; a foot is
a wedge about a head long pointing the way the person faces. The head keeps
its skull and jaw, with its far side in shadow; the hair is a silhouette
that stops at a hairline (long hair falls behind the shoulders), never a
disc.

**Small figures are drawn for their size.** From ~10 to ~26 px tall
(`drawFar`) a figure is silhouette first: a head, shoulders wider than the
waist, arms set apart from the trunk, two legs with daylight between them,
a lit and a shaded side, a thin ink edge so pale skin reads on sand, and the
garment's colour at the hips. Under ~10 px (`drawTiny`) it is an upright
two-tone mark on whole pixels.

**Garments** follow the existing modesty share (`dressOf`): resort wear in
EDEN (trunks or a brief and top), a hide wrap with a belt in LAGOON, fur over
the trunk in a hard winter — over the body, following its masses, with a
shaded side. Children under twelve wear nothing and never get genital
detail.

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
- **The body is the record.** Width follows BMI, muscle follows strength
  (strong 7–9: bulging limbs, squared deltoids, pectorals; weak 0–2: thinner
  limbs and a stoop), famine (BMI < 15) takes the limbs to the bone so the
  joints stand out and the ribs and hollow cheeks show, the hunger flag
  stoops and hollows the face, a belly shows obesity or pregnancy, a bandage
  marks an injury and a limp changes the leg. Every one of these is in the
  sprite key.
- **Several people on one tile** are fanned out inside it on a sunflower
  spiral (display only) and drawn back to front, instead of reading as one
  figure.

### The pair

Couples retain the individual body sprites and activity poses. The unfinished
combined-pair renderer was removed during audit: it grouped unrelated people
by tile, reused another couple's appearance, shifted flipped images downward,
and discarded BMI, strength, injury and pregnancy differences. Individual
sprites preserve the body's record and the existing pose solver.

---

## 5. What happened on 28 October 2026, and the guard that came of it

Six commits came back from the other machine trying to "upgrade" the
graphics. They were re-palettied to a Ghibli watercolour, given large round
chibi heads, given anime faces, smoothed off the pixel grid, and the couple
was quietly deleted. The result was worse than what it replaced: the hair
was drawn as overlapping filled circles, so every figure had a black blob
where its head should be; the bodies were six heads tall instead of seven
and a half; and the sex the owner had asked for by name was gone.

**Why it went wrong.** The brief was written in prose — "chunky pixels",
"flat 16-colour palettes", "an adult is about 7.5 heads" — and prose is easy
to agree with and easy to ignore. Each commit was a *stylistic substitution*
rather than a fix for a defect: the defects were that crowds interpenetrate,
that the night is an overlay, and that firelight does not reach the people
standing in it. None of those were addressed.

**The guard.** `tests/test_style.py` now pins the measurable parts of the
brief, so the next attempt fails the suite instead of the eye:

- the palette, exactly as shipped, and every colour flat;
- `imageSmoothingEnabled` never true — the figures are pixels;
- the figure sprite is a 40×40 box, so a "higher resolution" re-skin has to
  be argued for in the test file;
- an adult is between 7.0 and 8.5 heads tall, computed from the renderer's
  own tables;
- the head has a jaw, and is not an ellipse again;
- the couple is drawn as one picture, and the walk has a planted foot.

Checked against the six commits that came back, that guard fails **six of
its nine tests**. That is the point: the failure now costs a minute, not a
whole session of looking at the wrong thing.

**What was kept** from that pass: the collarbones, which are real anatomy
and made the shoulder line read. Nothing else.

## 6. What does not work (yet)

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
3. **EDEN's night is still a grade, not a redraw.** The painted sky and the lit
   windows are the same daytime image with a blue wash and a warm glow over
   it. A real night sky with stars, and windows that are actually lit, would
   be better.
4. **The island rung is a map.** At 6 px a person is a body's mass; it is
   only reached on request (key 1, wheel). The auto camera uses camp and
   hearth.
5. *(fixed 2026-10-28: the grade is painted after the people and the fire
   after the grade, so firelight now reaches the figures in its circle.)*
6. **No occlusion from the world's own geometry.** Huts, trees and cabanas are
   in the baked layer, so a person always draws over a hut, even when they
   are standing behind it.
7. *(fixed 2026-10-28: children have their own proportions by age band.)*
   The pair (`drawMating`) is still drawn from its own hand-placed segments,
   not from the rig.
8. **The animation budget is 12 buckets per activity.** At close zoom a
   two-handed gesture reads as a loop of twelve positions, not as motion.

---

## 7. Changelog

Every change to the drawing gets a line here, newest first.

- **2026-10-28 — the timeline and the first run.** The Book reader has a
  one-row timeline under the page: years before 2026 on a log scale (so the
  Big Bang and the last century both have room), the chapters' eras as faint
  bands (the current one in amber), the book's 69 events as ticks, the date
  at the handle ("13.8 billion years ago", "11,000 BCE", "1945"). The handle
  follows the page being read; dragging it, clicking it, or ←/→ when it has
  focus goes to the chapter whose era holds that point (the narrowest era;
  the whole-story chapters are skipped). The help card (?) opens THE FIRST
  RUN — `archive/archive.json`, the record of the original two universes —
  in the same paged reader. Figures sit in a fixed box so page breaks are
  known before the pictures load; pages are measured once the reading faces
  are loaded, and a page that renders taller than it measured gives its last
  block to a new page rather than cutting it.

- **2026-10-28 — the worlds at work.** For the owner's "we need to SEE them
  survive": LAGOON's huts come from the record (`u.huts`, one per bonded
  pair) and are drawn in stages — a ring of poles leaning to a tied peak,
  thatch climbing it as the work goes on, a finished hut with a door; the
  single decorative camp hut is gone, the hearth stays. No shelter, no hut.
  (A hut site the record puts on a water tile is not drawn — the act fixture
  has two.) Encounters (`u.encounters`) are what the documentary eye looks
  for first and are drawn where they happened: a deer down, a cat springing,
  a cat driven off, a cat killed, the marks where someone was taken or
  mauled; anyone standing by a cat raises a spear and faces it. The 14-field
  people rows reach the body: a load on the back or a carcass across the
  shoulders (`carry`), and hunger ≥7/10 draws a person gaunt. A woman giving
  birth has the nearest woman kneel by her; a mother with an infant cradles
  it; the watch stands at the fire with a spear upright. The couple is now
  two rigged bodies lying together on a mat, turned to each other — nothing
  more explicit at any zoom. Spears, hoes, baskets, loads and infants are
  drawn at camp size too. EDEN is a resort island: a calm painted sea, a
  beach, a mown lawn with palms, the pool with loungers, the dome's glass
  edge round the pen, bars with stools, loungers by the boardwalks. The
  record box takes only the lines it has, and its controls sit in one row
  on a phone.

- **2026-10-28 — modernised: full resolution, TERRARIUM, one screen.** The
  8-bit lock is retired by the owner (§1). The tile builders (`buildBase9`,
  `buildSemi9`, `buildBase6` at 12 px a tile, blown up with
  `pixelated`) are replaced by painters that draw the ground at device
  resolution from the model's grid, cached per view and zoom step. One
  palette on `:root`; the canvas reads it. The record, the research (with a
  new first section, "From Universe 25 to here", from `book/origin.json`),
  the help and the new BOOK (`book/book.json`, table of contents, chapters,
  figures with credit and licence) are read in pages; the page never
  scrolls. Deer and big cats redrawn as animals with a gait, eased between
  the engine's positions. A stub book (marked STUB) stands in until the
  writer's arrives. The local server does not yet serve `/book/`; on GitHub
  Pages (`docs/book/`) it is served as a file.

- **2026-10-28 — people, not puppets.** The owner's verdict on the rig pass
  was that the people still looked wrong, and they did: the standing pose
  was a crouch (legs 1–3% longer than hip-to-ankle, so every IK knee bent),
  the trunk was one sack, the arms hung over the torso, hands had spikes,
  feet were half a head long, the crotch sat at 55% of height, a contour
  stroke ran through every form, and at camp size (18 px) a figure was a
  smudge. Fixed as described in §2 "The anatomy rig"; the canon landmarks,
  the rest pose, mitten hands and the small-size drawings are pinned in
  `tests/test_style.py`. Comparison: `compare-48px-detail.png` and the
  galleries at 48/18/6 px in the review folder.

- **2026-10-28 — the instrument strip.** The four-line per-world HUD is gone:
  each world's heading is one line (name, year, hour, population, phase or
  age, what the camera is on; click for the rest), and the numbers that were
  stacked under it are now eight shared gauges in one strip, both worlds on
  one scale with literature ticks (§2). The corner population sparklines are
  replaced by the population gauge. At 1440×900 the world headings went from
  102 px each to 25 px; the strip is 48 px.

- **2026-10-28 — the anatomy rig, the ladder, and the night after the
  people.** Figures are skeleton-driven (`buildRig`, `ik2`, `RIG_PARENT`) with
  proportions by age and sex from the anthropometric canon, and a painted
  three-tone skin around capsule limbs with muscle bellies; hair is a
  silhouette. Body build reads BMI, strength, injury, pregnancy and the
  hunger flag. Camera: island/camp/hearth rungs (6/18/48 CSS px), the
  establishing shot on the largest camp. The night grade and fire are painted
  after the people. Labels only for the chosen person and at most two births
  or fights. Identical record lines coalesce as ×N with a year range (and
  record text is escaped). Under 700 px the worlds stack and each HUD
  collapses to one line (tap the heading to open it). Optional `sites` are
  drawn if the summary carries them. Art system locked as pixel world +
  painted ink figures (§1); `tests/test_style.py` pins the rig, the age
  table, the sex widths, the stature difference and the sprite key.
  Follow-up the same day: EDEN's eye kept inside the pen and the fallback
  shot on the densest cluster (it had framed one sleeper on empty sand);
  far shots cut instead of gliding; fish drawn as fish; `farm` sites; the
  controls hint hidden under 1180 px where it wrapped the masthead;
  `tools/shoot.py` accepts the stacked layout under 700 px.

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
- **2026-10-28 — the pair is one picture, and only ever a real pair.** A
  couple is drawn as one scene — in profile, from the front, from behind —
  rather than as two people who happen to be on the same tile. The first
  version of that scene grouped anybody doing the same thing on the same
  tile, which put strangers in bed with each other, and it drew both bodies
  from one template, so a fat person and a thin one looked alike. It now
  couples only the two whose recorded partner is the other, and each body
  keeps its own width, its own strength and its own skin. The individual
  sprites, the cache, the pose solver, the particles and the camera are
  untouched.

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
- **2026-10-28 — the Ghibli/manga pass was reverted.** Chunky pixels, flat
  sixteen-colour palettes, 7.5-head adults, the pair drawn as one picture and
  the planted-foot walk are all back, and `tests/test_style.py` now fails any
  attempt to take them away again. The collarbones were kept.
