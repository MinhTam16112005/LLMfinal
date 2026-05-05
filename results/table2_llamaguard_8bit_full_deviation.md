# LlamaGuard 8-bit Full-Dataset Deviation

Status: `PARTIAL-HARDWARE-ADAPTED`

This run scored all six Table 2 datasets with `meta-llama/LlamaGuard-7b`, but loaded locally with 8-bit quantization on the RTX 5070. The paper reports LlamaGuard under its default setup on an RTX A6000, so these numbers should be compared to the paper row as a hardware-adapted reproduction, not an exact paper-resource run.

Outputs:

- `results/table2_llamaguard_8bit_full.jsonl`
- `results/table2_llamaguard_8bit_full.csv`

Full-dataset AUPRCs:

| Dataset | Paper LlamaGuard | Reproduced 8-bit local | Delta |
| --- | ---: | ---: | ---: |
| OpenAI Mod | 0.788 | 0.772854 | -0.015146 |
| ToxicChat | 0.698 | 0.665021 | -0.032979 |
| XSTest | 0.765 | 0.778840 | 0.013840 |
| Overkill | 0.855 | 0.850133 | -0.004867 |
| BeaverTails | 0.789 | 0.783033 | -0.005967 |
| TwinSafety | 0.737 | 0.735547 | -0.001453 |

No paid APIs, generation APIs, Azure, Perspective, or jailbreak attacks were used in this run.
