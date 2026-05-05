#!/usr/bin/env bash
set -euo pipefail

mkdir -p cache cache/probs_unsafe_r2guard

python run_knowledge_models.py --knowledge_model_name openai_mod --dataset toxicchat_train --api_key "${OPENAI_API_KEY:?OPENAI_API_KEY is required}"
python run_knowledge_models.py --knowledge_model_name perspective_api --dataset toxicchat_train --api_key "${PERSPECTIVE_API_KEY:?PERSPECTIVE_API_KEY is required}"
python run_knowledge_models.py --knowledge_model_name unitaryai_detoxify --dataset toxicchat_train --batch_size 10

python run_weight_optimization.py --knowledge_model_name openai_mod perspective_api unitaryai_detoxify --dataset pseudo --data_size 200 --batch_size 10 --epochs 5 --lr1 1e-1 --lr2 1e-3
python run_weight_optimization.py --knowledge_model_name openai_mod perspective_api unitaryai_detoxify --dataset toxicchat_train --data_size 200 --pos_ratio 0.3 --batch_size 10 --epochs 3 --lr1 1e-3 --lr2 3e-2

for training_dataset in pseudo toxicchat_train; do
  for dataset in openaimod toxicchat; do
    python knowledge_guardrail_inference.py --knowledge_model_name openai_mod perspective_api unitaryai_detoxify --dataset "$dataset" --num_processes "${NUM_PROCESSES:-300}" --load_knowledge_weights --training_dataset "$training_dataset"
  done
done
