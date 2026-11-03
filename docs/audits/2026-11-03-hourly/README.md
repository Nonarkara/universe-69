# Hourly clock and human figures — 2026-11-03

The user changed the clock to one year per real hour and asked for clearer,
higher-resolution humans, timelapse with three or four visible night cycles per
hour, and slower close inspection/walking. Started by pulling `main`: already
up to date at `edaa698`. No instrument state, service, reseed or restart touched.

## Clock and model boundary

A model year is 360 days. One real hour per year means 10 seconds per model
day and 2.5 seconds per part, not one day per second. Default is now 24 years
per real day. The existing environment override still takes precedence.
Engine `2026.11.03.2` records this boundary. Only the default wall mapping,
version and additive summary pace field change: every other engine function's
AST is unchanged (`engine-boundary.json`). Per-part biology and RNG are
unchanged; future events arrive at different real times. Old century trials
remain historical per-part evidence, not a benchmark of this clock.

Tests cover fractional ticks/backlog across a change of pace, save/load, an
hour's 1,440 parts and real-time/default transitions without replaying time.
No new saved fields. Local `/pace` still controls the instrument; a static
mirror cannot control it. VR INSPECT holds the observed record and animates
its recorded body poses at inspection pace; it does not claim to run a second
sealed world or invent destinations while held.

## Graphics and space

- 2D hearth camera: 84 CSS pixels per adult instead of 48; island/camp unchanged.
  Existing wheel zoom, skeleton lengths, planted-foot walk, caches, contact
  drawing, particles and documentary camera preserved. Tapered far limbs,
  jaw/hair/neck/feet and restrained close anatomy landmarks improve legibility.
- Timelapse light follows four representative cycles per model year. Model
  sleep/actions and the actual time label remain daily. Slow instrument mode
  uses actual model light; held records do not extrapolate illumination.
- Found: selected ring circled empty space above the person; sleepers' captions
  floated at standing-body height. Changed: kept the ground selection ellipse
  and put captions beside the body's actual posture. Independent final review
  and recaptures are in `review/`.
- Both worlds remain visible together. Long records/research/help remain paged.
  No font shrink or content removal used to fit the screen.

## Evidence boundaries

`fixture.json` is the exact historical public record retained by the prior audit,
with its embedded terrain. It is not current live state and correctly displays
its old pace as approximately 4.17 years/hour. `current-fixture.json` is a bounded
90-part seed-69 lab fixture produced by `make_fixture.py` from this engine: two
16-person worlds at day22/part1, with the new one-year/hour default. It is not a
live run or evidence of long-term survival.

`2d/final-*` contains the full historical-record interaction pass at all three
widths: 272/272, 256/256 and 246/246 checks, zero browser errors, including
expanded records/readers/error+Retry/focus and body/movement preservation.
The subsequent only 2D differences remove the elevated ring and correct the
posture caption; `review/final-*-selected.png` captures those exact final bytes.
The current fixture also renders all three widths (12/12,11/11,11/11 checks).
Source hashes, viewport geometry, page checks and fixture provenance are in
those JSON reports. Anatomy diagnostic images are explicitly synthetic bodies
calling the actual renderer, not simulation observations.

Independent 2D review measured total first-screen chrome (including world
headings, instruments and record): 390×844 216.78px/25.68%;1024×768
243.67px/31.73%;1440×900 192.28px/21.36%. Worlds dominate first, their identity/
time/population second, selected person's information or events third. Primary
views/actions are visible together; no unintended overflow, clipping or nested
scrolling. Expanded records earn their height with actual events.

The pictures remain stylized anatomical figures, not photoreal humans. Full
3D planted-foot IK, measured 2016 MacBook performance, and physical Quest
verification remain outside the verified result. No civilization or fertility
claim follows from a drawing or this clock change.


## 3D verification

The procedural 3D figures use a continuous rib cage/waist/pelvis profile,
tapered limbs with overlapping joint sections, a jaw/scalp/face, connected
ankles and properly supported soles. Infants and adults lying down face up;
actual instanced-geometry bounds are checked for ground contact. Instancing
and recorded destinations/actions remain intact. The canvas now permits a
2.5 device-pixel ratio ceiling; the retained DPR2 capture is a true
2880×1800 drawing buffer at 1440×900 CSS pixels.

`vr/` retains nine frames from the unmodified production animation loop on
Apple M3 Metal: table/inside at all three widths, standing/seated synthetic
anatomy and a DPR2 inside view. The anatomy fixture runs actual drawBody;
it is explicitly synthetic. 126 age/sex/build/posture vertex-bound cases
have positive minimum ground clearance (+0.00131709 world units). They do
not prove collision-free interactions between people or full planted-foot IK.

Found: round hair volumes covered faces, zero-radius limb ends pinched into
separate beads, displaced feet missed ankles, soles floated, sleepers faced
into the ground, and added hip/ankle instances exceeded the old allocation.
Changed: shaped profiles, overlapping limb joints, heel/ankle connection,
pose support, face-up rest and eight foot/joint slots per person. Found on
390px: the table's south coastline ran under the readout. Changed: portrait
camera framing, preserving world size; final island edge clears the readout.
Help/keys gained content-sized contrast backings, readable 12px text and no
stacked overlap. A final CSS-only change makes record-age text muted rather
than dim for adequate contrast on the translucent readout; independent final
keyboard/readout captures cover that final colour.

The component README and manifest distinguish exact captured bytes from
that final colour delta. Normal-loop rendering is verified; sustained frame
rate, performance on the 2016 MacBook and headset input remain unverified.


## Final release checks

Frozen release: **610/610 tests pass** on Python3.14.6 in225.765seconds,
exit0. All56 recorded runtime/test source hashes are unchanged through the
complete run. Apple Python3.9.6 focused engine/clock/style/VR/resource checks:
**202/202 pass**, exit0. Fresh final style+VR checks: **103/103 pass**.
Logs/status/source hashes are in `tests/`. Earlier full attempts loaded old
VR assertions while source was changing (hair/light then six-versus-eight
joint slots); their failures are retained and explicitly superseded by the
frozen complete green run. No model test was waived or weakened.

Independent visual review: pass for the inspected three-width 2D and 3D
fixtures, final-source keyboard/contrast states and source-bounded anatomy.
See `review/vr-independent-review.md` and `review/independent-review.md`.
Preview servers and owned browser sessions were stopped. The instrument was
not restarted; its existing environment override, if any, still wins over
the new default until changed on that machine.
