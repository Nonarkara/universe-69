# Audit of the unfinished four-part day and viewer

The viewer's task is to watch and compare the people in two sealed worlds,
then inspect their record or the hypotheses behind the model. The worlds
are the first reading priority; their identity, time and population are
second; activity, conditions and the event record are third. In Research,
the title and verdict orient the reader, the claim leads, then its value,
threshold and source explain it.

## Found and changed

- At 390 px the worlds stacked vertically, breaking the simultaneous
  comparison. They now stay side by side at every tested width, with aligned
  headings above the scenes. The headings no longer obscure inhabitants.
- Establishing shots cropped the population around an empty midpoint; close
  shots held a position after their subjects moved away. Establishing shots
  now fit population bounds to the aspect; close shots track their subjects.
- Research had two independent scroll areas, small test text under a larger
  story, an inert CLOSE button and incorrect contradiction sorting. It now
  has one reading scroll, Model tests / The books views, explicit verdicts,
  16 px claims and prose capped at 65 characters. Dialog keyboard focus stays
  inside, Escape closes it, and focus returns to its trigger. Snapshot text
  is escaped before entering the new Research markup.
- A shared `.world` selector split event metadata into separate flex rows.
  Universe geometry is now scoped to `#worlds > .world`.
- Both the compact and expanded record reserved empty lines. They now grow
  only with their contents, capped at four/five lines or 42% of the viewport
  when expanded. Expanding an empty record no longer takes 42% of the screen.
- The combined-pair draft falsely grouped unrelated people, reused appearance,
  displaced flipped images and erased body differences. It was withdrawn;
  individual body sprites, the pose solver, sprite cache, camera controls,
  particles, population trends and event record are preserved.
- Activity captions stay inside the scene. Walk annotations wrap condition
  text and only occupy positions where their complete text fits.

## Evidence

`before-*.png` are the original unfinished worktree, not the previous Git
commit. Before chrome heights below were measured from screenshot pixel
bands; after measurements come from browser DOM rectangles in the JSON
reports. Real content varies over time, so these compare geometry, not
population outcomes.

| Before viewport | Masthead | Bottom record | Comparison |
| --- | --- | --- | --- |
| 390 × 844 | 44 px / 5.2% | 105 px / 12.4% | Stacked |
| 1024 × 768 | 33 px / 4.3% | 123 px / 16.0% | Side by side |
| 1440 × 900 | 33 px / 3.7% | 123 px / 13.7% | Side by side |

The masthead's larger targets and readable instructions earn their extra
height. HUDs reserve space for identity, clock, population, activity and
conditions; their height follows the real text. The comparison aligns both
headings to keep the scene horizons aligned. The record shrinks when empty
and expands only for actual events. No fit relies on reduced text size,
hidden document overflow or a new nested reading scroll.

After geometry and validation results are recorded alongside this document.

## Runtime findings

Engine `2026.10.28.1` changes the trajectory of the live run. It ships the
four-part day, night behavior and predator hunting from the unfinished work,
with corrections to daily rates, meat conservation, boat work units, legacy
clock migration, empty-world advancement, reseed counters and provenance.
The default pace is three real seconds per part, twelve per simulated day.
Migration catches up unsimulated time at the new pace without replaying
completed calendar days. Historical study figures are explicitly stale.

Research reads the worlds and records results separately. Numeric thresholds
are model choices inspired by the books, not empirical validation of claims
about humans. Saved counts can span iterations and engine versions; new
history entries include both.

## Remaining limits

The actual 2016 MacBook and its live state were not accessed or restarted.
The viewport evidence uses Chrome on the workbench, fresh development state,
and a separate engine-generated early-history fixture, never live `data/`.
Very crowded late-run geometry, old-Mac performance, all rare activity poses
and a new live deployment remain unverified. GRAPHICS.md retains the known
crowd occlusion, night-art, firelight and figure-animation limitations.

## Final viewport measurements

| Viewport | Masthead | World HUD | Combined top | Record | Scene height |
| --- | --- | --- | --- | --- | --- |
| 390 × 844 | 70.8 px / 8.4% | 137.3 px | 208.1 px / 24.7% | 116.0 px / 13.7% | 519.9 px |
| 1024 × 768 | 39.0 px / 5.1% | 96.0 px | 135.0 px / 17.6% | 78.0 px / 10.2% | 555.0 px |
| 1440 × 900 | 39.0 px / 4.3% | 102.0 px | 141.0 px / 15.7% | 78.0 px / 8.7% | 681.0 px |

Empty-state checks measured the record at 62/60/60 px instead of the original 105/123/123 px. The latest live screenshots above contain emergent events, so their footer heights grow with that real content. The scenes remain aligned with inhabitants visible and all primary controls in the same first screen. Research and the full event history earn scrolling; each has a single reading surface. No horizontal document overflow was measured.

**Verified:** 32 browser checks per viewport on both fresh live development state and an engine-derived seed-69, 3,000-day fixture: 192 checks, zero reported failures or browser exceptions. The fixture has 10 EDEN inhabitants, 8 LAGOON inhabitants and 10 recorded events; these are test content, not live observations. Screenshots cover worlds, Research tests, books, expanded record, follow cards, help and failure/retry. Camera zoom, follow, walk, filters, modal Tab/Escape/focus and recovery were exercised. An additional age-boundary check verifies that 17-year-olds and unknown ages cannot share adult-detail sprite cache entries.

Reports: [fresh state](final-report.json), [populated fixture](populated-report.json). Screenshots are named by viewport and state.

Independent review covered all seven screenshot states at all three widths,
plus the populated fixture. It found no remaining MSH failures in those
tested states and no blocking Python/security findings. Late-run crowds and
the instrument remain outside that verified scope.

## Reproduce the viewer checks

Use a development server with `UNIVERSE69_PORT=6973` and `UNIVERSE69_DATA`
under `/Volumes/Data/agent-scratch`, then run:

```sh
python3 tools/shoot.py http://127.0.0.1:6973/ --interact \
  --out /Volumes/Data/agent-scratch/u69-audit/verified-final --tag final
```

To regenerate the populated fixture from this commit, run from the repository:

```python
import json, sys
from pathlib import Path
sys.path.insert(0, 'sim')
import engine, research
world = engine.genesis(seed=69)
events = []
for _ in range(3000 * engine.PARTS_PER_DAY):
    engine.tick_world(world, events)
research.record(world, research.evaluate(world))
snap = engine.summarize(world)
snap['events'] = [dict(d=d, y=d//engine.DAYS_PER_YEAR, u=u, t=t, msg=m)
                  for d, u, t, m in events[-500:]]
snap['research'] = research.report(world)
snap['status'] = dict(catching_up=False, behind_days=0)
lag = world['lagoon']
terrain = engine.make_lagoon_terrain(lag.get('terrain_seed', lag['seed']))
view = dict(eden_size=engine.EDEN_SIZE, lagoon_size=engine.LAGOON_SIZE,
            lagoon_iter=lag['iteration'], terrain=terrain)
out = Path('/Volumes/Data/agent-scratch/u69-audit/populated-fixture.json')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(dict(state=snap, world=view)))
```

Pass that file to the same command with `--fixture` to reproduce the populated
checks. The fixture is test material and is deliberately kept out of `data/`.

## Bounded model arc

`python3 tools/lab.py --days 60000 --every 3600 --json arc-60000.json --quiet`
completed with seed 69, engine `2026.10.28.1`, in 1,118.1 seconds on this
workbench while the suite also ran. The actual arc and byte-preserved raw log (losslessly compressed) are retained
in [arc-60000.json](arc-60000.json) and [lab-60000.log.gz](lab-60000.log.gz).

At day 60,000 (year 166), EDEN had 926 inhabitants, a peak of 1,802, and was
in its death phase. It had **not emptied** or reseeded: this bounded run does
not establish an extinction cycle. LAGOON had 463 inhabitants, peak 470,
iteration 2, thirteen technologies, two tribes, and one postmortem; its
survivors reached the mainland. These are fresh model measurements, not
claims about human populations.

The raw research output marked two contradictions. EDEN's post occupancy was
89.7%, below the chosen 99% threshold; that remains a failed model check.
The second was a reporting defect: the no-lore settlement-size hypothesis was
still tested after lore existed. The observer's applicability check was
corrected after this trajectory run, with a focused regression. The raw
arc/log remain unchanged so that correction is visible; it does not change
the engine or require pretending that the trajectory was run again.

The separate [observer correction](research-applicability-correction.json)
records the terminal technology facts and the revised applicability result:
15 supported checks, one contradicted, one undecided because its condition no
longer applies. These labels describe this implementation's chosen tests.


## Final validation

- The frozen engine suite passed all 104 tests in 1,505.270 seconds. Two new
  lab-report cases and two new research-applicability cases also passed;
  108 distinct Python cases were checked. The updated research suite passed
  all 21 cases and the lab-report suite both cases.
- Both browser evidence sets passed 32 checks at each of three widths:
  192 checks, zero final failures or browser exceptions. ALL now restores
  every world and event kind; its reset and highlights were independently
  verified for LIFE, WORLD and END.
- The 60,000-day arc completed. Its remaining failed post-occupancy hypothesis
  is retained rather than tuning the engine to pass it.
- Independent code/security and visual reviews found no blocking issues in
  tested states. JavaScript syntax, Python compilation, mirror equality and
  Git whitespace checks passed.
- MacBook deployment, late crowded rendering, rare poses and instrument
  performance were not verified. No live state was touched or committed.

Chrome cleanup stalled once after all browser assertions completed; that
scratch process was interrupted and the run repeated successfully. The
harness now writes its report before browser shutdown to preserve evidence.

Three additional targeted empty-record checks passed at the required widths.
Their screenshots (`empty-expanded-*.png`) and
[DOM measurements](empty-record-report.json) preserve the 62/60/60 px result
even after the live development instance accumulated events.
