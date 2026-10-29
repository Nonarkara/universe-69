# Personal resource experience — engine 2026.10.30.2

The task is to make individual experience affect a person's next physical
choice, while preserving honest observation and finite supplies. The complete
digital-human objective remains active; this increment is not general cognition.

## Found

The former nearest-site helper consulted exact current stock at every reachable
patch. Party following, farms and urgent water seeking could bypass any local
knowledge. Away workers also read current camp supplies instantly. Resource-use
return values could omit a successful on-site meal or drink when nothing was
carried home. The fight-score adapter passed years to a day-based maturation
function. Milk-food lacked milk-water's proximity constraint, and milk could
cross a narrow strait.

## Changed

People retain at most 24 resource notes and 12 actual visited positions. Nearby
connected sites enter perception within 6 tiles. Distant notes remain stale;
planning balances remembered quantity and distance. Estimates move toward an
uncertain prior rather than revealing regrowth. Empty remembered sources can
be checked again after 7 days. Hungry/thirsty people can scout reachable local
dry terrain without knowing where unseen resources are. Farm tending remains
possible at an empty known field, and party following cannot reveal an unseen
site. Away camp inventory is a remembered observation.

Actual source depletion records food eaten and carried, and water drunk and
fetched; consuming an old load or a camp reserve is not credited to a source.
These realized-use fields are audit evidence, not learned skills/action values.
Maturation units and physical maternal proximity/connected land are corrected.
Newborn and reseeded memories start empty, migration adds independent defaults,
and JSON reload preserves subsequent behavior. EDEN receives no new assistance;
its future fights/nursing can change because the old bugs are corrected.

All numerical memory/sight/decay choices are illustrative. Primary modern human
experiments support qualitative location/outcome-guided search, not these
coefficients or population forecasts (RESEARCH.md).

## Verification

All 268 tests pass on Apple Python 3.9.6 in 227.804 seconds. Independent
source review passed all 22 new causal tests and checked the six final
model/lab hashes. The final century experiment completed in 604.9 seconds on Python 3.14.6;
`results.json` and `arc-36000.json` retain the data. At year 100 EDEN had 456
people (peak 525) and LAGOON 36 (peak 36), both generation 6. No human-universe
extinction/reseed occurred; LAGOON reached six technologies and one existing
model lesson. These are combined-release results, not an isolated memory
benefit or a human forecast.

- `focused-tests.log`: 60 focused tests, including 22 new causal resource,
  persistence, maturation and nursing cases, pass before the final full run.
- `maturity-red.log` and `nursing-red.log` retain failed pre-fix regressions.
- `eden-before.sha`, `eden-after.sha` and `compare_eden.py` compare canonical
  EDEN at 120 days, omitting experience/version/cache metadata. This initial
  phase matches; it does not claim that later crowded EDEN stays unchanged.
- `bake-inputs.json` fixes the model source hashes, seed 69, Python version
  and 36,000-day horizon of the final century experiment. Final results must
  match those hashes. No live state was read or restarted.
- `superseded-before-maturity-fix/` retains interrupted pre-correction checks.
  They were deliberately stopped because the source needed a behavior fix,
  not because observation timed out. There is no completed century outcome
  from that run. The first strait-test failure is retained separately; its
  old no-destination expectation was updated to permit a connected scout
  while continuing to prove no remote food/water grant.

Rendering files are unchanged; this model pass makes no new visual-pass claim.
Viewer contract/style tests cover preservation alongside the existing evidence.

## Remaining

Knowledge of technology remains world-shared, rather than transmitted between
individuals. Hunting initiation uses sight 6; existing 12-tile active pursuit
remains a separate approximation. Terrain routing still uses the engine's map.
There are no learned general action values, harvesting-skill growth, broad
relationship beliefs, explicit long-range planning, genome or validated human
cognition. The technology ladder still ends at writing. A century per real day
is a target pace; sustained 2016 MacBook throughput remains unverified.

Next work should transmit person-held knowledge through actual contact, with
provenance and stale/fallible claims, then extend personal memory to social
experience and planning. Preserve EDEN's controlled reset and re-derive every
version's outcomes rather than guaranteeing civilization or survival.
