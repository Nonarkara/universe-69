# Independent rendered review — encounter UI

**Status: accepted for the inspected controlled UI states, final HTML SHA-256 `529d0594fae4248fcb915154bd2e26a2c584eecd1d3f4e92174251f1c7194a19`.** This is a UI review only. The fixtures are explicitly controlled/synthetic setups using actual engine APIs and summary packets. They do not establish natural mating, birth rates, human agency, or demographic success. The century run's EDEN/LAGOON extinctions are a separate model result.

Task: see both worlds together, distinguish invitation/contact/labour/rest, and inspect a person's actual activity without losing the comparison. Priority: worlds first, selected person/activity second, record third.

Applied `anti-slop-design` and project MSH. Read fixture and viewer provenance, focused/full browser reports, and inspected the actual PNGs with `view_image`. No `viewer/README.md` existed at review time; provenance was available. The reviewer did not author this renderer increment or its screenshot harness.

## Found

The **first-snapshot empty record footer reserved unnecessary space**, visible in the person-focus captures, although its content did not require that space. At 390×844 it occupied 111 px (13.15%) versus 54 px (6.40%) after MORE. At 1440×900 it occupied 130 px (14.44%) versus 54 px (6.00%). This reserved 57/76 px of empty space and reduces the worlds. The screenshots show the blank area; a passing overflow check alone cannot accept it. `lagoon-contact-390x844-focus.png` and the corresponding MORE state are a direct example. Initial diagnosis suspected a focus/reflow fit loss. The owner reproduced the cause: the first poll did not initialize records until the eighth animation tick, approximately 0.27–0.53 s later. Settled records already fit correctly. The fix initializes the record immediately from the first snapshot before a frame can expose the empty default-height box. A red-then-green poll regression and first-snapshot content/fit assertions pin it. No reviewer renderer changes.

## Changed and verified

- Phone stacks the worlds, tablet/desktop show them side by side. Both remain visible with selected details, MORE and expanded world information. Maps deserve their area: they are the task, not empty decorative panels.
- Pending bonded invitations show `seeking a partner`, neutral independent rest figures, and no joint sprite. Actual EDEN nonbond contact draws IDs1/4 despite biography partner2; actual LAGOON draws1/2. Render-call probes support the visible figures. Permanent partner identity no longer invents a sexual couple.
- Labour reads `in labour`; post-delivery reads `resting`, without a sexual couple or continuing birth label. The controlled postpartum packet records an infant loss, so it is not evidence of a surviving newborn.
- Native focus on the person details has a visible gold outline. The selected body stays above the details card. Existing body/age rig, cameras, full-resolution terrain, captions, instruments, paged reading, filters and controls are retained in the supplied browser evidence.
- Font sizes/line measures remain readable. Compact35px masthead groups identity and actions; body reading has a comfortable measure. No new badge/card/hero/chrome band was introduced. Expanded world metadata earns its requested height; aligned comparison panes retain the two-world composition.

Fresh images at all three widths show the empty record at 54 px from the initial person-focus state, through MORE and expanded world information. The phone recovers 57 px (6.75% of viewport); desktop recovers 76 px (8.44%). The actual selected bodies remain visible above their cards. Before images and measurements are retained in `viewer/before-footer-fit/`.

Representative measured chrome (masthead + world headings + instrument strip + record; excludes earned person detail overlay):

| Viewport | Masthead | Focus total before repair | Final focus / MORE total | Task visibility |
|---|---:|---:|---:|---|
|390×844|35px /4.15%|228.5px /27.07%|171.5px /20.32%|Both worlds and selected activity visible;57px restored to world views.|
|1024×768|35px /4.56%|226.4px /29.48%|226.4px /29.48%|Both worlds side by side; two-row instrument strip earns its109.4px.|
|1440×900|35px /3.89%|247.7px /27.52%|171.7px /19.08%|Both worlds, activity and record visible;76px restored to world views.|

Viewed first-screen world images at all three sizes; focused pending 390, actual EDEN 1024, labour 1440, actual LAGOON 390; MORE pending 390/labour1024/postpartum 390; expanded pending1440/actual EDEN 1024/labour 390/postpartum 1440; and the390 research reading page. After the fix, independently re-opened the fresh LAGOON focus screenshots at 390/1024/1440; pending 390 expanded; actual EDEN 1024 MORE; labour 390 focus; postpartum 1440 expanded. The formerly blank footer now contains its empty-state line and fits 54 px in each inspected state. The gold native focus outline, selected portraits, honest captions, reciprocal joint figures and both worlds remain intact. Final focused report: 441/441; full journey: 268/268 phone and242/242 each tablet/desktop (752/752 total), with no recorded failures. Reports, PNGs and current byte-identical web/docs HTML share the final source hash above.

## Remaining

No unresolved SH found in the inspected final states. Expanded metadata and reading pages remain intentional user-selected content, with readable text and paging; no new decorative chrome was added to repair the gap. Motion/cache/rig/menu/error/retry coverage is supplied by the full browser journey, rather than inferred solely from still images. All acceptance remains scoped to the controlled UI packets, not the biological model or century outcome. The separate century run ended with EDEN extinct on day 28555 and LAGOON on day 35630; a visual pass does not turn that into a successful demographic model.
