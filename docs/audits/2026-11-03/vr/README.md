# VR observation and geometry repair — 2026-11-03

Task: inspect the same two recorded worlds, enter either scene and hold a
moment without inventing inhabitants' movement or changing their actions.
The world picture wins, followed by time/source context, then navigation.

**Scope:** final viewport/keyboard evidence uses the exact production geometry
and packet with a harness-only 1 fps drawing-loop substitution. Production
animation/input performance remains **unverified** after an intermittent native
RECORD-dispatch timeout. This is not a Quest/WebXR headset pass.

## Found

- Held mode changed the recorded position and/or action of all 20 people
  in every captured viewport, including invented walks. Timelapse also offset stationary fishers,
  drinkers and social activity between packets.
- Resting poses used adult-sized local joints for children. Head size, limb
  fractions and prepubertal body widths disagreed with the canonical 2D age
  table; the newborn skull could intersect the floor.
- Same-iteration clock rewinds retained stale terrain, and reused person IDs
  could interpolate from ancestors. Terrain-only changes did not invalidate
  the static mesh.
- On 390×844 the 207.531px readout overlaid LAGOON while the portrait camera
  left about200px above EDEN. Inside either world, repeated context for both
  worlds displaced the scene. Jost was declared but not loaded.

## Changed

Held mode now preserves exact recorded coordinates and actions. Only actual
WALK/FORAGE/HUNT/SCOUT activity may interpolate between observed endpoints.
The complete straight chord must remain dry, including diagonal corner gates;
otherwise the viewer snaps to the observed endpoint. No invented detour.

Head count, leg/arm fractions and child shoulder/hip proportions match the 2D
age tables. Height and torso/shoulder/hip sex differences begin at puberty.
Each articulated limb retains its age-specific bone lengths in every pose.
Neck and joint surfaces connect the capsule segments; lying support comes
from actual head/torso/limb extents, including the infant skull.

Timeline/terrain changes reset the relevant drawing caches. Identical or
wall-only polls do not fabricate a pending record; fresh transport metadata
is preserved. Real updates and calendar rewinds use the neutral “updated
record” caption. Holding is ignored before the first record exists. The default
readout shows both short world summaries at TABLE, or the active world inside.
RECORD retains the full context in pages. Portrait framing brings the worlds
into the picture. Local, licensed Jost loads for DOM and canvas text; Source
Serif 4 is also vendored for the 2D reader. Fonts and licenses are mirrored.
The legacy cohort counter is labelled competent adults 16–45, not fertility.

## Verified

Sources, source hashes, exact packet hashes and raw geometry are in
`verification.json`, `before/report.json`, `after/report.json` and the
keyboard report. The packet records engine `2026.11.01.1`, day 53460/year 148, EDEN iteration 3
and LAGOON iteration 2; this is real public content, not a natural run of the
new fuzzy engine. The public packet is retained centrally under
`../public-records/snapshot.json.gz`; no model fields were staged or edited.
All 20 people and 569 animals remain in the record. Captures use native controls
on the immutable public packet, not the instrument or a new simulation.

The original before-images ran at production cadence in isolated headful
Chrome using ANGLE Metal/Apple M3. Intermediate production-cadence captures
also completed, but the final production refresh timed out during a visible,
stable RECORD button's native click dispatch. Earlier SwiftShader screenshot
stalls are retained failures, not passes. The Mac was locked, so native CUA
was unavailable; isolated Chrome could still render.

The final static/keyboard probe uses headless Chrome/ANGLE Metal with only
`renderer.setAnimationLoop(frame)` replaced by `setInterval(frame,1000);frame()`
in the retained served HTML. The production file is unchanged. Source and
served hashes are distinct; the exact diff is auditable. This proves static
geometry and native keyboard behavior, not production animation performance.
All 20 people and 569 animals are retained; nothing was filtered to obtain a pass.

The final source also exempts open RECORD reading and keyboard-visible focus
from automatic chrome dimming. All three viewports retained opacity 1 after
16 seconds without pointer movement; the idle camera still dims normally.

| Viewport | Old readout | New readout | Recovered | Old held mismatches | New |
|---|---:|---:|---:|---:|---:|
|390×844|207.531px|73.586px|133.945px|20/20|0/20|
|1024×768|129.172px|73.586px|55.586px|20/20|0/20|
|1440×900|129.172px|73.586px|55.586px|20/20|0/20|

Chrome cost is measured from actual top/bottom overlay extents, without a
universal percentage cutoff. Phone controls earn 34px targets; the expanded
record earns its additional height with context and keyboard paging. No
earned field or action was removed to obtain the compact summary. Both worlds
remain visible at TABLE; the person, not a repeated dashboard, dominates INSIDE.

All populated body instance matrices were finite with positive determinants.
The 30 focused tests pass on Apple Python 3.9 (including optional Node checks).
Actual JavaScript helper tests cover deterministic record motion, water and
corner gates, age/sex bone lengths, puberty onset, lying support over body-size
ranges, cache continuity and resets. Core tests use only the standard library;
Node execution is optional workbench verification, not a runtime dependency.
The browser also delays the first packet and presses R before loading, then
checks that no empty record was held. Repeated identical held polls must arrive
without a false pending row. Native Tab/Enter opens paging, shows a visible
outline, advances/returns and traverses all four TABLE record pages at each
viewport.

## Remaining limits

This is a desktop WebGL visual review, not Quest/WebXR headset validation.
The VR surface remains a coarse articulated capsule figure, not the 2D ink
anatomy rig. It does not have the 2D planted-foot IK solver: time-driven gait
and endpoint smoothing may slide, and uneven-terrain body collision remains
approximate. Those are explicit limitations, not claims of physical realism.
The captured packet contains no infants; infant geometry is controlled helper
verification, not a natural infant scene. Neither these screenshots nor the
model trajectories validate human behavior, cognition or biology.
