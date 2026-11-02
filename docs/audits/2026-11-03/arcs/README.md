# Frozen century runs — engine2026.11.03.1

Predeclared seeds7/25/69, each36,000days /144,000parts /100 model years from
standard genesis: eight pairs, with the upstream mixed-age founding cohort.
All three standard `tools/lab.py` processes completed at the fixed horizon,
exit 0, with every recorded source hash unchanged before/after. No intervention,
rate adjustment, seed substitution or survivor selection. Logs, complete
standard arc/research/verdict JSON and provenance are retained per seed.

| Seed | EDEN end /peak | EDEN max maternal generation | LAGOON end /peak | LAGOON max maternal generation | LAGOON historical discoveries |
|---|---:|---:|---:|---:|---:|
|7|250 /255|6|26 /102|6|7|
|25|198 /229|6|64 /64|6|7|
|69|239 /240|7|21 /35|6|6|

Every world remains iteration1, with no extinction/postmortem/reseed in this
horizon. This does not guarantee survival later, establish viable mating cohorts,
or demonstrate a Calhoun collapse mechanism. LAGOON7 declines substantially from
its peak; positive final headcount must not hide that. The generation field is
maximum maternal generation reached historically, not the age structure or
number of living members in that generation.

No case reaches agriculture, domestication, granary, seacraft, healing,
metallurgy or writing. Historical discovery does not mean current competence:
LAGOON69 has no living aware/qualified predator-hunting holder despite the old
discovery label. Procedure counts, local assets and requested instruction are
in each arc. LAGOON69 carries the existing near-wipe lesson `preserve` without
an extinction; lessons are hypotheses, not proven remedies.

The standard lab output does not preserve full final-world snapshots or LAGOON
sex/age cohorts. Those are unverified here; do not infer long-term demographic
viability from totals or reconstruct raw state from a summary. The exact
historical .8 endpoint fixtures are separate and are not current-version worlds.

Wall elapsed seconds:7=6197.439;25=5334.614;69=5260.452, Python 3.14.6 on the
workbench, concurrent with tests and graphics work. These are not isolated CPU
benchmarks, MacBook timings or proof of sustained100 years/realday throughput.
The separate [runtime diagnostic](../runtime/README.md) uses a labelled older
workbench checkpoint and reports profiling overhead and limits.

## Reproduce

At the audited source revision, from the checkout:

```sh
python3 tools/lab.py --seed 7 --days 36000 --json seed-7.json
python3 tools/lab.py --seed 25 --days 36000 --json seed-25.json
python3 tools/lab.py --seed 69 --days 36000 --json seed-69.json
```

`run_lab.py` is the exact executed observation wrapper (recorded local repository
and scratch paths may need relocation). It adds no RNG calls or tick wrappers.
It hashes all simulation files and `tools/lab.py`, runs the standard lab once,
and records hashes again after terminal output. Engine/procedure/reproduction
code still matches those hashes in the shipped version.

Only **after all horizons completed**, the unused-by-lab `sim/server.py` received
a read-only `/fonts` delivery route. Its only changed AST scope is
`Handler.do_GET`; all other runtime AST is identical. This observer delivery
bridge is recorded in [server-delivery-proof.json](../server-delivery-proof.json).
The raw pre/post run manifests retain their actual original hashes; they were
not rewritten to hide that later delivery-only difference.

This version also incorporates upstream founding-cohort/island/quarrel changes
and the agency corrections. These arcs do not isolate a causal effect of fuzzy
sensitivity alone. Controlled matched-body tests establish narrower properties.
