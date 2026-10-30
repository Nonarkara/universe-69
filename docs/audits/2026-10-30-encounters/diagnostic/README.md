# Bounded social-choice diagnostic

`contacts-10yr.json` and `trace_contacts.py` retain the exact reviewer replay:
EDEN only, seed 69, 3,600 model days / 14,400 parts. It uses the engine's same
per-part RNG seed law. It is neither the full two-world experiment, the final
100-year bake, nor the MacBook's live runtime. Four touched source-file hashes
were recorded before and after and stayed identical. The final release's full
model manifest is separate. `manifest.json` hashes these retained artifacts.

The ten-year replay records 666 new proposals, 1,012 mating choices, 1,061
arrived capture attempts and 357 raw mate frames. Deduplication yields **260
completed mutual contacts and 260 eligible conception trials**. Failed arrived
attempts include 628 peers not yet reciprocating and 76 peers still travelling;
there were no token mismatches or other capture failures. The existing
probabilities sum to 0.3571916666666662 across those trials. There were zero
pregnancies; population remained 16 and no child had been named.

This establishes that the new independent handshake is reachable: invitations
are accepted and actual meetings complete. Zero pregnancies here does not
establish structural sterility. The previous ambient per-part conception
coefficient now applies only at a much sparser actual encounter and is not a
calibrated per-encounter probability. Time basis, sperm persistence and fertile
windows remain future biology work; neither desire nor fertility was increased
to force a child into this diagnostic.

The older first-child naming test required seed 69 to produce a birth within
2,000 days under the former unconditional pregnancy process. It now explicitly
stages an existing non-miscarried pregnancy and verifies an actual successful
birth creates exactly one child, sets `named`, and emits that child's first-name
event. This preserves the naming assertion without treating that arbitrary
natural birth deadline as a calibrated demographic requirement. The independent
encounter and conception tests separately pin physical reproduction eligibility.

`social-red.log` runs the 17 new social-choice cases against the prior HEAD's
needs module: 11 assertion failures and 6 errors. `social-focused.log` records
60 passing social-choice, procedural-world and instruction cases after the
implementation. These bounded results are not the final full-suite outcome.

The exact runner preserves its original workbench checkout and scratch output
paths. Reproduction on another checkout requires adapting those two paths;
create the named scratch directory before execution. Instrumentation wraps the
real functions, records their outcomes, and adds no simulation randomness.
