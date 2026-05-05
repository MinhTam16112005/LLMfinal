import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--n", type=int, required=True)
    args = parser.parse_args()

    for model in args.models:
        src = Path(f"cache/{model}_{args.dataset}_scores.json")
        dst = Path(f"cache/{model}_{args.dataset}_scores_n{args.n}.json")
        if not src.exists():
            raise FileNotFoundError(src)
        scores = json.loads(src.read_text(encoding="utf-8"))
        sliced = {key: value[: args.n] for key, value in scores.items()}
        dst.write_text(json.dumps(sliced), encoding="utf-8")
        print(f"{src} -> {dst}")


if __name__ == "__main__":
    main()
