# Human anatomy and locomotion — VR second pass

The task is to compare the worlds and inspect recognizably human inhabitants,
including neutral adult external anatomy, without inventing actions or movement.
The source is exactly SHA256
`d47dd0e3253acd5d2a34dd50674a82dc047f731884f5fb612d838dbf4451702a`.
Both mirrors are identical. Production captures assert source unchanged from
start to finish; no animation-loop cadence replacement was used.

## Found and changed

The shared surface-of-revolution torso gave every person the same hourglass.
Hip joints at .92 of half-pelvis width put the thighs outside the pelvic mass;
shoulder roots sat at the outer shoulder contour. These produced the mannequin/
disconnected-body appearance. The new closed surface has independent lateral
and front/back dimensions at the rib cage, waist, pelvis and neck. Adult male
and female profiles differ; juveniles use a neutral profile. Hip roots at .52
of half-pelvis width emerge inside the pelvis, and the arm roots are embedded
below the deltoid contour. Palms follow forearms and have a small thumb.

The old VR forced coloured torso uniforms onto women and hides onto arms and
legs. Clothing now matches the 2D recorded modesty/identity/winter rule. A
swimsuit and hide wrap cover their own regions; winter fur covers the torso
and limbs. No new cultural or body state is invented.

Human-scale bare adults have restrained external landmarks. A finite numeric
age >=18 and known sex are mandatory; missing/unknown ages and minors never
receive explicit detail. Clothing, table distance and records of mating or
birth suppress it. Male anatomy is non-erect; female pubic contours follow the
front of the pelvis rather than hanging below it. Nipple depth follows the
actual shared torso-ring profile. Clinical adult fixtures are exclusively age30;
the age6 neutral proportion fixture is separate and contains no explicit detail.

The former walk phase depended on wall time, so feet glided independently of
actual travel. The new phase derives only from distance actually interpolated
along a permitted recorded dry segment. During 62% stance, the foot's local
backward displacement cancels the body's forward movement. Two-bone IK and
pelvis drop keep thigh/shin lengths fixed and the planted ankle on the floor.
The same-side hand swings against its foot. Arm IK gives observed eating,
drinking, talking, grooming and gathering their own gestures. Quiet thorax
breathing continues during inspection. No gesture changes an action, intent,
position or the biological clock. Held records remain held.

For a zero observed population, phase text reads EMPTY rather than advertising
an earlier growth phase. This does not infer a death cause or reseed countdown.

## Verified

- `390/1024/1440-{table,inside}.png`: actual unmodified production renderer at
  390×844,1024×768,1440×900 with both worlds retained in the table view.
- `adult-clinical-front.png`, `adult-clinical-side.png`, `adult-seated.png`:
  synthetic known adults age30 through actual `Crowd.drawBody()`, at a shared
  scale. These are clinical/anatomy drawings, not live population observations.
- `child-neutral.png`: separate age6 neutral bodies, no explicit detail.
- `adult-walk-0..7.png`: discrete synthetic adult walk poses through the actual
  renderer. These pictures show articulation; they are not a recording of a
  model-generated trip or a motion-capture benchmark.
- `report.json.gz` (lossless; raw/gzip hashes in `report-provenance.json`): actual transformed THREE vertices in162 age/sex/BMI/standing,
  sitting and lying cases; minimum y=+0.001317090354859829 world units. Counts
  are checked against actual allocated instancing buffers.
- `matrix-proof.json`: raw actual produced arm/leg instance matrices over81
  distances for each of eight age/sex cases (648 poses). Maximum planted-ankle
  world drift is1.0430813e-7 units; maximum segment-length range is3.084587e-8.
  Every same-side hand/foot forward-offset product is negative, confirming
  counter-swing. `analyze.py` derives these results from the raw matrices;
  it does not repeat the rig solver formula as its assertion.
- `surface-proof.json`: actual THREE ray intersections place all four sampled
  female nipple/pubic details across the body's front surface (not floating in
  front or hidden inside).24 actual male/female age/modesty cases preserve
  unknown/minor/covered-body gates. The clinical side image is the visual check
  for the male attachment and neutral non-erect orientation.
- `tests.log`, `tests-python39.log`:36 VR tests pass on Python3.14 and3.9,
  including unknown age, minors, sex, clothing, activity, fixed bone length,
  collinear IK, distance phase and representative light contracts.

The retained fixture is the earlier bounded seed69 engine3.2 day22/part1 run,
16 founders in each world. It is not the current live MacBook snapshot. The
studio replaces only diagnostic mesh instances on that page. `capture.py` and
`surface_proof.py` retain the executed workbench harnesses; relocate their paths
to reproduce. No live state or service was changed.

## Remaining

These are stylized procedural humans, not scans or photoreal bodies. Planting
is verified for straight sampled segments on level ground; turning, slope
adaptation, heel/toe roll, collisions and full contact dynamics are not solved.
All observed actions are not separately validated. The anatomical values are
illustrative drawing proportions, not physiological measurements. Production
frames on this workbench do not establish2016 MacBook or Quest throughput.
Independent review accompanies this component in the parent audit.
