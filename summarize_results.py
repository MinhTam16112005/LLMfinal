import argparse
import csv
import json
import sys


def row_name(record):
    if record.get("kind") == "knowledge_model":
        return record["model"]
    if record.get("ensemble_max"):
        return "Ensemble"
    if record.get("ac_inference"):
        return "R2-Guard (PC)"
    return "R2-Guard (MLN)"


def main():
    parser = argparse.ArgumentParser(description="Summarize R2-Guard JSONL result logs as CSV")
    parser.add_argument("jsonl")
    args = parser.parse_args()

    rows = []
    with open(args.jsonl, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                rows.append({
                    "row": row_name(record),
                    "dataset": record.get("dataset"),
                    "auprc": record.get("auprc"),
                    "udr_at_0_5": record.get("udr_at_0_5"),
                    "runtime_seconds": record.get("runtime_seconds"),
                    "num_instances": record.get("num_instances"),
                    "advbench_suffix": record.get("advbench_suffix", ""),
                })

    writer = csv.DictWriter(sys.stdout, fieldnames=[
        "row",
        "dataset",
        "auprc",
        "udr_at_0_5",
        "runtime_seconds",
        "num_instances",
        "advbench_suffix",
    ])
    writer.writeheader()
    writer.writerows(rows)


if __name__ == "__main__":
    main()
