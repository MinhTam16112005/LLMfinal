# R2-Guard Reproduction Log

This file records the current budget-capped reproduction state.

## Repository

- Official repo: https://github.com/kangmintong/R-2-Guard
- Local commit: 8cc3ce3f103892886e5e8261bf41b8929f7021e0

## Budget Policy

- Total budget limit: $10.
- Paid API calls are not allowed unless explicitly approved.
- OpenAI, Azure, Perspective, and jailbreak tables are marked `BLOCKED` when they require API calls or missing artifacts.

## Completed Minimal Run

Command:

```bash
docker run --rm --gpus all -v "${PWD}:/workspace" -v "${PWD}/hf_cache:/root/.cache/huggingface" -v "${PWD}/torch_cache:/root/.cache/torch" -w /workspace -e NUM_PROCESSES=4 r2guard-local5070:latest python3.10 repro_runner.py --stage minimal-local --datasets toxicchat xstest overkill ours --max_instances 100 --subset_strategy balanced --result_jsonl results/minimal_local_balanced.jsonl
```

Produced:

- Detoxify on balanced 100-example subsets
- ToxicChat-T5 on balanced 100-example subsets
- Ensemble over Detoxify + ToxicChat-T5
- R2-Guard MLN over Detoxify + ToxicChat-T5 with uniform aggregation
- R2-Guard PC-like `--AC_inference` over the same components

The run used local/free model paths and did not pass API keys into Docker.

## Outputs

- `results/minimal_local_balanced.jsonl`
- `results/table2_reproduction.csv`
- `results/table4_reproduction.csv`
- `results/table5_reproduction.csv`
- `results/deviation_report.md`
- `results/environment_snapshot.txt`
- `requirements-freeze.txt`

See `REPRODUCIBILITY.md` for the broader runbook and blocker inventory.

## Completed Full Local-Only Table 2 Pass

Command:

```bash
docker run --rm --gpus all -v "${PWD}:/workspace" -v "${PWD}/hf_cache:/root/.cache/huggingface" -v "${PWD}/torch_cache:/root/.cache/torch" -w /workspace -e NUM_PROCESSES=4 r2guard-local5070:latest python3.10 repro_runner.py --stage local-full --datasets openaimod toxicchat xstest overkill beavertail ours --result_jsonl results/table2_local_full.jsonl
```

Produced full-dataset, no-paid-API rows for:

- Detoxify on OpenAI Mod, ToxicChat, XSTest, Overkill, BeaverTails, and TwinSafety/ours.
- ToxicChat-T5 on OpenAI Mod, ToxicChat, XSTest, Overkill, BeaverTails, and TwinSafety/ours.
- Local-component ensemble over Detoxify + ToxicChat-T5.
- Local-component R2-Guard MLN over Detoxify + ToxicChat-T5.
- Local-component R2-Guard PC-like released `--AC_inference` over Detoxify + ToxicChat-T5.

Outputs:

- `results/table2_local_full.jsonl`
- `results/table2_local_full.csv`
- `results/table2_local_full_deviation.md`

Important interpretation:

- Detoxify and ToxicChat-T5 rows are labeled `EXACT-LOCAL`: full dataset and same local model family as the paper, no paid API.
- Ensemble and R2-Guard rows are labeled `PARTIAL-COMPONENT`: full dataset, but they use Detoxify + ToxicChat-T5 instead of the paper's OpenAI Mod + LlamaGuard + ToxicChat-T5 component set.
- PC is labeled `R2-Guard PC-like released AC_inference`, not exact Algorithm 1 spectral clustering.
- No paid APIs were called.
- No new jailbreak generation was run.

## LlamaGuard Smoke Test

Access state:

- `HF_TOKEN` is present in `.env`.
- After Hugging Face approval, `AutoConfig.from_pretrained("meta-llama/LlamaGuard-7b", token=HF_TOKEN)` succeeds.
- The three LlamaGuard model shards downloaded into `hf_cache`.

Released-code/full-precision attempt:

- A first smoke attempt started downloading/loading the released `llamaguard` path.
- It used the repo's original full-precision loading style.
- It did not write a result before the auto-removed container exited.
- Observed memory use reached roughly 14 GB container RAM before exit, so this path is not reliable on the local 12 GB RTX 5070.

Local 5070 adaptation:

- Added optional flags to `run_knowledge_models.py`:
  - `--llamaguard_load_in_8bit`
  - `--llamaguard_float16`
- Retried a 2-example LlamaGuard smoke test with `--llamaguard_load_in_8bit`.
- The 8-bit smoke test succeeded.

Smoke outputs:

- `results/llamaguard_smoke_8bit.jsonl`
- `cache/llamaguard_xstest_scores_n2.json`

Interpretation:

- Hugging Face gated access is now available.
- LlamaGuard can run locally on the RTX 5070 in 8-bit mode for smoke testing.
- The 8-bit path is a local-resource adaptation and must be labeled separately from exact paper-resource LlamaGuard.

## LlamaGuard 8-bit Balanced 100-Example Run

Command pattern:

```bash
python3.10 run_knowledge_models.py --knowledge_model_name llamaguard --dataset DATASET --max_instances 100 --subset_strategy balanced --result_jsonl results/table2_llamaguard_8bit_balanced_n100.jsonl --checkpoint_every 10 --llamaguard_load_in_8bit --llamaguard_float16
```

Datasets:

- `openaimod`
- `toxicchat`
- `xstest`
- `overkill`
- `beavertail`
- `ours`

Outputs:

- `results/table2_llamaguard_8bit_balanced_n100.jsonl`
- `results/table2_llamaguard_8bit_balanced_n100.csv`

Status label:

- `PARTIAL-HARDWARE-ADAPTED-SUBSET`

Results:

- OpenAI Mod: AUPRC `0.8675734871081862`
- ToxicChat: AUPRC `0.8703995578344464`
- XSTest: AUPRC `0.8924162575272574`
- Overkill: AUPRC `0.8532653121839349`
- BeaverTails: AUPRC `0.6324105945750919`
- TwinSafety/ours: AUPRC `0.8482753310196558`

Interpretation:

- The 8-bit local LlamaGuard path is stable on balanced 100-example subsets across all six Table 2 datasets.
- These rows are subset and hardware-adapted results, not exact paper-resource LlamaGuard rows.
