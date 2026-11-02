# EDEN own-choice causal diagnostic

Baseline engine 2026.10.30.7, main 638eb48. **A biography pair pointer changes EDEN free-mating utility even when the body, candidate, needs and RNG are identical.** This can exclude an otherwise eligible option from the 85% choice band. It is not a universal penalty, proof of sterility, or a demographic forecast.

## Actual production-call counterfactual

`paired_choice.py` calls unchanged `needs.assign`, with no engine tick, conception call or probability modification. A trace hook only copies the already calculated local options at function return. Each pair uses the same RNG seed 0 and exactly the same actor/peer fields except reciprocal `p` biography pointers. Both cases use an available adult opposite-sex local peer. The controlled actors are generation 2, 25 years old, competent, awake, fed, rested, company-sated, not withdrawn/aboard, with identical intimacy and purpose. The occupied post is an explicit controlled condition, not an assertion about every natural descendant.

The script asserts identical candidates/RNG and matched starting bodies, and saves complete before/after actor and peer records. The peer is unchanged by every actual assignment.

Let C=company need, I=intimacy need, H=food urgency, E=energy, P=purpose. Current source uses:

```text
B = (.3 + .3*C + 1.5*I) * (1-.85*H) * (.4+.6*E)
paired EDEN mate utility   = B
unpaired EDEN mate utility = B * (.4+P) * max(.2,1-ennui)
post utility              = (.9+.6*P) * (1-.9*H)
choice eligibility        = utility >= .85 * maximum option utility
```

For the main matched point C=H=0,E=1,I=.5,P=.3,ennui=0: B=1.05, post=1.08, band floor=.918. Changing only the biography pointers changes utility from 1.05 to .735. The actual paired actor selects MATE; the actual unpaired actor selects WORK.

| Controlled case | Paired utility/action | Unpaired utility/action | Meaning |
|---|---|---|---|
|P=.3,I=.5,post|1.05 /MATE|.735 /WORK|Unpaired option falls outside the same .918 band.|
|P=.6,I=.6,post|1.20 /MATE|1.20 /MATE|Multiplier-neutral control; identical choice.|
|P=1,I=.5,post|1.05 /WORK|1.47 /MATE|Effect reverses at high purpose; not an always-unpaired penalty.|
|P=.6,I=.6,ennui=.5,post|1.20 /MATE|.60 /WORK|The world ennui factor affects only the unpaired branch.|
|P=.3,I=.5,no post|1.05 /MATE|.735 /MATE|Lower utility is not itself guaranteed exclusion or sterility.|

Food and rest are zero at the primary matched body's fed/rested daytime point; company options are not added because company need is zero. There is no hidden candidate failure. Randomness breaks only the existing near-tie; it cannot rescue an option below the 85% band.

## Separate findings, not bundled explanations

- **Male age gate:** `needs.assign` restricts the initiating actor to 16..45, and `_social_person` filters all mate candidates at 45 regardless of sex. Actual controlled age 45/46 tests show both `encounters.available` predicates remain true, yet the older male loses the mate option as initiator and as a female actor's candidate. This is separate from the pair-pointer branch, and from the female reproductive-cycle age limit. No age-policy fix was made here.
- **Care interruption:** `care_paths.py` calls actual `labor.prepare` and `keep_watch` on a controlled real camp. A currently arrived A_TEND fire expert is selected as A_WATCH. With a different guard selected at night, the gathering loop leaves the caregiver A_TEND but moves the target away from the patient. It also leaves an actually prepared mother A_BIRTH while moving her target away from her actual labour position. These are watch-selection and target-overwrite paths, not evidence about mating probabilities. Full before/after records are retained. No production fix was made here.
- Candidate filters such as competency, direct known family, distance, sleep, thirst, injury and current care can separately remove an option. The matched pair-pointer experiment deliberately holds those conditions equal and eligible; it does not attribute all natural low encounter frequency to the pointer branch.

## Causally narrow next step

If EDEN is free of bond-based mating restrictions, give both biography states the **same EDEN utility policy**. Retaining or revising purpose/ennui factors should be justified as one mechanism applied consistently, not selected from resulting birth counts. Keep actual local eligibility, independent recipient choice, real reciprocal completion and the entire reproductive timing/probability pipeline intact. Address male-age policy and care/target protection in separate changes/tests.

## Evidence and limits

- `paired_choice.json`: source hashes, actual option scores/band, outcomes and complete detached before/after records.
- `care_paths.json`: actual call order and state changes for separate care/watch probes.
- Both runners/logs are retained beside this report; all simulation sources were unchanged during their executions. No long-lived or natural simulation was run, no live data accessed, and no pregnancy trial invoked.
- These controlled feasible states prove the local source dependency. Their prevalence or demographic impact in a natural run is unmeasured here. Current clinical probabilities were not tuned or evaluated by this diagnostic.

## Exact unchanged simulation source SHA-256

| File | SHA-256 |
|---|---|
| `sim/minds.py` | `95965b717e4e72fa45a79b48c8b5a00904b416406ce0b6e905bcab882c481d0a` |
| `sim/server.py` | `5e1bfe65ed3a37e8695c190bc8764fe98d6986108c877fead8c4bbf87cf44f4d` |
| `sim/skills.py` | `5588dad50dd1a925d30a08bb35907cc7cc6c6dc23ab31ca58597aa6eddd74555` |
| `sim/research.py` | `a0afcd7055afa28777f4c8721a7d5b1fbd70c9c5bbae198f5eae03d4bdca54e4` |
| `sim/needs.py` | `1d9f69de0b20b71710d529e91d52b2c6e339bc63f48c716f7b9f007e781db6a5` |
| `sim/reproduction.py` | `20c9c189cba51db418eaa000b3b6cd3b7b68c2f865436bbbb485fe182725e3cf` |
| `sim/historian.py` | `ad0728651b5f6b326fc02cc05ab2c112dfe34506e1ba1af81dacfa3541f30c69` |
| `sim/engine.py` | `53415944ef4d5af155462f7af4217053319868a2f6e1abc4cfa952af16b8ee53` |
| `sim/labor.py` | `3f05c805ba8d2e0e113e079709909a5f34f40a066dc3df6b3b587983cb36c1be` |
| `sim/animals.py` | `5622b0910d185da4e9c8b6f680ce87a1feada111fb5505b483bd3de563864577` |
| `sim/learning.py` | `b83ddb2818f8e4675eaebc7f0f38526d08aa4ad06e595ef075f1464bad99a5ff` |
| `sim/encounters.py` | `913e361567a682618c20f8a887eefc695eb77af6ad428591843080141eea4394` |
