import argparse
import csv
import json
from pathlib import Path


DATASET_NAMES = {
    "openaimod": "OpenAI Mod",
    "toxicchat": "ToxicChat",
    "xstest": "XSTest",
    "overkill": "Overkill",
    "beavertail": "BeaverTails",
    "ours": "TwinSafety",
}

PAPER_LLAMAGUARD_AUPRC = {
    "OpenAI Mod": 0.788,
    "ToxicChat": 0.698,
    "XSTest": 0.765,
    "Overkill": 0.855,
    "BeaverTails": 0.789,
    "TwinSafety": 0.737,
}


def read_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--model-label", default="LlamaGuard-8bit-local")
    args = parser.parse_args()

    rows = []
    for row in read_jsonl(args.jsonl):
        dataset = DATASET_NAMES.get(row["dataset"], row["dataset"])
        paper = PAPER_LLAMAGUARD_AUPRC.get(dataset, "")
        reproduced = row.get("auprc", "")
        rows.append({
            "model": args.model_label,
            "dataset": dataset,
            "paper_reference_model": "LlamaGuard",
            "paper_auprc": paper,
            "reproduced_auprc": reproduced,
            "delta": reproduced - paper if paper != "" and reproduced != "" else "",
            "status": args.status,
            "num_instances": row.get("num_instances", ""),
            "max_instances": row.get("max_instances", ""),
            "subset_strategy": row.get("subset_strategy", ""),
            "runtime_seconds": row.get("runtime_seconds", ""),
            "notes": "8-bit local RTX 5070 adaptation; not exact paper-resource LlamaGuard",
        })

    fieldnames = [
        "model",
        "dataset",
        "paper_reference_model",
        "paper_auprc",
        "reproduced_auprc",
        "delta",
        "status",
        "num_instances",
        "max_instances",
        "subset_strategy",
        "runtime_seconds",
        "notes",
    ]
    out_path = Path(args.csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
