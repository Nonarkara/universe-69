# Embodied encounters — engine 2026.10.30.6

**Verified causal/UI fixes; demographic realism remains unresolved.** This is
progress toward the continuing digital-human objective, not a completed model.
The workbench never touched the instrument's live state or ran its live process.
The default clock remains 100 model years (360 days each) per real day.

The retained before-conception probe was run on engine `.5` at base commit
`6f8c579`. Its forced success probability checks eligibility only; it is not
a population forecast. It demonstrates the four remote/ghost eligibility bugs.

## Found → changed

- Pregnancy previously needed no actual encounter and could use a remote,
  sleeping or missing father. Frozen simultaneous mutual contact now supplies
  the actual father and hereditary values; later bonds cannot rewrite paternity.
- Mating/grooming used to assign both people's actions. Invitations now change
  only their initiator; recipients score their own choices. Body needs can
  refuse, and actual arrived contact alone satisfies personal intimacy/grooming.
- EDEN work/food scores mathematically excluded mating from the choice band.
  A separate adult intimacy need repairs reachability in both worlds. Its
  seven-day urgency and weight 1.5 are explicit hypotheses, not fitted rates.
- Global automatic pairing is removed. LAGOON singles bond at actual mutual
  contact; EDEN contact does not create a permanent bond. Known direct/shared
  parents are excluded using recorded relationships, without inventing genetics.
- Labour is visible one illustrative model day before due delivery; only the
  mother stops. Helpers choose independently. Actual delivery/miscarriage ends
  the labour pose; delivery does not wait for a helper.
- The viewer formerly drew a coupled sexual pose from a social bond even when
  proposals were not reciprocal. Actual contact now controls the joint picture,
  neutral pending poses and accurate words. The first visible snapshot now
  initializes the record immediately, removing blank footer space before the
  next animation update. No new panel is added.

## Final bounded century

Seed 69; 36,000 model days; Python 3.14.6; 300.598 seconds on the workbench while
other verification was running. This is not a MacBook benchmark. All 11 simulation
source SHA256 values match before/after; see arc-provenance.json and source-review.md.
The read-only instrumentation consumes no RNG and never changes world state.
It counts unique simultaneous pair/part facts, not distinct intercourse sessions
or fertile conception opportunities. Exact lab output/data and executed runner
are retained alongside this note.

| World | Peak | Max generation | Unique mate contact parts | Extinction day | Model year | End population |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| EDEN |16|1|734|28,555|79.32|0|
| LAGOON |17|2|10,324|35,630|98.97|0|

Both remain iteration 1 at year 100: the existing 30-year quiet reseed delay has
not elapsed. Both wrote a postmortem. EDEN's 16 recorded deaths were age deaths;
this was founder attrition without births, **not a demonstrated Calhoun collapse**.
LAGOON's historical discovery record contains fire, shelter, stone tools,
fishing and preservation; all practitioners are dead at the endpoint. Nothing
here demonstrates agriculture, writing, great civilizations or long-run survival.

The old unconditional 1/180 and 1/240 daily coefficients, divided by four,
are now tried only at actual contact. They are **not calibrated per-intercourse
probabilities**. Age/body/nursing modifiers remain. The changed exposure gate
substantially changes effective fertility. The isolated ten-year EDEN diagnostic
in diagnostic/ found 260 eligible trials, summed probability 0.3571916667 and
zero pregnancies: meetings work; zero births is plausible under the retained
hazard. This is a time-basis/calibration problem to investigate, not evidence
that the island cannot support humans or that extinction was inevitable.
No coefficient was increased to manufacture a surviving population.

## MSH first-screen repair

Independent rendered review caught a transient first-snapshot gap: poll installed
the worlds without initializing the record. Before the next record animation
tick (roughly 0.27–0.53 seconds), the empty footer occupied 111px on phone and
130px on desktop. Clicking MORE happened to initialize and fit the same empty
content to 54px. The fix renders the authoritative record in poll immediately;
no spacer, clipping, font shrink or feature removal is involved.

Final focus/MORE footer height is 54px at 390, 1024 and 1440; first-screen
world space recovers 57px on phone and 76px on desktop. The independent review
records total chrome, task visibility, hierarchy and preservation per viewport.
Before source/images/geometry are in viewer/before-record-init/; final images,
reports, fixture provenance and exact HTML hash are in viewer/.

## Verification and limits

- **Final full suite: 453/453 pass on Python 3.14.6 in 153.660 seconds.**
  `full-suite-shipped.log` covers the final source, including the first-snapshot
  record fix and adult-only visual pose gate. Apple Python 3.9.6 also passed the
  prior 452-case full suite in 315.573 seconds; all 47 final style tests pass
  on that runtime (`style-shipped-apple.log`).

- 49 source-focused cases independently pass on Apple Python 3.9; see source-review.md.
- The initial Python 3.14 suite ran 452 tests with one failure: the old naming
  test assumed a natural birth within 2,000 days. It now checks the naming event
  at a controlled actual birth in each world; the final suite passes.
- 16 final needs cases pass, including the corrected naming semantic assertion.
- Viewer: 268/268 journey checks at 390, 242/242 at 1024, 242/242 at 1440;
  plus 441/441 controlled contact/labour/postpartum and first-snapshot checks across all three.
  These are explicit synthetic setups passed through actual engine APIs,
  not natural behavioural or biological validation. See viewer/provenance.json.
- Persistent defaults/JSON roundtrip, actual paternity after bond change,
  no ghost/dead/remote conception, simultaneous contact, independent refusal,
  desire daily units/cap/satisfaction and labour transitions are pinned by tests.

Remaining: fertility timing/rate calibration, coarse four-part/day actions,
limited recorded kinship, voyage physiology, clinical labour/medical calibration,
finite predefined technology, abstract tools/fuel/materials and general cognition.
MacBook throughput and live restart are unverified. Island geography remains a
procedural coastal analogue, not a surveyed physical replica. The anatomy rig
and existing age/sex/gait laws remain; this increment fixes interaction truth,
not anatomical realism in general. The larger goal remains active.

The next model increment must define encounter sessions versus contact parts,
then calibrate reproductive timing/exposure and conception together against
primary data and multiple seeds. Preserve independent choices and actual
paternity; do not restore ambient pregnancy or target a desired population.
