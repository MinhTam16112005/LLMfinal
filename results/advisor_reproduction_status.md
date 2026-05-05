# R2-Guard Reproduction Status for Advisor

## Current Verdict

We have a strong controlled partial reproduction and an official-style R2-Guard setup, but not an exact full paper reproduction yet.

The main blocker is no longer code execution. The blocker is OpenAI Moderation rate limiting for full six-dataset scoring under the current API. LlamaGuard gated access is resolved, and local baselines are complete.

## Completed

### 1. Environment and Repo Recovery

- Official repo: `kangmintong/R-2-Guard`
- Commit: `8cc3ce3f103892886e5e8261bf41b8929f7021e0`
- Local hardware: RTX 5070, 12 GB VRAM
- Paper hardware: RTX A6000
- Docker/local environment built and smoke-tested.
- Reproducibility runbook, environment files, result logging, checkpointing, and resume support added.

Status: `DONE`

### 2. Local Baseline Reproduction

Full local-only Table 2-style runs completed where no paid API or gated model was needed.

Key sanity checks:

| Model | Dataset | Paper AUPRC | Reproduced AUPRC | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Detoxify | OpenAI Mod | 0.780 | 0.779746 | Very close |
| ToxicChat-T5 | OpenAI Mod | 0.787 | 0.787199 | Very close |

These results strongly validate the dataset loading, score extraction, and AUPRC evaluation path.

Outputs:

- `results/table2_local_full.jsonl`
- `results/table2_local_full.csv`
- `results/table2_local_full_deviation.md`

Status: `STRONG PARTIAL REPRODUCTION`

### 3. LlamaGuard

Hugging Face gated access was approved and verified.

Full six-dataset LlamaGuard run completed using 8-bit local inference on RTX 5070.

| Dataset | LlamaGuard-8bit AUPRC |
| --- | ---: |
| OpenAI Mod | 0.772854 |
| ToxicChat | 0.665021 |
| XSTest | 0.778840 |
| Overkill | 0.850133 |
| BeaverTails | 0.783033 |
| TwinSafety/ours | 0.735547 |

Label: `PARTIAL-HARDWARE-ADAPTED`

Reason: the paper used an RTX A6000/default LlamaGuard setup, while this run used 8-bit inference on RTX 5070.

Outputs:

- `results/table2_llamaguard_8bit_full.jsonl`
- `results/table2_llamaguard_8bit_full.csv`
- `results/table2_llamaguard_8bit_full_deviation.md`

Status: `DONE, HARDWARE-ADAPTED`

## OpenAI Moderation Status

### Smoke Test

OpenAI Moderation endpoint works.

Observed:

- `text-moderation-stable` failed because it is unavailable.
- Current default moderation endpoint worked and returned `omni-moderation-latest`.

Label: `RECONSTRUCTED-CURRENT-API`

Outputs:

- `results/openai_moderation_smoke.json`
- `results/table2_openai_mod_smoke_n2.jsonl`
- `results/openai_preflight_smoke.md`

Status: `SMOKE PASSED`

### Full Run

The full OpenAI Moderation run was started but paused due to rate limits.

Preserved progress:

- `openaimod`: 600 / 1680 examples scored

Observed rate-limit behavior:

- Batch size 32 without pacing hit `Too Many Requests`.
- Batch size 8 with short sleep still hit `Too Many Requests`.
- Batch size 32 with 65-second sleep worked but was too slow for the report timeline.
- Batch size 128 probe failed immediately with `RateLimitError`, likely because the project was still inside the rate-limit cooldown window.

Diagnosis:

- This is an OpenAI project/key rate-limit issue, not a repo execution issue.
- Adding API budget may not immediately increase request/minute or token/minute limits unless the OpenAI account/project tier or limits are increased.

Output:

- `results/openai_rate_limit_diagnosis.md`

Status: `BLOCKED / TOO SLOW UNDER CURRENT RATE LIMIT`

## Official-Style R2-Guard Status

The official-style inference path was smoke-tested using:

- OpenAI Mod
- LlamaGuard-8bit
- ToxicChat-T5

Rows tested:

- Ensemble
- R2-Guard MLN
- R2-Guard PC-like released-code `--AC_inference`

Output:

- `results/table2_official_style_smoke_n10.jsonl`

Status: `READY, BUT FULL OFFICIAL-STYLE TABLE BLOCKED BY FULL OPENAI SCORES`

Important labeling:

- OpenAI Mod: `RECONSTRUCTED-CURRENT-API`
- LlamaGuard: `PARTIAL-HARDWARE-ADAPTED`
- R2-Guard MLN: `OFFICIAL-STYLE`, once full component scores exist
- R2-Guard PC: `OFFICIAL-STYLE / PC-LIKE-RELEASED-CODE`

## What We Can Honestly Claim Now

We can claim:

1. The official R2-Guard repo was recovered into a controlled reproducibility environment.
2. The core dataset and AUPRC evaluation pipeline was validated against paper numbers.
3. Detoxify and ToxicChat-T5 reproduce very closely on OpenAI Mod.
4. LlamaGuard is no longer blocked and has been run across all six datasets in an 8-bit local configuration.
5. OpenAI Moderation is available only through the current default API, not the paper's deprecated `text-moderation-stable`.
6. Full official-style R2-Guard is technically ready but blocked by OpenAI rate limits for full six-dataset scoring.

We should not claim:

1. Exact Table 2 reproduction.
2. Exact OpenAI Mod paper row.
3. Exact LlamaGuard paper row.
4. Exact Algorithm 1 PC, because the released code path is PC-like `AC_inference`, not clearly the spectral clustering algorithm described in the paper.
5. Jailbreak Table 3/4 reproduction.

## Fast Report Recommendation

For the report deadline, use the completed local and LlamaGuard results as the main evidence, and present OpenAI Moderation as a documented current-API blocker.

Recommended wording:

> We reproduced the R2-Guard evaluation pipeline and several Table 2 components. Detoxify and ToxicChat-T5 closely match the reported OpenAI Mod AUPRCs, validating the dataset and metric implementation. We also recovered LlamaGuard after gated access approval and evaluated it on all six datasets using an 8-bit RTX 5070 configuration. The official-style R2-Guard pipeline with OpenAI Mod, LlamaGuard, and ToxicChat-T5 was smoke-tested successfully. However, full OpenAI Moderation scoring could not be completed within the reporting timeline because the current OpenAI Moderation API rate-limited full dataset scoring, and the paper's `text-moderation-stable` model is no longer available. Therefore, official-style R2-Guard full Table 2 results remain blocked under current API constraints.

