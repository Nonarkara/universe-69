# Independent module review

Reviewer `/root/viewer_review` independently reviewed `sim/reproduction.py`
at the frozen SHA-256
`20c9c189cba51db418eaa000b3b6cd3b7b68c2f865436bbbb485fe182725e3cf`.
No remaining module blocker was found. This is implementation review, not
clinical calibration or validation of the human-population model.

## Units and evidence mapping

Against the primary-source excerpt retained in `research.md`, the lag mapping
is correctly oriented: `ovulation_day - exposed_day` of 5, 4, 3, 2, 1, 0 maps
to .04, .13, .08, .29, .27, .08. Outside those calendar bins the selected model
uses zero. The cycle chance is the maximum exposed-day benchmark, with the
modifier bounded to [0,1] before multiplying. It does not apply independent
product-of-failures trials, sum probabilities across acts, or silently boost
the reference benchmark. MAX is the stated unfitted approximation, not an
empirically established joint probability or a proven conservative bound.

The unit is a calendar day containing actual captured mutual contact. Repeated
parts or social tokens do not multiply that day's chance. Distinct captured
fathers remain as attribution candidates, capped at four per day; six retained
calendar bins bound the buffer at 24 records. These bins are not a strict
120-hour sperm-lifetime model. Same-part overflow is canonical by father ID;
earlier-part records occupy capacity first, as the stated bounded convention.

## State, randomness and causal boundary

Only current-part mate facts enter the buffer, with detached traits and a
living mother. The producer is the actual encounter-capture boundary; the
module does not infer contact from a current partner, action label or male
population. A father's later death, withdrawal, boarding or partnership change
cannot erase an already captured biological exposure. A removed/staged-dead
mother cannot advance to a new pregnancy.

The ovulation calendar day's night evaluates once. The evaluated day and next
cycle are recorded before the outcome coin, so failure, duplicate calls and
reload do not reopen that cycle. The engine ingests all current-part facts
before evaluation. Skipped dates schedule forward without inventing historical
trials. Phase, cycle length, conception outcome and attribution use separate
stable private RNG purposes; they do not consume the engine's global stream.

Attribution selects uniformly among retained records with the maximal chosen
benchmark. This is not necessarily equal probability per unique father: tied
benchmark days can contribute multiple records for one father. It remains
explicit bookkeeping, not a calibrated sperm-competition mechanism. Returned
traits are detached. The engine separately applies pregnancy and its existing
illustrative later-loss fate.

Migration adds no phase or contact history and uses no randomness. Lazy initial
phase is an explicit prior, not reconstructed menstrual history. Cycle intervals
24–35 are illustrative. Pending pregnancy clears future schedule/exposures
without changing gestation, frozen traits, paternity or cycle index. Unknown
paternity in old saves remains unknown. State is plain JSON and bounded.

## Independent checks and limits

Apple Python 3.9 passed all 20 module tests. The reviewer also updated and ran
18 engine reproductive-contact tests and 13 death-cleanup tests on Python 3.14
and Apple Python 3.9. They cover actual capture, daily duplication, failed-cycle
re-evaluation/reload, no ambient conception, living-mother and historical-father
semantics, actual paternity at birth, pregnancy/migration and retained casualty
claims. The module author's pure tests cover timing, capacity, pace/query
invariance and private RNG as additional evidence.

No clinical probabilities, demographic targets or seed outcomes were tuned by
this reviewer. The predeclared seed 7/25/69 bounded centuries remain separate
outcome evidence; this source review makes no survival, civilization, human
equivalence or MacBook-throughput claim. No live runtime state was accessed.
