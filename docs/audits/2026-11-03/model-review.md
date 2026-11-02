# Independent model review — personal need responses

Reviewed engine2026.11.03.1 on2026-11-03. Read-only review: no model/UI/test implementation edits by this reviewer. **No blocking defect found in the reviewed increment.** This is mathematical and bounded behavior verification, not human calibration or a population-outcome claim.

## Mathematical check

For midpoint m∈[.44,.56], the intended memberships are left shoulder max(0,1−x/m), centre x/m for x≤m or(1−x)/(1−m) otherwise, and right shoulder max(0,(x−m)/(1−m)). On clamped x∈[0,1] exactly two adjacent memberships sum to1; endpoints have one membership1. Singleton consequents0,.5,1 therefore yield the implemented piecewise formula.

The slopes .5/m and .5/(1−m) are positive (between .892857 and1.136364); both branches meet at(m,.5), with endpoints(0,0)/(1,1). Difference from identity is linear on each side and zero at endpoints, so its absolute maximum is |.5−m|≤.06, attained at m. This bound is on each response grade, **not** on downstream utility, action frequency, population or probability. Midpoint.5 reproduces the identity curve exactly. Clamping preserves bounds for finite deficits.

## Identity and state

SHA256 input is explicit JSON[fseed-or-seed,iteration,person-id,need], not process-randomized hash. `engine.genesis` supplies the same fseed to both worlds while retaining different world RNG seeds; matching founder IDs therefore share profiles. Kind, current hunger/body, inherited traits and partner pointer do not enter the profile. Reseeds change iteration, intentionally changing profiles. Legacy defaults match migration conventions. These are stable illustrative preferences, neither genes nor fitted psychological measurements.

`drives` writes no dictionaries, consumes no RNG and adds no saved fields/schema. The same JSON identity survives save/reload. This does not mean trajectories or subsequent RNG consumption are unchanged: changing chosen actions changes later behavior. Version2026.11.03.1 explicitly acknowledges that model change.

## Integration and protected decisions

- Personal food uses transformed own hunger; camp shortage raises collection demand via `want_food=max(body_food,.75*larder_short)`. EAT uses `body_food`, so an empty camp does not directly fabricate hunger in a fed actor. Existing comfort eating remains a separate EDEN hypothesis.
- Food/rest/company/intimacy use the same response mechanism in both worlds. Final scoring and the85% near-tie band remain discrete: profiles can change band membership or the winning action. No continuous-action or probabilistic calibration claim follows.
- Finished self-actions are cleared only when ad≤0 and already at target; birth and withdrawal remain continuing states. Ongoing peer sleep is never cleared or woken. Completed own sleep can stop vetoing a fresh social decision. Raw encounter hunger/thirst/injury/energy/minor guards remain outside fuzzy scoring.
- Own bond pointer no longer selects a different personal-purpose multiplier. The existing EDEN ennui modifier applies consistently to both bond states; local compatibility and reciprocal choices still control contact. Its value remains illustrative.
- Older adult behavior no longer ends categorically at45. The existing female clinical16–45 conception gate remains separate; no male fertility, menopause or older-adult frequency was fitted. Adult-only renderer gates are outside this unchanged UI scope.
- Watch gathering preserves explicit bodily, care, work and instruction targets; caregiver/instruction holders are excluded from guard selection. Actual lit-hearth arrived TALK still permits stories.

**Scope limit:** background guard selection remains a pre-existing camp routine, not a fully independent watch utility choice. An otherwise eligible awake worker can still be selected as guard. The repair protects care/instruction/bodily exclusions and gathering targets; it should not be described as eliminating every external watch assignment. This was reported to the parent, not silently broadened into a model edit.

## Executed verification

Apple `/usr/bin/python3`3.9.6, four focused suites, **28/28 passed**:

- `test_drives.py`:5tests,1.297s — endpoints, bounded monotonic samples, continuity, midpoint, cross-world matching, identity/iteration distinction, legacy defaults, JSON and RNG/state preservation.
- `test_fuzzy_choices.py`:3tests,.014s — repeatable differing close choices plus64identity extreme-hunger and extreme-fatigue checks.
- `test_choice_readiness.py`:13tests,.771s — actual dawn/nap completion, unchanged sleeping peer, food/rest priorities, same-body bond invariance grid, older behavior with unchanged clinical gate, minors/urgency, completed care/social stints, birth/withdrawal.
- `test_watch_agency.py`:7tests,2.230s — prepared labour, caregivers, explicit actions/meeting goals, preserved camp convergence/story conditions and actual independently chosen helper.

Logs and before/after source manifests are in workbench scratch `/Volumes/Data/agent-scratch/u69-nov3-baseline/{model-focused.log,review-before.json,review-after.json}`. All seven reviewed file hashes matched before and after these checks. The earlier full Apple suite was interrupted at parent request, exit130, after sources changed during execution; it is **not** a passing baseline or a final frozen-suite result. The parent owns final frozen full suites/labs. No survival target, probability or fertility coefficient was changed by this review.

## Exact reviewed SHA256

- `sim/drives.py`: `070a521f8d57339d15f3d21c84259aa0dbdb8e7aeff866492050219ef1e4fe5e`
- `sim/needs.py`: `6f32bee2f03cfcf5792d7d515b42ddb4f11161d32bbbedfc413c778ff59645a9`
- `sim/engine.py`: `1ec2e88db8edd3e4256e73771c843886675781b6ce1e4078b031403a6ac927fc`
- `tests/test_drives.py`: `590a399bb8f0e07faf49ff54b2b7e1c9a76ecdf06fc9d922acaaeb39355fa9ec`
- `tests/test_fuzzy_choices.py`: `e098a18d84878048ce8fca083433276ecc535540b031eeeeb7c03ff08a639d45`
- `tests/test_choice_readiness.py`: `b2123dabc2e6e0923e8701faaea60187fe897a9c1a7af02d5dbea81b601bff19`
- `tests/test_watch_agency.py`: `c42af4223a79b669f9538d18f15f513781b1784eb3034a70c28be5e0e3aa48d7`

## Independent replacement-test review

The replaced `TestDayAndNight.test_a_person_keeps_the_same_job_for_the_length_of_a_day` formerly sampled population action labels after60days, then required no more than one quarter to differ a day later. That mixes voluntary choices, nightly sleep and bodily interruptions with stint-duration correctness; there is no implementation or empirical guarantee for its25% threshold.

The replacement directly uses `_duration(A_FORAGE, ...)` with7days and asserts28parts, then executes the real night/dawn functions and checks the saved forage action, target and remaining commitment restored exactly. It would fail a missing day-to-part conversion or lost night/dawn job restoration. It is a meaningful narrower regression, not a raised population threshold or forced favorable behavior. It does not alone prove28engine countdown ticks; no such broader coverage is claimed. Existing interaction, urgent-body and actual-helper checks remain separate.

The single replacement case passed on Apple Python3.9.6. Reviewed `tests/test_engine.py` SHA256: `f57bce5dbfc6ad25632d1d55960894ff2d8a93980dec93320464c202338b4c24`. No production source was changed for this review.
