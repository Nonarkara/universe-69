# Independent VR anatomy, motion and MSH review — second human round

Task: compare the sealed worlds, enter at human height and inspect people with ordinary male/female anatomy and legible recorded actions. Priority is world/inhabitant first, identity/time second, navigation and optional record third. This is a renderer review; no model rule, live world or runtime service was altered.

Reviewed final source SHA256 `d47dd0e3253acd5d2a34dd50674a82dc047f731884f5fb612d838dbf4451702a`. The implementer's retained production-loop packet contains TABLE/INSIDE at390×844,1024×768,1440×900; clinical adult front/side and seated studies; neutral age6 proportions; and eight adult walk samples. The clinical figures are explicitly age30 synthetic fixtures through actual Crowd.drawBody, not live people. The implementation used the unchanged renderer.setAnimationLoop(frame), with real Three.js geometry/matrices; no slowed substitute render loop or illustrative replacement image was used.

## Found, changed and verified

The old body was a shared rotational trunk, separated limbs and overly simple face. Initial source review identified that hipHalf never shaped the trunk, so scaling the shoulders did not create a female pelvis. The final mesh has distinct male/female/juvenile ring profiles, with rib cage, waist, hips and front/back depth. Hip roots now lie within the pelvic mass rather than outside it, and deltoid roots intersect the shoulder surface. Hands follow forearm orientation, with thumbs; ankles meet feet. In the inspected front/side/seated/walk studies, full heads, necks, trunks and limbs are present without detached lower bodies or foot gaps. Male/female forms are visibly distinct. The result remains recognizably stylized procedural figures, not scanned people or photoreal anatomy.

Adult external anatomy is neutral and nonsexual. Male shaft/scrotal forms attach to the pubic region; female external folds and nipples follow the torso surface. A prior floating nipple/attachment draft was repaired before this final packet. Front and side views were independently inspected; no detached nipple/pubic pieces were visible. Surface-proof.json records actual Three.js surface intersections for the adult female landmarks. This supports sampled attachment, not a claim of clinical anatomical precision.

The age/dress rules are explicit. Unknown, null, non-finite and under18 ages cannot receive explicit external detail; garments and private actions prevent it. Both-sex actual age/modesty cases are retained in the component surface proof. The separate neutral age6 study contains no explicit genital detail or adult secondary-sex mesh. Coverings follow the society's observed modesty/season instead of painting a whole torso and legs as a garment. Actual cloth regions cover what they cover; body geometry is not painted through them.

Distance-driven phase replaces wall-time flailing, and two-bone leg/arm constraints preserve segment length. Independent analysis of the produced instance matrices uses81 distances across8 age/sex cases. Across sampled walks, maximum leg-segment length variation is3.08458695e-8 scene units; arm variation3.00198847e-8. Grounded runs are detected from the actual ankle's floor-height plateau, and their maximum world-z drift is1.04308128e-7. Every same-side hand/leg correlation is negative (highest−0.99989745), showing the corrected counter-swing. This analysis uses the raw produced matrices, not only the intended gait formula. The retained phase images show lifted swing feet and reciprocal arms without a missing leg. Sampled rest/seated/lying vertex bounds cover162 age/sex/BMI/action cases; minimum y remains+0.00131709 scene units. These are bounded flat-fixture checks, not universal physical locomotion proof.

## Viewport geometry and controls

All three normal TABLE views show both complete world planes and their controls together. The portrait south coast remains clear of the bottom readout (about27px separation), preserving the previous repair. World planes/labels dominate the comparison; navigation stays compact. INSIDE views have a human-height horizon, nearby bodies, clear top navigation and a small corner readout. Sky and ground are the camera view, not invented UI padding. No unintended clipping, page overflow, detached labels, giant empty header or covered normal-state world edge was found in these frames.

|Viewport|Top navigation bottom|Bottom readout height|Visibility|
|---|---|---|---|
|390×844|68px /8.06%|73.56px /8.72%|Both world planes, identities and all five choices fit|
|1024×768|46px /5.99%|73.56px /9.58%|Both planes/labels and choices fit|
|1440×900|46px /5.11%|73.56px /8.17%|Both planes/labels and choices fit|

The desktop brand/instruction group extends to y146 as a content-sized corner overlay; it is not a full-width bar. Its backdrop, hint and key text retain the readable contrast repair. On phone the secondary instructions are omitted while action labels/world facts remain. Buttons and reader controls remain34px high. No text was shrunk or world feature clipped to accommodate the new figures.

Independent native-keyboard captures at390/1440 used exact final HTTP bytes. Five native Tab presses focus RECORD with a visible gold outline; Enter opens the record and its pagers. Page dimensions equal viewport dimensions, no JavaScript errors are reported, and the expanded record remains readable within the screen. On phone, opening RECORD intentionally overlays a small lower part of the scene while the observer reads evidence; closing it restores the complete comparison. This is useful optional content, not a blank expanded panel. Normal-state coastline remains unobscured.

Verdict: scoped pass for these exact-source views, age/garment guards, sampled attachment/floor/straight-gait geometry and keyboard states. Existing world comparison, actual recorded positions/actions, held-record semantics, lighting clock, readable controls and focus remain preserved.

Remaining: figures are stylized; all action transitions, terrain-slope foot contact, turning/crowd interactions, detailed human anatomical variation and physical tissue motion are not established by these samples. MacBook performance, touch locomotion and Quest input/performance remain unverified. INSPECT holds an observed record rather than inventing a continuous biological life between snapshots. No survival or physiology claim follows from these drawings.
