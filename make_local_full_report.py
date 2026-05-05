import argparse
import csv
import json
from pathlib import Path

from make_reproduction_reports import DATASET_NAMES, TABLE2_TARGETS, write_csv


LOCAL_MODELS = {
    "unitaryai_detoxify": "Detoxify",
    "toxicchat-T5": "ToxicChat-T5",
}

LOCAL_DATASETS = ["OpenAI Mod", "ToxicChat", "XSTest", "Overkill", "BeaverTails", "TwinSafety"]


def read_jsonl(paths):
    rows = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def row_model_name(row):
    if row.get("kind") == "knowledge_model":
        return LOCAL_MODELS.get(row["model"], row["model"])
    if row.get("kind") == "r2guard_inference":
        if row.get("ensemble_max"):
            return "Ensemble"
        if row.get("ac_inference"):
            return "R2-Guard PC-like released AC_inference"
        return "R2-Guard MLN local-components"
    return None


def row_dataset_name(row):
    return DATASET_NAMES.get(row.get("dataset"), row.get("dataset"))


def collect(rows):
    out = {}
    for row in rows:
        model = row_model_name(row)
        dataset = row_dataset_name(row)
        if not model or not dataset:
            continue
        if row.get("max_instances"):
            continue
        out[(model, dataset)] = row
    return out


def status_for(model, dataset, row):
    if not row:
        if model in {"Detoxify", "ToxicChat-T5"}:
            return "BLOCKED", "Full local score cache/result not produced yet"
        return "BLOCKED", "Requires full local component caches first"
    if model in {"Detoxify", "ToxicChat-T5"}:
        return "EXACT-LOCAL", "Full dataset and same local model family as paper; no paid API"
    return "PARTIAL-COMPONENT", "Full dataset, but R2-Guard uses only Detoxify + ToxicChat-T5 rather than paper OpenAI Mod + LlamaGuard + ToxicChat-T5"


def build_table(rows):
    produced = collect(rows)
    table = []
    local_models = [
        "Detoxify",
        "ToxicChat-T5",
        "Ensemble",
        "R2-Guard MLN local-components",
        "R2-Guard PC-like released AC_inference",
    ]
    paper_lookup = {
        "R2-Guard MLN local-components": "R2-Guard MLN",
        "R2-Guard PC-like released AC_inference": "R2-Guard PC",
    }
    for model in local_models:
        for dataset in LOCAL_DATASETS:
            row = produced.get((model, dataset))
            paper_model = paper_lookup.get(model, model)
            paper_value = TABLE2_TARGETS.get((paper_model, dataset), "")
            reproduced = row.get("auprc") if row else ""
            delta = reproduced - paper_value if row and paper_value != "" else ""
            status, note = status_for(model, dataset, row)
            table.append({
                "model": model,
                "dataset": dataset,
                "paper_reference_model": paper_model,
                "paper_auprc": paper_value,
                "reproduced_auprc": reproduced,
                "delta": delta,
                "status": status,
                "num_instances": row.get("num_instances") if row else "",
                "runtime_seconds": row.get("runtime_seconds") if row else "",
                "notes": note,
            })
    return table


def write_deviation(path, table):
    produced = [row for row in table if row["status"] != "BLOCKED"]
    blocked = [row for row in table if row["status"] == "BLOCKED"]
    lines = [
        "# Local Full Table 2 Deviation",
        "",
        "This report uses full datasets where available and no paid APIs.",
        "",
        f"- Produced rows: {len(produced)}",
        f"- Blocked rows: {len(blocked)}",
        "- `EXACT-LOCAL` means same full dataset and same local model family as the paper row.",
        "- `PARTIAL-COMPONENT` means full dataset but not the official paper R2-Guard component set.",
        "- PC result is labeled `PC-like released AC_inference`, not exact Algorithm 1 spectral clustering.",
        "",
        "## Produced Rows",
        "",
    ]
    for row in produced:
        lines.append(
            f"- {row['model']} / {row['dataset']}: AUPRC={row['reproduced_auprc']}, "
            f"paper_ref={row['paper_auprc']}, delta={row['delta']}, status={row['status']}"
        )
    lines.extend([
        "",
        "## Blockers",
        "",
        "- Official R2-Guard full Table 2 remains blocked until OpenAI Mod, LlamaGuard, and ToxicChat-T5 full score caches exist for all six datasets.",
        "- OpenAI/Azure/Perspective rows remain blocked by budget policy unless explicitly approved.",
        "- LlamaGuard remains blocked unless gated Hugging Face access/checkpoint is available.",
        "- Table 4 jailbreak reproduction remains blocked by missing exact artifacts and the no-new-jailbreak-generation constraint.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", nargs="+", required=True)
    parser.add_argument("--csv", default="results/table2_local_full.csv")
    parser.add_argument("--report", default="results/table2_local_full_deviation.md")
    args = parser.parse_args()

    rows = read_jsonl(args.jsonl)
    table = build_table(rows)
    write_csv(Path(args.csv), table, [
        "model", "dataset", "paper_reference_model", "paper_auprc", "reproduced_auprc",
        "delta", "status", "num_instances", "runtime_seconds", "notes"
    ])
    write_deviation(Path(args.report), table)


if __name__ == "__main__":
    main()
