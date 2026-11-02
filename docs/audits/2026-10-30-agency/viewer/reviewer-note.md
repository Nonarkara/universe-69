# Independent rendered review

Reviewer `/root/viewer_review` inspected all twelve retained natural-checkpoint
PNGs at 390×844, 1024×768 and 1440×900, including first-screen, person focus,
person+MORE and expanded HUD. Applied anti-slop-design and the project's MSH
law. This review did not author the capture harness or change production code.

**Found: one unresolved spatial failure in expanded HUD.** At 1024px, expanding
only EDEN makes LAGOON's single-line heading grow from 28 to 103px; about 75px
of blank header replaces useful LAGOON canvas. At 1440px it grows from 28 to
84px, costing about 56px. Both screenshots show a blank band below LAGOON's
one-line title. Aligning two scene baselines does not earn this otherwise
contentless band. Each world's own heading should determine its height, while
both scenes remain visible. First-screen and person/MORE states do not have
this expansion. No unconditional expanded-state MSH pass is claimed yet.

## Task and hierarchy

Task: compare the two inhabited worlds, select a real person, and read their
identity/activity and the record without losing either world. The two painted
worlds dominate; selected name/activity and compact world identity come second;
instruments and record controls come third. This order is apparent at all
three widths. Phone stacks both worlds and condenses instruments, rather than
turning the desktop into a long page. Expanded phone facts have earned content;
its other world's header remains content-sized.

## Measured chrome

Combined chrome includes masthead, world headings (summed on phone, maximum on
wide screens), instruments and record/footer. Percentages use full viewport
height, so they include these meaningful comparison/readout regions.

| Width | Masthead | Collapsed headings | Instruments | Record/footer | Combined first screen | Combined expanded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 390 | 35px | 27.75px each, stacked | 27px | 54px | 171.5px / 20.32% | 265.72px / 31.48% |
| 1024 | 35px | 28px | 109.38px | 54px | 226.38px / 29.48% | 301.5px / 39.26% |
| 1440 | 35px | 28px | 54.69px | 54px | 171.69px / 19.08% | 227.97px / 25.33% |

First-screen scene heights are respectively 335.25px each, 541.62px each and
728.31px each. Useful information/action fit without page scrolling. The
expanded-wide unused header is the specific unnecessary demand identified
above, rather than a blanket numeric threshold on chrome.

## Verified preservation and provenance

The capture report has 119/119 automated checks (40/40/39 by viewport), no
browser/request errors, and no overflow/overlap/clipped reading failures.
Independent visual inspection confirms selected foreground bodies above their
cards, readable full activities, visible native keyboard focus, functioning
MORE/expanded controls, both worlds and instruments retained. Cards fit their
content; phone detail pagination preserves available portrait space. No new
visual hierarchy failure was found in first-screen, focus or MORE states.

Checkpoint gzip/raw hashes, world-adapter hash, captured HTML and all thirteen
model-source hashes independently match the final freeze. `web/index.html`
and `docs/index.html` are byte-identical. HTML SHA-256 is
`dfe1de9aad347e2fea999a4df2bcb93dc3b6249af5b72f3f01592fc44f59675b`.
The source is unchanged from before this model increment.

This is the actual saved natural seed69 day9000/year25 workbench checkpoint,
EDEN57/LAGOON24, not the live MacBook instrument. Selected real generation-two
adults are Zillah18 on phone/tablet and Eve17 on desktop. No person fields were
fabricated. Event history was not supplied: the record placeholder is evidence
of omitted input, not an empty natural history. This bounded capture does not
retest all research/help/error/legacy states or prove natural century outcomes.

**Changed by reviewer:** none; the unnecessary wide expanded-header growth was
reported to root for correction. **Remaining:** re-render and independently
inspect that state after a cause-level fix before declaring full MSH clearance.
