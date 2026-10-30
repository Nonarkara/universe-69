# Encounter integration source review — 2026-10-30

Engine **2026.10.30.6**. No unresolved causal blocker found in the reviewed increment. This review covers completion, own decisions, paternity, grooming benefits, labour and their integration; it does not certify human cognition, consent, biology or demographic calibration.

The reviewer authored `encounters.py`; its unit cases are self-verification. The engine/needs/minds/labour integration was reviewed separately from those files' authors. No simulation source was changed during this final review.

## What was checked

- `encounters.propose` changes only the actor. Recipient scoring remains their own. Incoming invitations can reopen an awake nonurgent decision but cannot command acceptance, wake a sleeper, or replace urgent bodily care. Local candidates reject known direct parents/shared parents for mating, without inventing unknown genealogy. LAGOON accepts an existing reciprocal partner or two singles; EDEN contact does not assign permanent bonds.
- `capture` reads both participants at the **same instant**: reciprocal kind/session, matching current actions, own intended targets actually reached, living competent available adults for mating, adjacency and a direct dry segment with the water-corner rule. Separate endpoint observations cannot be stitched into a fictional encounter. Frames copy IDs and father traits and have canonical same-part identity.
- Both engine loops capture before decrement/reassignment. Thus a valid final part is not erased when someone immediately chooses a different next action. Ordinary casualties are removed before need satisfaction. Conception additionally resolves after EDEN's plague casualties; dead, withdrawn, incompetent or aboard endpoints cannot supply a pregnancy trial. Current action/target is deliberately not rechecked at commit, because the frozen frame is the completion fact.
- Conception is once per mother in the current engine part. Remote pair IDs/global male lists alone provide no trial. LAGOON singles acquire a reciprocal bond at actual completed contact; the former global automatic pairing and bilateral `couple_up`/`groom_with` paths are removed. Actual father ID and copied hereditary values are stored at conception. Birth keeps that father across later bond changes; pending-pregnancy father is cleared after delivery/loss. Legacy pregnancies retain their saved hereditary values with **unknown** father ID.
- The original mate utility could never enter the 85% choice band for EDEN postholders. A separate capped personal intimacy need now grows by `1/(7*4)` per adult part in both worlds and adds weight 1.5 under the existing hunger/energy/ennui factors. Only actual completed live contact satisfies it. Children do not accumulate it. This makes choice reachable without changing conception coefficients or forcing a recipient's choice.
- Watch selection and night camp gathering protect existing mate/groom actions. Groom proposals alone produce no active grooming benefit or knowledge-contact frame. Actual mutual grooming gives each participant at most +0.3 company per day, deduplicated across endpoint captures; ordinary TALK/proximity retain their existing, separate company abstraction.
- Labour preparation changes only the due mother at her actual dry position during the illustrative one-day lead; no teleport or assigned helper. Birth assistance is a separate local choice with bodily eligibility. Qualified healing additionally requires actual arrived awake nearby care. Delivery exits A_BIRTH to own REST, rather than leaving a permanent birth pose.
- New persistent fields `social`, `dad`, `pregnancy_father`, `groom_day` and `intimacy` have newborn/founder/migration defaults. New intent tokens/targets and contact facts are JSON data; copied tokens and traits avoid shared-container mutation. Migration preserves existing data rather than fabricating historical encounters.

## Verification

Apple `/usr/bin/python3` (3.9) focused run:

```text
PYTHONPATH=tests /usr/bin/python3 -m unittest test_encounters test_reproductive_contact test_social_choices test_labor
Ran 49 tests in 1.545s — OK
```

These are meaningful deterministic gate/mechanism fixtures, including rejected remote/asleep/aboard/ghost/one-way/wrong-session/wrong-target/water-corner contact; independent refusal and postholder reachability; copied father values; actual-parent birth inheritance after a bond change; legacy unknown paternity; daily grooming bounds; intimacy units; mother-only labour and independent care. They include controlled state and mocked terrain/coins where required; they are not a natural population forecast. Full-suite, natural arc, runtime portability and visual evidence are recorded separately by their owners.

## Limits and consequences

- Engine edits change the live trajectory. Earlier ambient conception allowed births without completed contact; its population figures do not validate this increment. Existing coefficients now mean a **contact-conditional per-part probability**, not a fitted probability per intercourse. No increase was made to produce survival or a desired population.
- No ovulation cycle, sperm persistence, fertile window, sex-specific desire calibration, validated reproductive act duration or full genetics. Seven-day need growth, weight 1.5, body eligibility, contact geometry, grooming reward and labour lead are explicit illustrative model choices.
- Sexual and relationship choices remain a finite utility model with a binary sex schema and existing age gates, not validated consent or human cognition. Known-family avoidance can only use recorded parents; legacy unknown fathers remain unknown. LAGOON bonding remains a simplified reciprocal relationship rule.
- Voyagers still skip ordinary physiology while aboard (pre-existing abstraction). Labour helpers do not receive competence merely by attending; local supplies and medical expertise remain separate mechanisms. Ordinary TALK/proximity can restore company without formal grooming.
- Captured contact and a person's next current pose are different facts. The observer must use authoritative reciprocal contact metadata to draw a sexual pair; permanent partner IDs and one-sided invitations are insufficient. The separate UI reviewer owns rendered proof.

## Exact reviewed source SHA-256

| File | SHA-256 |
|---|---|
| `sim/engine.py` | `6be8721ef0c7079295b1ea7d13ead43e92f8cbcfce442aa62ee7dcc61bba3db8` |
| `sim/needs.py` | `1d9f69de0b20b71710d529e91d52b2c6e339bc63f48c716f7b9f007e781db6a5` |
| `sim/minds.py` | `c41994125a0ccfad8ae025ae38452179e8640362aa88263659eb983a2f8c04f8` |
| `sim/encounters.py` | `913e361567a682618c20f8a887eefc695eb77af6ad428591843080141eea4394` |
| `sim/labor.py` | `3f05c805ba8d2e0e113e079709909a5f34f40a066dc3df6b3b587983cb36c1be` |
| `sim/skills.py` | `5588dad50dd1a925d30a08bb35907cc7cc6c6dc23ab31ca58597aa6eddd74555` |
| `sim/learning.py` | `b83ddb2818f8e4675eaebc7f0f38526d08aa4ad06e595ef075f1464bad99a5ff` |
| `sim/animals.py` | `5622b0910d185da4e9c8b6f680ce87a1feada111fb5505b483bd3de563864577` |
| `sim/research.py` | `a0afcd7055afa28777f4c8721a7d5b1fbd70c9c5bbae198f5eae03d4bdca54e4` |
| `sim/historian.py` | `ad0728651b5f6b326fc02cc05ab2c112dfe34506e1ba1af81dacfa3541f30c69` |
| `sim/server.py` | `5e1bfe65ed3a37e8695c190bc8764fe98d6986108c877fead8c4bbf87cf44f4d` |
