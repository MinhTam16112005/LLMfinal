# Deviation Report

## Summary

- Produced metric rows: 22 partial rows.
- Blocked metric rows: 94 rows.
- No paid API calls are included in the current budget-capped reproduction.
- Current produced values are not exact Table 2/Table 5 values because they use balanced 100-example local subsets and two local components.

## Produced Values

- Detoxify on ToxicChat: reproduced AUPRC 0.7078231908235595, delta 0.3218231908235595, status PARTIAL.
- Detoxify on XSTest: reproduced AUPRC 0.8683075283273901, delta 0.20830752832739008, status PARTIAL.
- Detoxify on Overkill: reproduced AUPRC 0.5868963914372108, delta 0.12489639143721082, status PARTIAL.
- Detoxify on TwinSafety: reproduced AUPRC 0.4651838259040192, delta -0.1328161740959808, status PARTIAL.
- ToxicChat-T5 on ToxicChat: reproduced AUPRC 0.9558075646110629, delta 0.07080756461106286, status PARTIAL.
- ToxicChat-T5 on XSTest: reproduced AUPRC 0.9570993453528914, delta 0.13809934535289148, status PARTIAL.
- ToxicChat-T5 on Overkill: reproduced AUPRC 0.9559099241832335, delta 0.15490992418323346, status PARTIAL.
- ToxicChat-T5 on TwinSafety: reproduced AUPRC 0.4771469458100067, delta -0.12985305418999327, status PARTIAL.
- Ensemble on ToxicChat: reproduced AUPRC 0.9358088484482026, delta 0.05380884844820255, status PARTIAL.
- Ensemble on XSTest: reproduced AUPRC 0.9544918325861529, delta 0.14449183258615284, status PARTIAL.
- Ensemble on Overkill: reproduced AUPRC 0.9052510788698056, delta 0.0262510788698056, status PARTIAL.
- Ensemble on TwinSafety: reproduced AUPRC 0.47198321831131756, delta -0.18101678168868246, status PARTIAL.
- R2-Guard MLN on ToxicChat: reproduced AUPRC 0.9393456510831898, delta 0.03634565108318977, status PARTIAL.
- R2-Guard MLN on XSTest: reproduced AUPRC 0.9589510557984737, delta 0.08095105579847373, status PARTIAL.
- R2-Guard MLN on Overkill: reproduced AUPRC 0.9099971832252072, delta -0.011002816774792867, status PARTIAL.
- R2-Guard MLN on TwinSafety: reproduced AUPRC 0.4745452340872633, delta -0.2834547659127367, status PARTIAL.
- R2-Guard PC on ToxicChat: reproduced AUPRC 0.9393456510831898, delta 0.030345651083189762, status PARTIAL.
- R2-Guard PC on XSTest: reproduced AUPRC 0.9589510557984737, delta 0.07695105579847372, status PARTIAL.
- R2-Guard PC on Overkill: reproduced AUPRC 0.9099971832252072, delta -0.009002816774792866, status PARTIAL.
- R2-Guard PC on TwinSafety: reproduced AUPRC 0.4745452340872633, delta -0.2824547659127367, status PARTIAL.
- MLN reasoning: reproduced AUPRC 0.8207097810485335, delta -0.04829021895146646, status PARTIAL.
- PC reasoning: reproduced AUPRC 0.8207097810485335, delta -0.04829021895146646, status PARTIAL.

## Main Blockers

- OpenAI, Azure, and Perspective rows require external APIs and are blocked under the $10 budget unless explicitly approved.
- LlamaGuard requires gated Hugging Face access and/or a cached checkpoint.
- CoT baseline is not released as runnable code with the manual demonstrations described in the paper.
- Full R2-Guard Table 2 needs complete component score caches for OpenAI Mod, LlamaGuard, and ToxicChat-T5 on all six datasets.
- Table 4 jailbreak reproduction is blocked because exact generated PAIR/TAP/AutoDAN/GCG-R artifacts are not fully present and new harmful jailbreak generation is out of scope.
- Paper PC reasoning says spectral clustering; released code path uses `--AC_inference` graph partitioning, so it is documented as PC-like unless the missing spectral clustering implementation is recovered.

## Environment Snapshot

- OS: Windows-11-10.0.26200-SP0
- Python used for report generation: 3.12.10
- Git commit: 8cc3ce3f103892886e5e8261bf41b8929f7021e0
- Docker images are documented in `REPRODUCIBILITY.md`; local smoke run used `r2guard-local5070:latest`.
