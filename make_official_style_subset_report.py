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


PAPER = {
    "OpenAI Mod": {
        "OpenAI Mod": 0.870,
        "Ensemble": 0.876,
        "R2-Guard MLN": 0.926,
        "R2-Guard PC-like": 0.924,
    },
    "ToxicChat": {
        "OpenAI Mod": 0.617,
        "Ensemble": 0.882,
        "R2-Guard MLN": 0.903,
        "R2-Guard PC-like": 0.909,
    },
    "XSTest": {
        "OpenAI Mod": 0.778,
        "Ensemble": 0.810,
        "R2-Guard MLN": 0.878,
        "R2-Guard PC-like": 0.882,
    },
    "Overkill": {
        "OpenAI Mod": 0.796,
        "Ensemble": 0.879,
        "R2-Guard MLN": 0.921,
        "R2-Guard PC-like": 0.919,
    },
    "BeaverTails": {
        "OpenAI Mod": 0.728,
        "Ensemble": 0.797,
        "R2-Guard MLN": 0.830,
        "R2-Guard PC-like": 0.825,
    },
    "TwinSafety": {
        "OpenAI Mod": 0.607,
        "Ensemble": 0.653,
        "R2-Guard MLN": 0.758,
        "R2-Guard PC-like": 0.757,
    },
}


def read_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def row_model_name(row):
    if row.get("kind") == "knowledge_model":
        if row.get("model") == "openai_mod":
            return "OpenAI Mod"
        return row.get("model")
    if row.get("ensemble_max"):
        return "Ensemble"
    if row.get("ac_inference"):
        return "R2-Guard PC-like"
    return "R2-Guard MLN"


def row_status(model):
    if model == "OpenAI Mod":
        return "RECONSTRUCTED-CURRENT-API-SUBSET"
    if model == "Ensemble":
        return "OFFICIAL-STYLE-SUBSET"
    if model == "R2-Guard MLN":
        return "OFFICIAL-STYLE-SUBSET"
    if model == "R2-Guard PC-like":
        return "OFFICIAL-STYLE-SUBSET / PC-LIKE-RELEASED-CODE"
    return "SUBSET"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--openai-jsonl", required=True)
    parser.add_argument("--official-jsonl", required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--deviation", required=True)
    args = parser.parse_args()

    combined = read_jsonl(args.openai_jsonl) + read_jsonl(args.official_jsonl)
    rows = []
    for item in combined:
        dataset = DATASET_NAMES.get(item["dataset"], item["dataset"])
        model = row_model_name(item)
        paper = PAPER.get(dataset, {}).get(model, "")
        reproduced = item.get("auprc", "")
        rows.append({
            "model": model,
            "dataset": dataset,
            "paper_auprc": paper,
            "subset_auprc": reproduced,
            "delta_vs_paper_full": reproduced - paper if paper != "" and reproduced != "" else "",
            "status": row_status(model),
            "num_instances": item.get("num_instances", ""),
            "subset_strategy": item.get("subset_strategy", ""),
            "runtime_seconds": item.get("runtime_seconds", ""),
            "notes": "balanced n64 subset; OpenAI current default moderation API; LlamaGuard 8-bit local; not full Table 2",
        })

    order = {"OpenAI Mod": 0, "Ensemble": 1, "R2-Guard MLN": 2, "R2-Guard PC-like": 3}
    rows.sort(key=lambda r: (order.get(r["model"], 99), r["dataset"]))

    fieldnames = [
        "model",
        "dataset",
        "paper_auprc",
        "subset_auprc",
        "delta_vs_paper_full",
        "status",
        "num_instances",
        "subset_strategy",
        "runtime_seconds",
        "notes",
    ]
    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Official-Style Balanced n64 Subset Deviation",
        "",
        "Status: `OFFICIAL-STYLE-SUBSET`",
        "",
        "This is not full Table 2. It is a deadline-safe subset run using 64 balanced examples per dataset.",
        "",
        "Components:",
        "",
        "- OpenAI Mod: current default OpenAI Moderation API, labeled `RECONSTRUCTED-CURRENT-API-SUBSET`",
        "- LlamaGuard: 8-bit local RTX 5070 scores, labeled `PARTIAL-HARDWARE-ADAPTED`",
        "- ToxicChat-T5: local cached full-score source sliced to the same balanced n64 subset",
        "- R2-Guard PC: released-code `--AC_inference`, labeled PC-like rather than exact Algorithm 1 spectral clustering",
        "",
        "Outputs:",
        "",
        f"- `{args.openai_jsonl}`",
        f"- `{args.official_jsonl}`",
        f"- `{args.csv}`",
        "",
        "| Model | Dataset | Paper full AUPRC | Subset AUPRC | Status |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        paper = row["paper_auprc"]
        subset = row["subset_auprc"]
        lines.append(f"| {row['model']} | {row['dataset']} | {paper} | {subset:.6f} | {row['status']} |")
    Path(args.deviation).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
