# VR: complete silhouettes, observer light and production-frame evidence

The task is to compare two worlds, then inspect people at human scale without
losing the relationship between the record and what the camera shows.

## Found → changed

- The former uniform capsule trunk, face-covering hair sphere and ball feet
  made the people look incomplete. The trunk is now a closed shoulder/rib/
  waist/pelvis surface; a tapered skull, scalp cap and human-scale facial
  landmarks replace the obscured face. Limb profiles overlap the anatomical
  joint centres, with smaller joint volumes. Feet meet the ankle rather than
  floating in front of it. The final waist profile is broader than the first
  draft. Canonical age/sex proportions and recorded actions remain intact.
- Lying bodies faced the floor, so the nose could intersect it. Supine bodies
  now face up. Ground support includes the elongated feet; seated facial
  landmarks share the head's forward offset. The feet instance allocation is
  eight per person (hip, knee, ankle, foot for each leg).
- Actual model-day lighting could flash at ten-second intervals. Normal light
  is now a smooth representative montage with four cycles per model year;
  model actions and sleep retain the actual calendar. INSPECT freezes the
  applied record, shows its actual day part, and lets the observer walk.
  The button no longer calls that snapshot hold REAL-TIME. Instrument slowdown
  remains the separate control in the main viewer.
- The portrait table previously ended at about y804 underneath the readout
  starting at y760. Camera composition now ends the terrain around y733:
  about 27 pixels of clear separation, with the same world scale. No terrain
  or text was clipped to fit.
- Hint, orientation keys and brand subtitle lost contrast over the changing
  sky/ground. Small backgrounds fit their actual content; hints and keys are
  12 pixels. Hint and brand no longer overlap.

## Verified

`source-vr.html` is the exact captured source, SHA-256
`c2fe5de4837a816de6e9ecb20ef8e2f2bc613b8217d08540ee007fd547a38ec2`.
The capture asserts unchanged source from start to finish. The loop is the
production `renderer.setAnimationLoop(frame)` with no cadence substitution.
The GPU reports ANGLE Metal / Apple M3. This proves these production frames
rendered, not an isolated frame-rate benchmark or old-MacBook performance.

- `390/1024/1440-{table,inside}.png`: real HTML at 390×844, 1024×768 and
  1440×900. No page overflow; both universes remain together in TABLE.
- `1440-anatomy.png` and `1440-seated.png`: explicitly synthetic adult male,
  adult female and child fixtures through the actual `Crowd.drawBody()`.
  These make anatomy assessable; they are not population/model evidence.
- `1440-2x-inside.png`: a fresh DPR2 browser at 1440×900 CSS pixels, actual
  drawing buffer 2880×1800. Production resolution cap is 2.5.
- `report.json`: actual Three.js vertices transformed by the produced instance
  matrices in 126 age/sex/BMI/standing/sitting/lying cases. Minimum y is
  +0.001317090354859829 in local world units with a zero ground/root, so none
  intersects the floor in this fixture grid. Instance counts also fit their
  allocated buffers. This is a concrete geometry check, not the rig formula
  repeated as an assertion.
- `final-tests.log`, `final-tests-python39.log`: all 32 VR tests pass on
  Python 3.14 and Apple Python 3.9. They retain record/action invariance,
  forbidden-water routes, restored worlds, child proportions, held-record
  polling, reader focus and the new light/crowd geometry contracts.

The input `fixture.json` is an isolated short engine run supplied by the root
agent (16 founders per world, day 22.25), not the live MacBook. The studio
replaces bodies only inside the diagnostic page. The capture uses a local
static server, routes state/world to that retained fixture, and makes no
changes to the instrument. `capture.py` retains the executed harness; paths
can be relocated to reproduce it. `manifest.json` hashes these component
artifacts.

## Scope and remaining

These are complete procedural human silhouettes with clearer faces and limbs.
They still look stylized: this is not photorealism, a scanned human, or a full
3D planted-foot IK gait. Quest and 2016 MacBook throughput remain unverified.
INSPECT holds positions and intentions; it does not slow the remote instrument
or invent a continuous unseen life between snapshots.

After these captures, independent review found the small record-age label's
`--dim` colour could fall below AA on the translucent readout. The root agent
changed only `#readout .now` to `--muted` in both mirrors, and is retaining the
final-source bridge plus keyboard/readout evidence separately. Therefore these
nine pictures prove the captured c2fe geometry/anatomy/production rendering;
they do not claim byte-identical final-source colour evidence. Independent
review reports accompany the root hourly audit.
