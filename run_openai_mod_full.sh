#!/usr/bin/env bash
set -euo pipefail

datasets=(openaimod toxicchat xstest overkill beavertail ours)

for dataset in "${datasets[@]}"; do
  python3.10 run_knowledge_models.py \
    --knowledge_model_name openai_mod \
    --dataset "${dataset}" \
    --openai_moderation_model default \
    --api_batch_size "${API_BATCH_SIZE:-32}" \
    --checkpoint_every "${CHECKPOINT_EVERY:-32}" \
    --max_retries "${MAX_RETRIES:-5}" \
    --retry_sleep "${RETRY_SLEEP:-2}" \
    --rate_limit_sleep "${RATE_LIMIT_SLEEP:-60}" \
    --api_sleep "${API_SLEEP:-0}" \
    --result_jsonl results/table2_openai_mod_full.jsonl
done
