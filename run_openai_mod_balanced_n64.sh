#!/usr/bin/env bash
set -euo pipefail

datasets=(openaimod toxicchat xstest overkill beavertail ours)

for dataset in "${datasets[@]}"; do
  python3.10 run_knowledge_models.py \
    --knowledge_model_name openai_mod \
    --dataset "${dataset}" \
    --max_instances 64 \
    --subset_strategy balanced \
    --ignore_cache \
    --openai_moderation_model default \
    --api_batch_size 64 \
    --checkpoint_every 64 \
    --max_retries "${MAX_RETRIES:-2}" \
    --retry_sleep "${RETRY_SLEEP:-2}" \
    --rate_limit_sleep "${RATE_LIMIT_SLEEP:-70}" \
    --api_sleep "${API_SLEEP:-70}" \
    --result_jsonl results/table2_openai_mod_currentapi_balanced_n64.jsonl
done
