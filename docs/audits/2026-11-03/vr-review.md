# Independent VR review — 2026-11-03

**Accepted for static desktop composition, recorded-state fidelity and native keyboard interaction at 390×844, 1024×768 and 1440×900. Production-cadence responsiveness/performance and Quest hardware remain unverified.** Applied anti-slop-design/MSH; this reviewer made no production renderer, model or test edits.

Task: compare both recorded terrariums, choose a viewpoint and read their context while preserving the inhabitants’ actual recorded state. Hierarchy: first the worlds, second world/time/population context, third viewpoint, hold and record choices.

## Found → changed

- The previous held view could invent movement/actions. Current motion only joins observed endpoints for explicit locomotion labels. Held/nonlocomotion states retain recorded coordinates/actions. LAGOON interpolation rejects water, missing terrain and blocked diagonal corners; unsupported chords snap to the observed endpoint rather than fabricate a detour.
- Same-iteration rewind reset people but could retain stale terrain. Iteration/day/part rewind now refetches the local world; exact terrain-content identity invalidates static terrain and dependent actor caches. Reused IDs cannot interpolate from another lineage; unchanged content retains caches.
- Age-dependent proportions were inconsistent in seated/lying poses and torso width. Canonical age tables now drive dimensions, torso width and connected fixed-length articulated limbs. Actual `bodyRadii` and lying-support helpers are used by rendering and regression tests. The skull/torso/limb support prevents large infant skulls intersecting the floor.
- Long repeated HUD context covered the phone lagoon. Default summaries now fit their content; explicit RECORD pages preserve full facts. Phone readout height falls from 207.531 to approximately73.6px (133.9px recovered); wide views 129.172→73.6px (55.6px recovered).
- Identical held polls falsely claimed a newer moment and spent another phone row. Model content is now separated from transport freshness; identical/wall-only reads create no pending update. Genuine changed/rewound records are staged, older-wall responses ignored and a return to held content clears obsolete pending state. The caption says an **updated record**, without asserting calendar advance.
- R during initial loading could enter a null-state path. Hold now requires a record. Open reading and visible keyboard focus are also exempt from the 14-second auto-dim timer; idle camera dimming remains.

## Verified

Independent Apple Python 3.9.6 run: **30/30 focused VR tests passed in 2.432s**. Actual Node helpers exercise dry/corner gates, action/held invariance, canonical age ratios, fixed limb lengths, body support, terrain fetch/cache reset, held update ordering, initial hold and idle-reading behavior. The reviewed source/test hashes match before and after. [Log](tests/independent/vr-focused.log), [before](tests/independent/vr-source-before.json), [after](tests/independent/vr-source-after.json).

Independently viewed the final table, inside-record focus and TABLE keyboard-record originals at all three widths (nine current images), alongside earlier full 18-image geometry/inside/held sets. No unresolved SH, clipped controls, horizontal scrolling or HUD/body overlap was found in these captured static compositions. The current screenshots visibly retain bright focus outlines and readable content; both worlds stay visible in TABLE, and inside-world subjects remain above the record.

The final capture report also records, at every width:

- Native R before the queued first packet leaves hold off; no initial-load error.
- After 16seconds, actual duplicate network deliveries increase (2→3 on phone,1→2 on wide views) while pending remains false.
- Open RECORD remains opacity 1 and `:focus-visible` true after another 16seconds without input.
- Native Tab reaches Next; Enter reaches page 2 and restores visible focus to Previous; Enter returns. All four TABLE pages work forward/back and retain the earned facts.
- Jost is loaded, viewport/body dimensions match, pager targets are approximately 32.875×34px; no page-error entries.
- 455 populated body instances have finite matrices and positive determinants; all 20 held actors retain exact recorded coordinates/actions.

Conservative top/bottom edge envelopes include margins and overlapping bands only once:

| Viewport | Top | Default bottom | Default total | Expanded TABLE record total |
|---|---:|---:|---:|---:|
|390×844|68px|83.56px|17.96%|27.48%|
|1024×768|103.14px|89.56px|25.09%|33.06%|
|1440×900|103.14px|89.56px|21.41%|28.21%|

Expanded space contains requested facts and paging choices, not reserved blank geometry. [Final report](vr/after/report.json), [phone focus](vr/after/390-record-focus.png), [tablet focus](vr/after/1024-record-focus.png), [desktop focus](vr/after/1440-record-focus.png), [verification](vr/verification.json).

## Exact provenance and remaining limits

Production VR mirrors: `9ec50254fa0f3e165d77ef7a48b24c01566ccee103c81e88bbab10de2d0f7684`.

Tests: `e21f3e04fac6d2ba6daceacf28c8e7809eb73e020dc43b6d6f3f07f73fd2dcd5`.

Capture-served HTML: `f84e937730755bd03f3f32be1232b41a8a4a228199d6a9f948ef6b4861e2c74b`.

I independently compared [served capture HTML](vr/after/capture-served.html) against production: the sole change replaces `renderer.setAnimationLoop(frame)` with `setInterval(frame,1000); frame()`. Root authorized this **harness-only 1 fps override**. Geometry, record and keyboard code are unchanged. This proves static rendering/native interaction at reduced cadence; it is not shipping-loop performance proof.

A production-cadence phone attempt rendered TABLE/EDEN/LAGOON/held but timed out dispatching RECORD. That failure is not a pass and has not been diagnosed away as external. **Production-cadence animation/interaction responsiveness remains unverified.** Quest session/controller behavior, headset comfort and full 3D planted-foot motion are also unverified. This is not unconditional VR release-readiness approval. The articulated rig is not the 2D planted-foot IK solver; its 9 tile/s observer smoothing is not physical speed or recovered subpart timing.

The unchanged public packet is engine 2026.11.01.1, EDEN 15/LAGOON 5 at global day 53460, fetched on Nov 3 with Nov 2 UTC packet wall. SHA256: `c4637d15ec6cc30b7304b24e59c6be9b69d838af74532563f774d2e50e6c2ec5`. It is a saved public projection, not a new-model run or live instrument proof; [public-record provenance](public-records/README.md) preserves the distinction. No simulation fields were staged or altered for these captures.

## Prepared font-delivery patch review

The parent’s static font-route patch is cleared by source review: allowlisted book/archive/fonts directories, font extensions restricted to WOFF2/text licenses, correct MIME, query stripping and realpath+separator containment. The actual-handler AST HTTP tests check exact five-asset bytes/types and reject missing, unlisted, traversal and escaped symlinks without importing/starting the simulation. This changes asset delivery, not model behavior; final application/server hashes and HTTP GREEN are parent-owned.
