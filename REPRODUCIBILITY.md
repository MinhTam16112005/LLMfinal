# Reproducibility Notes

## Goal

The goal was to reproduce the main R2-Guard evaluation pipeline from the released code and compare the results with Table 2 of the paper.

The full paper result is not completely reproducible from this repo alone because some external services and artifacts are not fixed:

- the paper's OpenAI moderation model `text-moderation-stable` is no longer available through the current API;
- OpenAI API scoring was rate-limited during full six-dataset runs;
- LlamaGuard requires gated Hugging Face access;
- the paper used an RTX A6000, while this reproduction was run on an RTX 5070;
- the released PC path is the repo's `--AC_inference` implementation, which I label as PC-like because it is not clearly the exact spectral clustering procedure described in Algorithm 1.

Because of this, I separate results into:

- **local full runs**: full datasets with local/free models;
- **hardware-adapted LlamaGuard**: full datasets with LlamaGuard loaded in 8-bit;
- **official-style subset**: balanced 64-example subset using OpenAI Moderation current API + LlamaGuard + ToxicChat-T5.

## Environment

The official repo did not include a dependency lockfile. I added:

```text
requirements-repro.txt
environment-repro.yml
Dockerfile.local5070
Dockerfile.repro
```

For my local machine, I used Docker:

```bash
docker build -f Dockerfile.local5070 -t r2guard-local5070 .
```

For an A6000 machine, `Dockerfile.repro` is closer to the paper hardware/software target.

## Credentials

Create `.env` from the template:

```bash
cp .env.template .env
```

Useful variables:

```text
HF_TOKEN=...
OPENAI_API_KEY=...
```

The `.env` file is ignored by git.

## Experiments

### 1. Local Table 2 style reproduction

This runs local models and R2-Guard inference paths without paid APIs:

```bash
bash repro_table2.sh
```

Important output files:

```text
results/table2_local_full.csv
results/table2_local_full_deviation.md
```

Two sanity checks matched the paper closely:

| Model | Dataset | Paper AUPRC | Reproduced AUPRC |
| --- | --- | ---: | ---: |
| Detoxify | OpenAI Mod | 0.780 | 0.779746 |
| ToxicChat-T5 | OpenAI Mod | 0.787 | 0.787199 |

### 2. LlamaGuard full run

LlamaGuard was run with 8-bit loading because of local VRAM limits:

```bash
python run_knowledge_models.py \
  --knowledge_model_name llamaguard \
  --dataset openaimod \
  --llamaguard_load_in_8bit \
  --llamaguard_float16
```

This was repeated for:

```text
openaimod, toxicchat, xstest, overkill, beavertail, ours
```

Important output files:

```text
results/table2_llamaguard_8bit_full.csv
results/table2_llamaguard_8bit_full_deviation.md
```

This should be read as `PARTIAL-HARDWARE-ADAPTED`, not exact paper hardware.

### 3. OpenAI Moderation subset

The original paper's OpenAI moderation model is no longer available. The current default OpenAI moderation endpoint returned `omni-moderation-latest`.

Full scoring was too slow under the current rate limit, so I ran a small balanced subset:

```bash
bash run_openai_mod_balanced_n64.sh
```

This used:

```text
max_instances=64
subset_strategy=balanced
datasets=openaimod toxicchat xstest overkill beavertail ours
```

### 4. Official-style subset R2-Guard

After the OpenAI subset scores were created, I matched the same balanced subset for LlamaGuard and ToxicChat-T5:

```bash
python prepare_subset_cache.py \
  --models llamaguard toxicchat-T5 \
  --dataset openaimod \
  --max-instances 64 \
  --subset-strategy balanced
```

Then I ran:

```bash
python knowledge_guardrail_inference.py \
  --knowledge_model_name openai_mod llamaguard toxicchat-T5 \
  --dataset openaimod \
  --max_instances 64 \
  --subset_strategy balanced \
  --ensemble_max
```

For R2-Guard MLN, remove `--ensemble_max`.

For the released PC-like path, add:

```bash
--AC_inference
```

Important output files:

```text
results/table2_official_style_balanced_n64.csv
results/table2_official_style_balanced_n64_deviation.md
```

## Final result files kept in this repo

Only the final report tables are kept:

```text
results/table2_local_full.csv
results/table2_local_full_deviation.md
results/table2_llamaguard_8bit_full.csv
results/table2_llamaguard_8bit_full_deviation.md
results/table2_official_style_balanced_n64.csv
results/table2_official_style_balanced_n64_deviation.md
```

Intermediate cache files and scratch logs were removed to keep the submission clean.

## Limitations

This repository does not claim exact reproduction of every paper table.

Not reproduced exactly:

- full OpenAI Mod row with the deprecated paper model;
- full official-style R2-Guard Table 2 using all three paper components on all six full datasets;
- CoT baseline, because the exact demonstrations were not released;
- jailbreak Tables 3 and 4;
- exact Algorithm 1 PC if the paper's spectral clustering implementation differs from the released `--AC_inference` path.

The strongest reproduced evidence is the local full baseline match and the official-style subset pipeline.
