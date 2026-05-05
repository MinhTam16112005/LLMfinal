import argparse
import json
import os
import time
from pathlib import Path

import openai

from data_loading import load_data


class Args:
    max_instances = None
    subset_strategy = "head"
    train_data_size = 200
    advbench_suffix = ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="openaimod")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--batch-size", type=int, required=True)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--sleep", type=float, default=0.0)
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set")
    openai.api_key = api_key

    instances, _ = load_data(args.dataset, Args())
    results = []
    cursor = args.start
    for attempt in range(args.repeat):
        batch = instances[cursor: cursor + args.batch_size]
        t0 = time.time()
        try:
            response = openai.Moderation.create(input=batch)
            elapsed = time.time() - t0
            results.append({
                "attempt": attempt + 1,
                "status": "ok",
                "dataset": args.dataset,
                "start": cursor,
                "batch_size": len(batch),
                "elapsed_seconds": elapsed,
                "returned_results": len(response["results"]),
                "model": response.get("model") if isinstance(response, dict) else None,
            })
            cursor += len(batch)
        except Exception as exc:
            elapsed = time.time() - t0
            results.append({
                "attempt": attempt + 1,
                "status": "failed",
                "dataset": args.dataset,
                "start": cursor,
                "batch_size": len(batch),
                "elapsed_seconds": elapsed,
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            })
            break
        if args.sleep > 0 and attempt + 1 < args.repeat:
            time.sleep(args.sleep)

    Path("results").mkdir(exist_ok=True)
    out = Path(f"results/openai_batch_probe_{args.dataset}_b{args.batch_size}_s{int(args.sleep)}.json")
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
