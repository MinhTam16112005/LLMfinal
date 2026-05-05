# Official-Style Balanced n64 Subset Deviation

Status: `OFFICIAL-STYLE-SUBSET`

This is not full Table 2. It is a deadline-safe subset run using 64 balanced examples per dataset.

Components:

- OpenAI Mod: current default OpenAI Moderation API, labeled `RECONSTRUCTED-CURRENT-API-SUBSET`
- LlamaGuard: 8-bit local RTX 5070 scores, labeled `PARTIAL-HARDWARE-ADAPTED`
- ToxicChat-T5: local cached full-score source sliced to the same balanced n64 subset
- R2-Guard PC: released-code `--AC_inference`, labeled PC-like rather than exact Algorithm 1 spectral clustering

Outputs:

- `results\table2_openai_mod_currentapi_balanced_n64.jsonl`
- `results\table2_official_style_balanced_n64.jsonl`
- `results\table2_official_style_balanced_n64.csv`

| Model | Dataset | Paper full AUPRC | Subset AUPRC | Status |
| --- | --- | ---: | ---: | --- |
| OpenAI Mod | BeaverTails | 0.728 | 0.662810 | RECONSTRUCTED-CURRENT-API-SUBSET |
| OpenAI Mod | OpenAI Mod | 0.87 | 0.766165 | RECONSTRUCTED-CURRENT-API-SUBSET |
| OpenAI Mod | Overkill | 0.796 | 0.921908 | RECONSTRUCTED-CURRENT-API-SUBSET |
| OpenAI Mod | ToxicChat | 0.617 | 0.766058 | RECONSTRUCTED-CURRENT-API-SUBSET |
| OpenAI Mod | TwinSafety | 0.607 | 0.548723 | RECONSTRUCTED-CURRENT-API-SUBSET |
| OpenAI Mod | XSTest | 0.778 | 0.915043 | RECONSTRUCTED-CURRENT-API-SUBSET |
| Ensemble | BeaverTails | 0.797 | 0.690715 | OFFICIAL-STYLE-SUBSET |
| Ensemble | OpenAI Mod | 0.876 | 0.904821 | OFFICIAL-STYLE-SUBSET |
| Ensemble | Overkill | 0.879 | 0.962704 | OFFICIAL-STYLE-SUBSET |
| Ensemble | ToxicChat | 0.882 | 0.967029 | OFFICIAL-STYLE-SUBSET |
| Ensemble | TwinSafety | 0.653 | 0.523721 | OFFICIAL-STYLE-SUBSET |
| Ensemble | XSTest | 0.81 | 0.906275 | OFFICIAL-STYLE-SUBSET |
| R2-Guard MLN | BeaverTails | 0.83 | 0.644592 | OFFICIAL-STYLE-SUBSET |
| R2-Guard MLN | OpenAI Mod | 0.926 | 0.900277 | OFFICIAL-STYLE-SUBSET |
| R2-Guard MLN | Overkill | 0.921 | 0.978220 | OFFICIAL-STYLE-SUBSET |
| R2-Guard MLN | ToxicChat | 0.903 | 0.952333 | OFFICIAL-STYLE-SUBSET |
| R2-Guard MLN | TwinSafety | 0.758 | 0.531998 | OFFICIAL-STYLE-SUBSET |
| R2-Guard MLN | XSTest | 0.878 | 0.961870 | OFFICIAL-STYLE-SUBSET |
| R2-Guard PC-like | BeaverTails | 0.825 | 0.644592 | OFFICIAL-STYLE-SUBSET / PC-LIKE-RELEASED-CODE |
| R2-Guard PC-like | OpenAI Mod | 0.924 | 0.900277 | OFFICIAL-STYLE-SUBSET / PC-LIKE-RELEASED-CODE |
| R2-Guard PC-like | Overkill | 0.919 | 0.978220 | OFFICIAL-STYLE-SUBSET / PC-LIKE-RELEASED-CODE |
| R2-Guard PC-like | ToxicChat | 0.909 | 0.952333 | OFFICIAL-STYLE-SUBSET / PC-LIKE-RELEASED-CODE |
| R2-Guard PC-like | TwinSafety | 0.757 | 0.531998 | OFFICIAL-STYLE-SUBSET / PC-LIKE-RELEASED-CODE |
| R2-Guard PC-like | XSTest | 0.882 | 0.961870 | OFFICIAL-STYLE-SUBSET / PC-LIKE-RELEASED-CODE |
