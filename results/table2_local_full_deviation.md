# Local Full Table 2 Deviation

This report uses full datasets where available and no paid APIs.

- Produced rows: 30
- Blocked rows: 0
- `EXACT-LOCAL` means same full dataset and same local model family as the paper row.
- `PARTIAL-COMPONENT` means full dataset but not the official paper R2-Guard component set.
- PC result is labeled `PC-like released AC_inference`, not exact Algorithm 1 spectral clustering.

## Produced Rows

- Detoxify / OpenAI Mod: AUPRC=0.7797461453228797, paper_ref=0.78, delta=-0.0002538546771203576, status=EXACT-LOCAL
- Detoxify / ToxicChat: AUPRC=0.4004593995200462, paper_ref=0.386, delta=0.014459399520046212, status=EXACT-LOCAL
- Detoxify / XSTest: AUPRC=0.6595135594342971, paper_ref=0.66, delta=-0.00048644056570290584, status=EXACT-LOCAL
- Detoxify / Overkill: AUPRC=0.46257655555067034, paper_ref=0.462, delta=0.0005765555506703213, status=EXACT-LOCAL
- Detoxify / BeaverTails: AUPRC=0.6361684313285679, paper_ref=0.636, delta=0.00016843132856791954, status=EXACT-LOCAL
- Detoxify / TwinSafety: AUPRC=0.5978033670060525, paper_ref=0.598, delta=-0.00019663299394745426, status=EXACT-LOCAL
- ToxicChat-T5 / OpenAI Mod: AUPRC=0.7871987209261866, paper_ref=0.787, delta=0.00019872092618655746, status=EXACT-LOCAL
- ToxicChat-T5 / ToxicChat: AUPRC=0.8848956823259938, paper_ref=0.885, delta=-0.00010431767400620462, status=EXACT-LOCAL
- ToxicChat-T5 / XSTest: AUPRC=0.8189983180769338, paper_ref=0.819, delta=-1.681923066154667e-06, status=EXACT-LOCAL
- ToxicChat-T5 / Overkill: AUPRC=0.8008279081323357, paper_ref=0.801, delta=-0.0001720918676643146, status=EXACT-LOCAL
- ToxicChat-T5 / BeaverTails: AUPRC=0.7611553624836135, paper_ref=0.761, delta=0.00015536248361347482, status=EXACT-LOCAL
- ToxicChat-T5 / TwinSafety: AUPRC=0.6067726585380147, paper_ref=0.607, delta=-0.0002273414619853309, status=EXACT-LOCAL
- Ensemble / OpenAI Mod: AUPRC=0.8081551823721133, paper_ref=0.876, delta=-0.06784481762788674, status=PARTIAL-COMPONENT
- Ensemble / ToxicChat: AUPRC=0.8728400395060156, paper_ref=0.882, delta=-0.009159960493984376, status=PARTIAL-COMPONENT
- Ensemble / XSTest: AUPRC=0.8055586227465681, paper_ref=0.81, delta=-0.004441377253431966, status=PARTIAL-COMPONENT
- Ensemble / Overkill: AUPRC=0.7462486869034711, paper_ref=0.879, delta=-0.13275131309652888, status=PARTIAL-COMPONENT
- Ensemble / BeaverTails: AUPRC=0.7322521789246508, paper_ref=0.797, delta=-0.06474782107534927, status=PARTIAL-COMPONENT
- Ensemble / TwinSafety: AUPRC=0.6012736915210753, paper_ref=0.653, delta=-0.051726308478924676, status=PARTIAL-COMPONENT
- R2-Guard MLN local-components / OpenAI Mod: AUPRC=0.8193763067902078, paper_ref=0.926, delta=-0.10662369320979226, status=PARTIAL-COMPONENT
- R2-Guard MLN local-components / ToxicChat: AUPRC=0.8261528472714276, paper_ref=0.903, delta=-0.07684715272857245, status=PARTIAL-COMPONENT
- R2-Guard MLN local-components / XSTest: AUPRC=0.8073299153693749, paper_ref=0.878, delta=-0.07067008463062507, status=PARTIAL-COMPONENT
- R2-Guard MLN local-components / Overkill: AUPRC=0.7169274257968659, paper_ref=0.921, delta=-0.20407257420313418, status=PARTIAL-COMPONENT
- R2-Guard MLN local-components / BeaverTails: AUPRC=0.727103785123446, paper_ref=0.83, delta=-0.10289621487655398, status=PARTIAL-COMPONENT
- R2-Guard MLN local-components / TwinSafety: AUPRC=0.6090071860703602, paper_ref=0.758, delta=-0.1489928139296398, status=PARTIAL-COMPONENT
- R2-Guard PC-like released AC_inference / OpenAI Mod: AUPRC=0.8193763067902078, paper_ref=0.924, delta=-0.10462369320979226, status=PARTIAL-COMPONENT
- R2-Guard PC-like released AC_inference / ToxicChat: AUPRC=0.8261528472714276, paper_ref=0.909, delta=-0.08284715272857246, status=PARTIAL-COMPONENT
- R2-Guard PC-like released AC_inference / XSTest: AUPRC=0.8073299153693749, paper_ref=0.882, delta=-0.07467008463062508, status=PARTIAL-COMPONENT
- R2-Guard PC-like released AC_inference / Overkill: AUPRC=0.7169274257968659, paper_ref=0.919, delta=-0.20207257420313418, status=PARTIAL-COMPONENT
- R2-Guard PC-like released AC_inference / BeaverTails: AUPRC=0.727103785123446, paper_ref=0.825, delta=-0.09789621487655398, status=PARTIAL-COMPONENT
- R2-Guard PC-like released AC_inference / TwinSafety: AUPRC=0.6090071860703602, paper_ref=0.757, delta=-0.1479928139296398, status=PARTIAL-COMPONENT

## Blockers

- Official R2-Guard full Table 2 remains blocked until OpenAI Mod, LlamaGuard, and ToxicChat-T5 full score caches exist for all six datasets.
- OpenAI/Azure/Perspective rows remain blocked by budget policy unless explicitly approved.
- LlamaGuard remains blocked unless gated Hugging Face access/checkpoint is available.
- Table 4 jailbreak reproduction remains blocked by missing exact artifacts and the no-new-jailbreak-generation constraint.
