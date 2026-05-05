#!/usr/bin/env bash
set -euo pipefail

DATASETS=(openaimod toxicchat xstest overkill beavertail ours)
BASELINE_MODELS=(unitaryai_detoxify perspective_api azure openai_mod llamaguard toxicchat-T5)

mkdir -p cache cache/probs_unsafe_r2guard

for dataset in "${DATASETS[@]}"; do
  for model in "${BASELINE_MODELS[@]}"; do
    case "$model" in
      openai_mod)
        python run_knowledge_models.py --knowledge_model_name "$model" --dataset "$dataset" --api_key "${OPENAI_API_KEY:?OPENAI_API_KEY is required}"
        ;;
      perspective_api)
        python run_knowledge_models.py --knowledge_model_name "$model" --dataset "$dataset" --api_key "${PERSPECTIVE_API_KEY:?PERSPECTIVE_API_KEY is required}"
        ;;
      azure)
        python run_knowledge_models.py --knowledge_model_name "$model" --dataset "$dataset" --api_key "${AZURE_CONTENT_SAFETY_KEY:?AZURE_CONTENT_SAFETY_KEY is required}" --batch_size 10
        ;;
      unitaryai_detoxify)
        python run_knowledge_models.py --knowledge_model_name "$model" --dataset "$dataset" --batch_size 10
        ;;
      *)
        python run_knowledge_models.py --knowledge_model_name "$model" --dataset "$dataset"
        ;;
    esac
  done

  python knowledge_guardrail_inference.py --knowledge_model_name openai_mod llamaguard toxicchat-T5 --dataset "$dataset" --num_processes "${NUM_PROCESSES:-300}"
  python knowledge_guardrail_inference.py --knowledge_model_name openai_mod llamaguard toxicchat-T5 --dataset "$dataset" --num_processes "${NUM_PROCESSES:-300}" --AC_inference
  python knowledge_guardrail_inference.py --knowledge_model_name openai_mod llamaguard toxicchat-T5 --dataset "$dataset" --num_processes "${NUM_PROCESSES:-300}" --ensemble_max
done
