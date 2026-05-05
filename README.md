# R2-Guard Reproduction

This repository contains my reproducibility work for the paper **R2-Guard: Robust Reasoning Enabled LLM Guardrail**.

The original code release is from:

```text
https://github.com/kangmintong/R-2-Guard
```

I kept the original project structure and added only the files needed to set up the environment, run the main reproduced experiments, and inspect the results.

## What is included

- `REPRODUCIBILITY.md`: setup instructions, commands used, and notes about what was/was not reproduced.
- `repro_table2.sh`: local Table 2 style runs.
- `repro_weights.sh`: weight-learning experiments.
- `run_openai_mod_balanced_n64.sh`: small OpenAI Moderation subset run used when full API scoring was rate-limited.
- `analyze_reasoning_extension.py`: reasoning-layer extension analysis using saved result CSVs.
- `results/`: final CSV/Markdown result summaries kept for the report.

## Main result files

```text
results/table2_local_full.csv
results/table2_local_full_deviation.md
results/table2_llamaguard_8bit_full.csv
results/table2_llamaguard_8bit_full_deviation.md
results/table2_official_style_balanced_n64.csv
results/table2_official_style_balanced_n64_deviation.md
results/extension_reasoning_ablation.csv
```

## Quick start

Create a `.env` file if you want to run gated/API models:

```bash
cp .env.template .env
```

For local Docker runs on my RTX 5070 setup:

```bash
docker build -f Dockerfile.local5070 -t r2guard-local5070 .
```

Then run the local reproduction commands:

```bash
bash repro_table2.sh
```

To reproduce the reasoning-layer extension table from the saved result CSVs:

```bash
python analyze_reasoning_extension.py
```

This creates:

```text
results/extension_reasoning_ablation.csv
```

The exact full paper reproduction requires external services and stronger hardware than my local machine. Details are in `REPRODUCIBILITY.md`.
