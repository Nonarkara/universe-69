# Japanese Manga Detail Plan for Universe 69 Figures

## Goal

Bring the figure rendering to the level of detail found in Japanese seinen manga
(Vagabond, Berserk, Gantz, Blade of the Immortal). The current renderer is
skeleton-driven with realistic proportions but flat, undifferentiated surfaces.
Manga achieves its look through **line quality, layered shading, and expressive
faces** — not through photorealism.

The owner's decision (2026-10-28) is full resolution, one palette (TERRARIUM),
no pixelated rendering. Figures are the exception: life-drawing ink sketches
with realistic proportion. This plan keeps that spirit but pushes the detail
to manga grade.

---

## 1. What manga does differently (the reference)

### Line art (ink)
- **Variable line weight**: thick outer silhouettes (2-3px), medium for
  major interior lines (1-1.5px), thin for detail (0.5-0.8px).
- **Tapered strokes**: lines start thick and taper to a point at tips
  (hair ends, limb extremities, fabric edges).
- **Broken lines**: not every contour is continuous; gaps suggest form
  without over-detailing.
- **Hatching**: parallel lines for shadow, cross-hatching for deep shadow,
  varying density for gradation.

### Shading
- **Screentone**: halftone dot patterns for mid-tones, applied as a flat
  field with a defined edge (not gradients).
- **Hard shadows**: a single strong light source creates sharp shadow
  boundaries, not soft gradients.
- **Reflected light**: the shadow side has a thin rim of lighter tone
  where light bounces back.
- **Specular highlights**: small bright points on wet surfaces, eyes,
  metal.

### Faces
- **Eyes**: the dominant feature. Multiple layers: white sclera, iris
  (colored ring), pupil (dark center), catch-light (small bright dot),
  upper lash line (thick), lower lash (thin), eyebrow (heavy, expressive).
  Eye shape changes with emotion: squinted for anger, wide for surprise,
  half-lidded for tiredness.
- **Nose**: minimal but defined — a bridge line, a tip, and nostrils
  (often just two small dots or a subtle shadow).
- **Mouth**: lip shape matters. Upper lip thinner, lower lip fuller.
  Mouth shape changes dramatically with emotion.
- **Expression**: the combination of eyebrow position, eye shape, and
  mouth shape creates readable emotion. Manga uses exaggeration for
  clarity.

### Hair
- **Silhouette first**: the hair's outline is the most important element.
- **Flowing strands**: hair moves in clumps, not as a solid mass. Each
  clump has a start (at the scalp) and an end (tapered tip).
- **Volume**: hair has depth — front pieces, side pieces, back pieces,
  each at a different plane.
- **Wind/sweat**: hair sticks to the forehead when wet, flies when
  running.

### Clothing
- **Folds**: fabric gathers at joints (elbows, knees, waist) and drapes
  from tension points (shoulders, hips).
- **Seams**: visible stitching lines at edges, hems, and construction
  joins.
- **Fabric texture**: different materials (hide, fur, cloth) have
  different rendering — fur has individual strands, hide has grain,
  cloth has weave.
- **Wear**: tears, patches, dirt, blood stains tell a story.

### Anatomy
- **Muscle groups**: deltoids, biceps, triceps, pectorals, rectus
  abdominis, obliques, quadriceps, hamstrings, gastrocnemius — each
  defined as a separate mass.
- **Tendons and veins**: visible on forearms, hands, neck, and shins
  in lean individuals.
- **Bone structure**: clavicle, scapula, ribs, iliac crest, spine —
  visible through skin, especially in thin/starving people.
- **Joint definition**: elbows, knees, wrists, ankles have visible
  structure (bony prominences).

### Expression system
- Manga characters have a **default expression** that matches their
  personality, and **emotional shifts** that are readable at a glance.
- Key expressions: neutral, angry, sad, surprised, determined, tired,
  afraid, focused.

---

## 2. Current renderer state (what we have)

### Anatomy rig (buildRig, ik2)
- ✅ Skeleton with joints (shoulders, elbows, wrists, hips, knees, ankles)
- ✅ Inverse kinematics for limbs
- ✅ Contrapposto (weight shift)
- ✅ Body proportions by age/sex (STATURE table)
- ✅ Muscle belly definition (biceps, quadriceps)
- ✅ Fat/starving body shape variation
- ❌ No tendon/vein detail
- ❌ No individual muscle group separation
- ❌ No bone structure visibility (scapula, iliac crest)
- ❌ No joint bony prominences

### Head and face
- ✅ Skull shape (not a circle)
- ✅ Jaw definition
- ✅ Eye (basic: sclera + iris + pupil + highlight)
- ✅ Nose (basic: bridge + tip)
- ✅ Mouth (basic: single line)
- ✅ Hair cap (silhouette)
- ✅ Long hair for women
- ✅ Hollow cheek in famine
- ❌ No iris detail (color rings, texture)
- ❌ No eyelashes
- ❌ No eyebrow expression (static)
- ❌ No mouth shapes (open, closed, talking, eating)
- ❌ No nostrils
- ❌ No ear detail
- ❌ No facial hair (beards for men)
- ❌ No expression system

### Clothing
- ✅ Swim (trunks/brief + top for women)
- ✅ Hide (wrap with shadow side)
- ✅ Fur (with hatching)
- ❌ No fabric folds
- ❌ No seams/stitching
- ❌ No wear/tears
- ❌ No fabric texture variation

### Hands and feet
- ✅ Hand as ellipse with thumb
- ✅ Foot as wedge
- ✅ Fingers (at s>=3)
- ❌ No individual fingers
- ❌ No knuckles
- ❌ No fingernails
- ❌ No toe definition

### Shading
- ✅ Single light source (top-left)
- ✅ Shadow side fill
- ✅ Reflected light (subtle)
- ❌ No screentone
- ❌ No crosshatching
- ❌ No specular highlights
- ❌ No rim light

### Line quality
- ✅ Round caps and joins
- ✅ Variable ink weight (ink*1.2 for outlines, ink*0.7 for details)
- ❌ No tapered strokes
- ❌ No broken lines
- ❌ No hatching

---

## 3. Implementation plan

### Phase A: Line quality and shading (foundation)

**A1. Variable line weight system**
- Add a `stroke()` helper that accepts weight, taper, and dash parameters
- Outer silhouette: thick (ink*1.8), tapered at extremities
- Major interior lines: medium (ink*1.0)
- Detail lines: thin (ink*0.5-0.7)
- Dashed for construction/hidden lines

**A2. Screentone shading**
- Create a `screentone()` function that fills a path with halftone dots
- Dot size and density adjustable per material
- Use for mid-tones on skin, cloth, and landscape

**A3. Hard shadow with reflected light**
- Replace soft shadow gradient with hard-edged shadow
- Add thin rim of reflected light on the shadow side
- Shadow boundary follows the form's contour

**Files**: `web/index.html` (drawSketch, paintForm, limbOutline), `docs/index.html`

### Phase B: Face overhaul (the biggest visual impact)

**B1. Eye system**
- Multi-layer eye: sclera → iris (colored ring with radial gradient) → pupil → catch-light
- Upper lash line: thick, with individual lash strokes at close zoom
- Lower lash: thin line
- Eyebrow: heavy, expressive, changes with emotion
- Eye shape variation by emotion (squint, wide, half-lid)
- Eye socket shadow

**B2. Nose**
- Bridge: single line from brow to tip
- Tip: small shadow under the tip
- Nostrils: two small dots/shadows (at close zoom only)

**B3. Mouth**
- Lip shape: upper lip thinner, lower lip fuller
- Mouth shapes: closed (line), slightly open (gap), talking (open with teeth), eating (wide)
- Lip color: slightly darker than skin

**B4. Expression system**
- Add `expression` field to bodyOf() based on activity, mood, health
- Expressions: neutral, focused, angry, sad, tired, determined, afraid
- Map to eyebrow position, eye shape, mouth shape

**B5. Hair overhaul**
- Hair silhouette with individual strand clusters
- Front, side, and back hair pieces at different planes
- Strand tapering (thick at root, thin at tip)
- Hair movement in wind/running
- Beards for men (at close zoom)

**B6. Ear detail**
- Ear outline with antihelix and helix
- Ear shadow (at close zoom)

**Files**: `web/index.html` (drawSketch head section), `docs/index.html`

### Phase C: Body and anatomy

**C1. Muscle definition**
- Separate muscle groups: deltoids, biceps, triceps, pectorals, rectus abdominis, obliques, quadriceps, hamstrings, gastrocnemius
- Tendon lines at joints (elbow, knee, wrist, ankle)
- Vein lines on forearms and shins (lean individuals)
- Muscle striation at close zoom

**C2. Bone structure**
- Clavicle (already added, enhance)
- Scapula outline (at close zoom)
- Ribcage detail (individual ribs at close zoom)
- Iliac crest (already present, enhance)
- Spine line (subtle)
- Knee and elbow bony prominences

**C3. Joint definition**
- Elbow: olecranon process
- Knee: patella, tibial tuberosity
- Wrist: carpal bones
- Ankle: malleoli (inner/outer)

**C4. Skin texture**
- Pores and blemishes (at close zoom)
- Sweat drops (during exertion)
- Dirt/grime on skin (Lagoon)
- Sunburn/tan lines (Lagoon)

**Files**: `web/index.html` (drawSketch, bone, limbOutline), `docs/index.html`

### Phase D: Clothing and equipment

**D1. Fabric system**
- Fold lines at joints and tension points
- Seam lines at construction joins
- Fabric texture per material (hide grain, fur strands, cloth weave)
- Wrinkles that follow body movement

**D2. Wear and damage**
- Tears and patches on hide clothing
- Dirt stains on lower garments
- Blood stains (after fights)
- Weathering on fur

**D3. Equipment detail**
- Better tool rendering (spear tip, hoe blade, basket weave)
- Carried loads (deer carcass, infant swaddle)

**Files**: `web/index.html` (drawSketch clothing section), `docs/index.html`

### Phase E: Hands and feet

**E1. Hand detail**
- Individual fingers (at s>=2)
- Knuckles and nail beds
- Thumb opposition
- Palm lines (at close zoom)
- Grip variations (holding tools, open hand, fist)

**E2. Foot detail**
- Individual toes (at s>=3)
- Arch definition
- Heel
- Barefoot vs shod

**Files**: `web/index.html` (drawSketch bone hand/foot section), `docs/index.html`

---

## 4. Implementation order

1. **Phase A (line quality + shading)** — foundation, makes everything else look better
2. **Phase B (face overhaul)** — biggest visual impact, most recognizable manga trait
3. **Phase C (anatomy)** — adds realism, especially at close zoom
4. **Phase D (clothing)** — adds texture and storytelling
5. **Phase E (hands/feet)** — final polish

Each phase should be a separate commit with before/after screenshots.

## 5. Performance considerations

- The sprite cache already deduplicates identical figures
- New detail should be gated by zoom level (s thresholds) so distant figures stay cheap
- Screentone should be cached per-material, not per-figure
- Line weight should scale with zoom to avoid overly thick lines at distance
- Consider a "detail level" setting (low/medium/high) for the 2016 MacBook

## 6. Testing

- `tests/test_style.py` pins the figure sprite box size (currently 60×60) — update if changed
- `tests/test_contract.py` pins the summarize() contract — new fields need new tests
- Add visual regression tests: render a figure at 3 zoom levels, compare pixel hashes
- Add tests for expression system: each activity maps to a valid expression

---

## 7. References

- **Vagabond** (Inoue Takehiko): the gold standard for manga anatomy. Brush ink,
  minimal screentone, maximum anatomical accuracy.
- **Berserk** (Miura Kentaro): crosshatching, extreme detail, dark atmosphere.
- **Gantz** (Oku Hiroya): photorealistic rendering, technical detail, body armor.
- **Blade of the Immortal** (Samura Hiroaki): brush-and-ink, flowing hair, dynamic poses.
- **Monster** (Urasawa Naoki): clean lines, psychological realism, minimal shading.
- **Ghost in the Shell** (Shirow Masamune): technical detail, mechanical precision.

The current renderer's skeleton-driven approach (buildRig, ik2) is already
more sophisticated than most manga artists' construction. The gap is in the
**rendering layer** — how the skin, face, hair, and clothing are painted
around the skeleton. That's where this plan focuses.
EOF
echo "done"