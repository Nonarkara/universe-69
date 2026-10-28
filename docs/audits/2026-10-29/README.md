# Finish the needs model and terrarium viewer

The task is to compare two sealed worlds, watch an inhabitant, and read the
record and research without losing the useful picture. The worlds lead;
identity, time and population orient the comparison; instruments and the
record explain it. A reader page puts its title first, prose second, and
navigation third.

## Found · Changed

- On a 390 px phone, simultaneous expanded details, instruments and record
  consumed the scenes. These related secondary views now share one expansion
  at a time. The record's phone cap is 30% of the viewport; both worlds remain
  visible. This does not remove events: they remain paged and filterable.
- A selected historical inhabitant's full conditions and four diary entries
  made a 227.5 px card in a 220 px scene. The card hid the person it described.
  Name and activity now stay visible above paged facts and diary entries;
  follow framing reserves the measured card and body extents. Short cards
  fit their content. Detail pages preserve the text rather than clipping it.
- Small Help and connection-error dialogs filled the phone despite little
  content. Their sheets now fit their contents with viewport margins; full
  reading documents retain the space they need.
- Oversized nested reader blocks lost text or captions during splitting.
  Pagination now splits the DOM while preserving wrappers, text and images.
  Every reader page is exercised, including oversized paragraphs, source
  notes and figures. Opening Origin after the archive now loads its image
  from the correct book directory. Old asynchronous loads cannot replace a
  newer document; retry restores keyboard focus to the actual open document.
- Pair sprites reused different bodies and variants, could group non-adults,
  and shifted flipped bodies. Cache identity now includes both complete
  bodies, sex and variation; grouping requires reciprocal nearby stationary
  adults. Existing rigs, poses, cache, particles, walking and camera controls
  remain. Snapshot updates refresh bodies; reseeds discard stale identities
  and camera targets. Mirror snapshots reuse unchanged terrain without
  serializing it on every animation frame.
- EDEN night lights used obsolete window and pool coordinates. They now
  follow the actual buildings and pool, using the existing palette.
- The legacy `infant_survival` value compared unmatched cohorts. Its display
  now says YEARLINGS / PRIOR BIRTHS, explains the limitation, and removes
  unsupported survival thresholds. The serialized field is retained. A person without territory is no longer
  falsely described as proof that every box is currently full.
- Food migration, seasonal gathering, unworked fields, carried food and
  predator encounters had accounting errors. They now conserve the intended
  resources and exclude people already killed. Carried berries are no longer
  labelled as carcasses. Names follow the child's sex and remain persistent;
  both worlds retain the owner's eight founding pairs.
- Death and withdrawal left partners, rooms or roles pointing at people no
  longer eligible to hold them. Shared cleanup and migration repair these
  references, including plague, epidemic, feud and revenge paths. Immediate
  neonatal deaths count a birth and a death; miscarriages count neither.
- The restart path archived only part of a run and the historian could use
  the wrong data directory. Explicit genesis now archives state, events,
  postmortems and history books together under a unique directory. The
  historian respects `UNIVERSE69_DATA`; `run.sh` forwards `--genesis`.

## Verified

The fresh viewer evidence is in [final/](final/). All 223 checks at 390×844
and 207 checks each at 1024×768 and 1440×900 pass, with zero browser errors.
Screenshots are captured only after stable painted geometry and decoded
visible images. Checks include actual controls, keyboard focus, every reader
page, swipe and arrow navigation, errors/retry, camera rungs, drag, follow,
walking, combined expanded states, body visibility and helper regressions.
A separate agent reviewed the rendered screenshots and source; see
[independent-review.md](independent-review.md) for scope and final clearance.

### First-screen geometry

| Viewport | Masthead | World headings | Instruments | Record | Total chrome | Each scene |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 390×844 | 35 px | 55.5 px, stacked | 27 px | 54 px | 171.5 px / 20.32% | 335.25 px |
| 1024×768 | 35 px | 28 px, shared row | 109.375 px | 54 px | 226.375 px / 29.48% | 541.625 px |
| 1440×900 | 35 px | 28 px, shared row | 54.6875 px | 54 px | 171.6875 px / 19.08% | 728.3125 px |

The instruments wrap at 1024 because their values and labels remain readable;
the row reports actual world conditions. Both scenes remain the dominant
region and their main actions remain available. There is no document scroll,
unnecessary horizontal scroll, clipped reading page or overlapping region in
the exercised states. Mobile composition stacks the two worlds; wide views
compare them side by side, as the current house style requires.

[historical/](historical/) checks the already archived engine-2026.10.28.1
snapshot (year 175, EDEN 47 / LAGOON 373), with 234 passing phone checks and
218 at each wider viewport. It is compatibility evidence, not a measurement
from the new engine. All exercised states paint and preserve their content.

The current-engine day-3000 fixture (34 EDEN / 28 LAGOON) is in
[day-3000/](day-3000/), with 234 passing phone checks and 217 at each wider
viewport. Its real event record earns more space: total chrome is 228.5 px /
27.07%, 302.375 px / 39.37%, and 247.6875 px / 27.52%, respectively. Each scene
is 306.75, 465.625, and 652.3125 px high. Independent review confirms the
portrait, both worlds and record remain visible. The fixture comparison file
records why earlier populated captures were superseded after the death fixes.

[day-36000/](day-36000/) adds the current engine at year 100, with EDEN 614
and LAGOON 231. All 234 phone checks and 218 at each wider viewport pass.
Chrome and scene dimensions match the populated day-3000 table above; long
records are paged rather than allowed to consume the comparison.

The compact before/after geometry is largely unchanged: this audit repairs
expanded states and relationships rather than reducing every surface. Original
before evidence is retained in [before/](before/) and [before-ui/](before-ui/).
The original phone report's `combinedTop=428` incorrectly counted the first
scene as chrome; another early `combinedHeight=144` omitted the second
heading. The corrected before total is 172 px / 20.38%: 35 masthead + 56
headings + 27 instruments + 54 record. Use the element rectangles, not those
obsolete aggregate fields. Fresh-state content differs over time, so geometry
comparisons do not measure model outcomes.

[person-paged/](person-paged/) retains the worst-card reproduction and its
23 passing checks: 329 text characters survive five pages, none clip, the
body remains visible, page index survives repaint and snapshot refresh, and
reselecting does not duplicate arrow handling. The four diary labels are
explicitly synthetic UI stress applied to a real historical person; this is
not a claimed simulation event sequence. [person-stress/](person-stress/)
records the earlier failing geometry. The retained stress uses the earlier,
longer territory label; final copy is simply “no territory,” because
historical rooms can remain vacant.

[unittest.log](unittest.log): 209 tests pass under Python 3.14.6.
[python39-tests.log](python39-tests.log): the same 209 tests pass under
Apple Python 3.9.6, selected by the launcher on this workbench. [style.log](style.log): all 40
style tests pass after the final person-card changes, viewer JavaScript parses,
the shell launcher parses, and `web/index.html` equals `docs/index.html`.
After the full suites, fixture storage was made portable: external-volume
scratch here, an explicit override or normal temporary storage on other
machines. [fixture-routing-tests.log](fixture-routing-tests.log) records all
29 affected tests passing; [scratch-routing-branches.log](scratch-routing-branches.log)
checks all three path choices. This changes no model behavior.
The model was independently reviewed, including all death-removal routes.
Restart/archive behavior was also exercised against isolated scratch data
through the real HTTP server.

### Bounded model run

Seed 69, engine `2026.10.29.1`, Python 3.14.6 completed 60,000 days / 240,000
parts in 1,345.4 seconds on the workbench. [arc-60000.json](arc-60000.json)
retains the figures; [lab-60000.log.gz](lab-60000.log.gz) retains the complete
raw log byte-for-byte, compressed because its console layout has trailing
spaces. Both worlds remain in iteration 1 with no extinction or postmortem.

| World | Final population | Peak | Result |
| --- | ---: | ---: | --- |
| EDEN | 711 | 723 | 359 withdrawn; still in exploit phase |
| LAGOON | 435 | 439 | 13 technologies, 3 tribes, greater shore reached |

This arc does not demonstrate EDEN collapse or validate the literature.
The registry's 14 supported / 0 contradicted / 3 undecided values describe
its coded hypotheses, not scientific validation. The sink timing tests have
no applicable phase dates; the Dunbar test does not apply after lore.
[checkpoint-invariants.log](checkpoint-invariants.log) confirms identity,
bonds, clocks, rooms, roles, stores and annual census accounting on raw saves
at days 3,000, 36,000 and 60,000, without migration repairing the input.
The year-100 fixture was rendered; the final day-60,000 save was checked for
model invariants but was not another rendered visual set.

## Reproduction and provenance

Engine `2026.10.29.1` changes the trajectory of an existing run. Earlier
published figures are historical, not predictions from this release. Source and fixture hashes are in [provenance.json](provenance.json). Current
mechanisms and their research mapping are recorded in `DESIGN.md`; current
bounded-arc results and the pending MacBook restart are recorded in `STUDY.md`.

Run `python3 -m unittest discover -s tests`, then an isolated development
server with both `UNIVERSE69_DATA` and `UNIVERSE69_PORT` set. The visual
harness is `python3 tools/shoot.py http://127.0.0.1:6974/ --interact --out
/Volumes/Data/agent-scratch/u69-review --tag review`. Its browser runtime is a
development tool, not a simulation dependency. A saved snapshot may be passed
with `--fixture`; preserved HTML may be compared with `--source`. The
`fixtures/lab-day-3000.json` and `fixtures/lab-day-36000.json` files are
isolated workbench outputs from the reviewed engine, never live state. The
historical compatibility fixture is `web/archive/first-run-snapshot.json`.
Raw lab saves are retained under `fixtures/day-*/saved-world.json`; run
`python3 docs/audits/2026-10-29/fixtures/verify_checkpoints.py` to check their
invariants without migration concealing defects. `run_arc.py` reproduces the
bounded run and checkpoints on this engine, writing to the scratch directory
given as its sole optional argument. It has no wall-clock waiting or live data
access.

## Remaining

The 2016 MacBook, its live state, actual restart, old-machine performance,
vanity DNS and external deployment were not accessed or verified. No live
state is committed. The checks cover the documented states and stress cases,
not every possible future population, rare pose or viewport. Actual crowded
people can overlap inside a scene; island scale does not make every body
individually legible. True infant
cohort survival remains unimplemented. Night skies and terrain art retain
the limitations documented in `GRAPHICS.md`.
