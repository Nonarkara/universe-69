# Island resources, human movement and a century per day

The task is to watch two worlds, understand how their people live, and follow
successive generations. The worlds lead; identity/time/population orient the
comparison; conditions and the record explain it. Reading pages put title,
content and pager in that order.

## Found · Changed

- The unfinished fertility draft reduced conception but did not make habitat
  capacity physical. Camps could create additional copies of renewable food,
  fish could be found on dry beach, and nearby targets could lie across water.
  Wild patches now belong to terrain, deplete/regrow once, and are shared by
  camps. Food, farms, pantries and animal encounters respect connected land.
  Wildlife is no longer replenished by invisible low-population respawns.
- Ocean and lagoon tiles existed, but freshwater did not constrain survival.
  Inland banks now supply finite water. Fetching, carrying, depositing,
  drinking and nursing debit the actual reserves; water spoils, seasons affect
  renewal, and sustained thirst can kill. These coefficients are illustrative
  model choices, not measured hydrology or clinical thresholds.
- New worlds use a Sri Lanka-inspired tropical coastal ecology with forest,
  shores, freshwater seeps, cultivable ground and wet/dry seasons. The
  procedural map is an analogue, not surveyed Sri Lanka. Existing saves keep
  their terrain version and seasonal regime. See RESEARCH.md for the FAO and
  WWCT source links and the boundary between sources and calibration.
- A walk had stance/swing code but its stride disagreed with the skeleton:
  the supposedly planted foot drifted by up to 0.258 world tiles. Profile
  stride now derives from leg length, stature and the shared 62% stance law.
  Pelvis sway no longer displaces a planted foot. Fixed motion steps preserve
  equal movement at different display frame rates. A ten-unit sweep, slower
  pace, stature-scaled children and bounded catch-up replace the rapid
  shuffle; weight transfers smoothly instead of snapping sides. Candidate
  diagnostics record effective source hashes and gait constants. Close walking uses 48
  cached poses, with 12 at a distance to keep crowds inexpensive.
- Sleep targets were overridden by the resting-arm rule; bedrolls scaled
  stature twice; far figures lost their cover. Corrected targets reach the
  rig, mats fit their bodies and near/far covers share one implementation.
  EDEN supplies bedding; primitive LAGOON sleeps on bare ground until its
  existing hide/fur clothing state supports bedding. No resort pillow is
  invented for LAGOON. Age stage and bedding are included in sprite identity.
- The minimum sprite scale prevented the smallest camera rung from using its
  small-figure drawing. Figures now follow actual camera scale while retaining
  age/sex proportions, body condition, injury, caches, poses and particles.
- Mobile reader images used an inner horizontal scroll. Removing it exposed
  a loading bug: an unloaded image measured 0×0 and expanded over the pager.
  All 91 static figures now include their actual asset dimensions and reserve
  aspect-correct space at an explicit page width before decoding. Legacy
  figures without metadata retain a stable fallback. Research summary text
  is set before measuring its page. No book/archive prose changed.
- Temporary spatial indexes used tuple keys, violating plain JSON state.
  Both site and child grids now use matching integer keys. Before/after
  canonical snapshots and events agree; these cache corrections do not change
  the measured trajectory. The first failed suite is retained as superseded
  evidence, followed by final green checks.

- The first century run exposed a causal nursing error: food nursing and
  mother-following lasted three years, but water nursing stopped at six
  months. A hydrated mother could feed a one-year-old who still died thirsty.
  Both flows now use the same under-three window, retaining maternal water
  cost, proximity and living-mother checks. That run is explicitly superseded;
  the final results come from a replacement run after the correction.

## Clock and provenance

Engine **2026.10.30.1** defaults to **0.6 seconds per part**, four parts per
360-day year: `0.6 × 4 × 360 × 100 = 86,400` real seconds. Thus one real day
is 100 simulated years, and a millennium takes ten real days. Eight pairs
found each world; births, aging and mortality produce the descendants.

Pace migration preserves completed and pending time. Explicit environment
pace overrides still apply; the masthead reads the active clock rather than
claiming 100 years/day for a slow test instance. The final fresh browser
instance deliberately uses 3,600 seconds/part, correctly shown as 0.0167
years/day. Current-engine lab snapshots use the actual default 100 years/day.
The web mirror retains its configured upload interval and shows snapshots.

This engine changes future trajectories. Prior release figures are historical.
The live MacBook and its state were not accessed, reset or restarted here.

## Verified

- [diagnostic/](diagnostic/) shows the actual renderer at a 120 CSS px adult
  reference height, with ages, both adult sexes, BMI, injury, elder hair,
  sleep and several walking phases. These are explicitly synthetic drawing
  fixtures, not claimed simulation events. A separate agent inspected them.
- [helpers/](helpers/) records the numerical/browser regressions. The
  preserved baseline failed four meaningful body/motion checks; the corrected
  renderer passes them. Independent numeric checks cover 16 age/sex bodies,
  four limbs each, planted-foot drift and equal wall-time motion at
  20/30/60/120 fps. Bone lengths remain fixed to numerical precision.
- [reader-fix-before/](reader-fix-before/) records the actual phone clipping.
  [reader-fix/](reader-fix/) holds the 18 passing cold-image checks: network
  responses are held until after measurement, then released and decoded.
  Archive and Origin pages fit before and after; image rectangles are stable.
  The 390×844 Origin overflow was 144 px; the archive also grew after decode.
  Retry recovery at 600 ms polling passes 11 focused checks in
  [retry-fix/](retry-fix/). The harness keeps failed responses until the
  actual Retry click, so background polling cannot race the button away.
- [final-fresh/](final-fresh/) records final-source tablet/desktop passes of 227 each. The first
  final-source phone attempt had one unattributed connection reset; the
  [fresh-phone-recheck/](fresh-phone-recheck/) full journey passed 253/253,
  with both fonts ready, no failed font faces and no console errors. Every reader page is exercised, along with focus,
  actual controls, errors/retry, zoom, drag, follow, expanded combinations,
  island overview, painted canvases, decoded images and person detail pages.
  The clean final passes have no browser errors/failures. A separate agent
  reviewed the rendered states.

- [day-3000/](day-3000/) is the corrected current model with EDEN 34 /
  LAGOON 25: 254/254 phone, 237/237 tablet and 227/227 desktop checks pass.
  Numeric event years match production. The release manifest confirms no
  screenshot was changed after the final report, including after an obsolete
  capture process was stopped.
- [day-36000/](day-36000/) is the current year-100 model with EDEN 614 /
  LAGOON 25: 254/254 phone and 238/238 at each wider viewport. All checked
  states fit and retain their selected bodies, full reading content and
  navigation; both fonts loaded, with no console errors. Every viewport's
  actual HTML SHA matches the reviewed full-journey renderer, not only a
  requested file path. The final lifecycle-only patch is scoped below.

### First-screen geometry

| Viewport | Masthead | World headings | Instruments | Record | Total chrome | Each scene |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 390×844 | 35 px | 55.5 px, stacked | 27 px | 54 px | 171.5 px / 20.32% | 335.25 px |
| 1024×768 | 35 px | 28 px, shared row | 109.375 px | 54 px | 226.375 px / 29.48% | 541.625 px |
| 1440×900 | 35 px | 28 px, shared row | 54.6875 px | 54 px | 171.6875 px / 19.08% | 728.3125 px |

In the populated sets, actual events earn more record space. Total chrome
is 228.5 px / 27.07% at 390, 302.375 px / 39.37% at 1024, and 247.6875 px /
27.52% at 1440. Each scene is respectively 306.75, 465.625 and 652.3125 px
high. Expanded states and exact element rectangles are retained in reports.

The compact geometry is unchanged; this pass repairs meaning and motion
rather than arbitrarily shrinking surfaces. Instruments wrap at 1024 to keep
their labels readable. Both primary scenes remain visible. The overview uses
the real world and existing camera controls; camp shots alone do not establish
island composition. There is no unnecessary horizontal scroll, reading clip,
UI overlap or hidden followed body in the checked final states.

## Current model measurement and reproduction

[unittest-python39.log](unittest-python39.log) records all **231 tests**
passing under Apple Python 3.9.6. The final 40 style checks, JavaScript parse,
mirror comparison and independent numeric gait checks also pass after the
last renderer calibration. The earlier failed JSON suite and red nursing
regression are retained and explicitly superseded by the corrected release.

The current seed-69 arc completed **36,000 days / 144,000 parts / 100 model
years** under Python 3.14.6 in 1,146.888 workbench seconds. Peak process RSS was
44,875,776 bytes (42.8 MiB), not a performance promise for the 2016 MacBook.
[arc-36000.json](arc-36000.json) retains the results and
[lab-36000.log.gz](lab-36000.log.gz) retains its raw log.

| World | Final people | Peak | Generation reached | Outcome |
| --- | ---: | ---: | ---: | --- |
| EDEN | 614 | 619 | 6 | 229 withdrawn; no extinction |
| LAGOON | 25 | 48 | 5 | Six technologies; one tribe; no extinction |

LAGOON's recorded deaths were dominated by dehydration (61), compared with
starvation (2). The registry returned 14 supported, 1 contradicted and 2
undecided checks; the famine-dominance claim was contradicted. This is not
validation of the literature or proof of a civilization's eventual arrival.
`STUDY.md` records the full cause table and limitations. No fertility/yield
parameter was changed to make the run grow toward a desired ending.

Raw engine saves, viewer snapshots, terrain and event rows are retained in
[fixtures/](fixtures/), with numeric event years matching the actual server
contract. [checkpoint-invariants.log](checkpoint-invariants.log) checks raw
saves without migration repairing the input: IDs, reciprocal bonds, clocks,
rooms/roles, finite resource bounds, site uniqueness, shores and annual
population change = births − deaths. Run the retained
`fixtures/verify_checkpoints.py` to inspect them again. `run_arc.py` repeats
the bounded lab run and captures checkpoints in an optional scratch output
directory. These are lab fixtures, never live state or restart seeds.

[provenance.json](provenance.json) records current source hashes and runtimes.
The pre-nursing-fix arc in [superseded-pre-milk-fix/](superseded-pre-milk-fix/)
is an unpublished candidate, not current measurements. Its dehydration counts
must not be quoted as the shipped result. The full reader/body/geometry journeys used HTML hash
`32ca5a85f3ac96827023162c767c95b238aaf9a03e340f51d99c47a97e8c5332`.
Final lifecycle checks then found stale local terrain, derived forest fields,
reused animal IDs and old event rows after an explicit genesis. The local
world response and wildlife identities now reset on day rewind; terrain-key
changes invalidate the derived fields; an authoritative empty event list
clears the old record. Record year/type text is also escaped.

[restart-before/](restart-before/) records the original refetch failure;
[restart-derived-before/](restart-derived-before/) records stale same-size
forest fields; [restart-lifecycle-before/](restart-lifecycle-before/) records
retained history/animal state and literal-markup failures.
[restart-lifecycle-after/](restart-lifecycle-after/) passes **69/69 at every
required width**, with no browser/console errors. The actual new terrain and
all four derived fields match; record rows and animal identities reset; world,
island overview, follow/MORE and keyboard/focus helpers remain usable. A
separate agent inspected the final PNGs. The current source hash is
`5213612d36db015be71b729d7a2818ba5c9e1201ee88e99b4721217a4449b791`.
The full earlier reader/body journeys remain valid for their recorded source;
CSS, composition, anatomy and readers are unchanged by this lifecycle patch.

## Remaining

The figures are drawn 2D anatomy, not scanned people or motion capture.
Map/drawing units are abstract, not surveyed metres, and people are enlarged
for legibility. Front/back views retain shallow projection and limited depth/foreshortening;
profile contact tests do not prove full 3D contact. Pixel rounding and cached
poses remain discrete. Dense people can overlap at island scale.

A century of one seed does not validate millennia or guarantee survival.
The technology ladder ends at writing, without a full city-state, industrial
or modern civilization model. Kinship genetics, complete nutrition, material
manufacturing and full hydrology/pathogen processes are not simulated. No
civilization date is forced by the clock. Actual 2016 MacBook throughput,
live state/restart and external deployment remain unverified.
