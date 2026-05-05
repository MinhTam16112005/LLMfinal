import argparse
import json
from pathlib import Path

from data_loading import load_data
from utils import score_cache_suffix


class Args:
    def __init__(self, max_instances, subset_strategy):
        self.max_instances = max_instances
        self.subset_strategy = subset_strategy
        self.train_data_size = 200
        self.advbench_suffix = ""


def selected_indices(dataset, args):
    full_args = Args(None, "head")
    subset_args = Args(args.max_instances, args.subset_strategy)
    full_instances, _ = load_data(dataset, full_args)
    subset_instances, _ = load_data(dataset, subset_args)
    positions = {}
    for idx, instance in enumerate(full_instances):
        positions.setdefault(instance, []).append(idx)
    used = {}
    indices = []
    for instance in subset_instances:
        seen = used.get(instance, 0)
        matches = positions[instance]
        indices.append(matches[seen])
        used[instance] = seen + 1
    return indices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--max-instances", type=int, required=True)
    parser.add_argument("--subset-strategy", choices=["head", "balanced"], required=True)
    args = parser.parse_args()

    subset_args = Args(args.max_instances, args.subset_strategy)
    suffix = score_cache_suffix(subset_args)
    indices = selected_indices(args.dataset, args)
    for model in args.models:
        src = Path(f"cache/{model}_{args.dataset}_scores.json")
        dst = Path(f"cache/{model}_{args.dataset}_scores{suffix}.json")
        if not src.exists():
            raise FileNotFoundError(src)
        scores = json.loads(src.read_text(encoding="utf-8"))
        subset_scores = {key: [values[idx] for idx in indices] for key, values in scores.items()}
        dst.write_text(json.dumps(subset_scores), encoding="utf-8")
        print(f"{src} -> {dst} ({len(indices)} rows)")


if __name__ == "__main__":
    main()
