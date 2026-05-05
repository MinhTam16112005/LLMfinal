import argparse
import csv
import json
import os
import platform
import subprocess
from pathlib import Path


TABLE2_TARGETS = {
    ("Detoxify", "OpenAI Mod"): 0.780,
    ("Detoxify", "ToxicChat"): 0.386,
    ("Detoxify", "XSTest"): 0.660,
    ("Detoxify", "Overkill"): 0.462,
    ("Detoxify", "BeaverTails"): 0.636,
    ("Detoxify", "TwinSafety"): 0.598,
    ("Perspective", "OpenAI Mod"): 0.787,
    ("Perspective", "ToxicChat"): 0.499,
    ("Perspective", "XSTest"): 0.671,
    ("Perspective", "Overkill"): 0.543,
    ("Perspective", "BeaverTails"): 0.761,
    ("Perspective", "TwinSafety"): 0.583,
    ("Azure", "OpenAI Mod"): 0.743,
    ("Azure", "ToxicChat"): 0.553,
    ("Azure", "XSTest"): 0.722,
    ("Azure", "Overkill"): 0.700,
    ("Azure", "BeaverTails"): 0.787,
    ("Azure", "TwinSafety"): 0.653,
    ("CoT", "OpenAI Mod"): 0.856,
    ("CoT", "ToxicChat"): 0.592,
    ("CoT", "XSTest"): 0.743,
    ("CoT", "Overkill"): 0.793,
    ("CoT", "BeaverTails"): 0.687,
    ("CoT", "TwinSafety"): 0.599,
    ("OpenAI Mod", "OpenAI Mod"): 0.870,
    ("OpenAI Mod", "ToxicChat"): 0.617,
    ("OpenAI Mod", "XSTest"): 0.778,
    ("OpenAI Mod", "Overkill"): 0.796,
    ("OpenAI Mod", "BeaverTails"): 0.728,
    ("OpenAI Mod", "TwinSafety"): 0.607,
    ("LlamaGuard", "OpenAI Mod"): 0.788,
    ("LlamaGuard", "ToxicChat"): 0.698,
    ("LlamaGuard", "XSTest"): 0.765,
    ("LlamaGuard", "Overkill"): 0.855,
    ("LlamaGuard", "BeaverTails"): 0.789,
    ("LlamaGuard", "TwinSafety"): 0.737,
    ("ToxicChat-T5", "OpenAI Mod"): 0.787,
    ("ToxicChat-T5", "ToxicChat"): 0.885,
    ("ToxicChat-T5", "XSTest"): 0.819,
    ("ToxicChat-T5", "Overkill"): 0.801,
    ("ToxicChat-T5", "BeaverTails"): 0.761,
    ("ToxicChat-T5", "TwinSafety"): 0.607,
    ("Ensemble", "OpenAI Mod"): 0.876,
    ("Ensemble", "ToxicChat"): 0.882,
    ("Ensemble", "XSTest"): 0.810,
    ("Ensemble", "Overkill"): 0.879,
    ("Ensemble", "BeaverTails"): 0.797,
    ("Ensemble", "TwinSafety"): 0.653,
    ("R2-Guard MLN", "OpenAI Mod"): 0.926,
    ("R2-Guard MLN", "ToxicChat"): 0.903,
    ("R2-Guard MLN", "XSTest"): 0.878,
    ("R2-Guard MLN", "Overkill"): 0.921,
    ("R2-Guard MLN", "BeaverTails"): 0.830,
    ("R2-Guard MLN", "TwinSafety"): 0.758,
    ("R2-Guard PC", "OpenAI Mod"): 0.924,
    ("R2-Guard PC", "ToxicChat"): 0.909,
    ("R2-Guard PC", "XSTest"): 0.882,
    ("R2-Guard PC", "Overkill"): 0.919,
    ("R2-Guard PC", "BeaverTails"): 0.825,
    ("R2-Guard PC", "TwinSafety"): 0.757,
}

TABLE4_TARGETS = {
    ("ToxicChat-T5", "Benign"): 0.541,
    ("ToxicChat-T5", "GCG-U1"): 0.395,
    ("ToxicChat-T5", "GCG-U2"): 0.261,
    ("ToxicChat-T5", "GCG-V"): 0.451,
    ("ToxicChat-T5", "GCG-L"): 0.279,
    ("ToxicChat-T5", "GCG-R"): 0.382,
    ("ToxicChat-T5", "AutoDAN"): 0.663,
    ("ToxicChat-T5", "PAIR"): 0.314,
    ("ToxicChat-T5", "TAP"): 0.056,
    ("OpenAI Mod", "Benign"): 0.645,
    ("OpenAI Mod", "GCG-U1"): 0.512,
    ("OpenAI Mod", "GCG-U2"): 0.516,
    ("OpenAI Mod", "GCG-V"): 0.524,
    ("OpenAI Mod", "GCG-L"): 0.526,
    ("OpenAI Mod", "GCG-R"): 0.505,
    ("OpenAI Mod", "AutoDAN"): 0.068,
    ("OpenAI Mod", "PAIR"): 0.359,
    ("OpenAI Mod", "TAP"): 0.061,
    ("LlamaGuard", "Benign"): 0.824,
    ("LlamaGuard", "GCG-U1"): 0.685,
    ("LlamaGuard", "GCG-U2"): 0.603,
    ("LlamaGuard", "GCG-V"): 0.711,
    ("LlamaGuard", "GCG-L"): 0.362,
    ("LlamaGuard", "GCG-R"): 0.612,
    ("LlamaGuard", "AutoDAN"): 0.738,
    ("LlamaGuard", "PAIR"): 0.491,
    ("LlamaGuard", "TAP"): 0.101,
    ("Ensemble", "Benign"): 0.883,
    ("Ensemble", "GCG-U1"): 0.782,
    ("Ensemble", "GCG-U2"): 0.744,
    ("Ensemble", "GCG-V"): 0.812,
    ("Ensemble", "GCG-L"): 0.688,
    ("Ensemble", "GCG-R"): 0.656,
    ("Ensemble", "AutoDAN"): 0.802,
    ("Ensemble", "PAIR"): 0.557,
    ("Ensemble", "TAP"): 0.278,
    ("R2-Guard MLN", "Benign"): 1.000,
    ("R2-Guard MLN", "GCG-U1"): 1.000,
    ("R2-Guard MLN", "GCG-U2"): 1.000,
    ("R2-Guard MLN", "GCG-V"): 1.000,
    ("R2-Guard MLN", "GCG-L"): 1.000,
    ("R2-Guard MLN", "GCG-R"): 0.973,
    ("R2-Guard MLN", "AutoDAN"): 0.948,
    ("R2-Guard MLN", "PAIR"): 0.581,
    ("R2-Guard MLN", "TAP"): 0.375,
    ("R2-Guard PC", "Benign"): 1.000,
    ("R2-Guard PC", "GCG-U1"): 1.000,
    ("R2-Guard PC", "GCG-U2"): 1.000,
    ("R2-Guard PC", "GCG-V"): 1.000,
    ("R2-Guard PC", "GCG-L"): 1.000,
    ("R2-Guard PC", "GCG-R"): 0.973,
    ("R2-Guard PC", "AutoDAN"): 0.945,
    ("R2-Guard PC", "PAIR"): 0.583,
    ("R2-Guard PC", "TAP"): 0.369,
}

TABLE5_TARGETS = {
    "MLN reasoning": (0.869, 0.1123),
    "PC reasoning": (0.869, 0.0062),
}

MODEL_NAMES = {
    "unitaryai_detoxify": "Detoxify",
    "toxicchat-T5": "ToxicChat-T5",
}

DATASET_NAMES = {
    "toxicchat": "ToxicChat",
    "xstest": "XSTest",
    "overkill": "Overkill",
    "beavertail": "BeaverTails",
    "ours": "TwinSafety",
    "openaimod": "OpenAI Mod",
}


def read_jsonl(path):
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run_text(command):
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNKNOWN"


def better_row(candidate, existing):
    if existing is None:
        return True
    candidate_strategy = candidate.get("subset_strategy") or "head"
    existing_strategy = existing.get("subset_strategy") or "head"
    if candidate_strategy == "balanced" and existing_strategy != "balanced":
        return True
    if candidate_strategy != "balanced" and existing_strategy == "balanced":
        return False
    return (candidate.get("max_instances") or 0) >= (existing.get("max_instances") or 0)


def produced_table2(rows):
    produced = {}
    for row in rows:
        if row.get("kind") == "knowledge_model":
            model = MODEL_NAMES.get(row["model"], row["model"])
        elif row.get("kind") == "r2guard_inference":
            if row.get("ensemble_max"):
                model = "Ensemble"
            elif row.get("ac_inference"):
                model = "R2-Guard PC"
            else:
                model = "R2-Guard MLN"
        else:
            continue
        dataset = DATASET_NAMES.get(row.get("dataset"), row.get("dataset"))
        key = (model, dataset)
        if better_row(row, produced.get(key)):
            produced[key] = row
    return produced


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_table2(rows):
    produced = produced_table2(rows)
    out = []
    for (model, dataset), target in TABLE2_TARGETS.items():
        row = produced.get((model, dataset))
        if row:
            reproduced = row["auprc"]
            max_instances = row.get("max_instances")
            subset_strategy = row.get("subset_strategy") or ""
            status = "PARTIAL" if max_instances else "EXACT"
            note = f"{dataset} subset ({subset_strategy}); no paid APIs; local/free models only" if max_instances else ""
            delta = reproduced - target
        else:
            reproduced = ""
            max_instances = ""
            subset_strategy = ""
            status = "BLOCKED"
            delta = ""
            note = blocker_note(model, dataset)
        out.append({
            "model": model,
            "dataset": dataset,
            "paper_auprc": target,
            "reproduced_auprc": reproduced,
            "delta": delta,
            "status": status,
            "max_instances": max_instances,
            "subset_strategy": subset_strategy,
            "notes": note,
        })
    return out


def blocker_note(model, dataset):
    if model in {"Perspective", "Azure", "OpenAI Mod"}:
        return "Blocked by budget/API policy unless explicitly approved; no full cached scores in repo"
    if model == "CoT":
        return "CoT demos/runner are not released in the repo"
    if model == "LlamaGuard":
        return "Hugging Face gated model access/cache required"
    if model in {"Ensemble", "R2-Guard MLN", "R2-Guard PC"}:
        return "Requires all selected component score caches for the full dataset"
    return "Full dataset/cache not produced in this budget-capped run"


def build_table4():
    out = []
    for (model, attack), target in TABLE4_TARGETS.items():
        out.append({
            "model": model,
            "attack": attack,
            "paper_udr": target,
            "reproduced_udr": "",
            "delta": "",
            "status": "BLOCKED",
            "notes": "Jailbreak reproduction is blocked under budget policy and missing exact repo-provided PAIR/TAP/AutoDAN/GCG-R artifacts",
        })
    return out


def build_table5(rows):
    out = []
    for method, (target_auprc, target_runtime) in TABLE5_TARGETS.items():
        ac_inference = method.startswith("PC")
        matching = [
            row for row in rows
            if row.get("kind") == "r2guard_inference"
            and not row.get("ensemble_max")
            and not row.get("ensemble_avg")
            and bool(row.get("ac_inference")) == ac_inference
        ]
        if matching:
            runtime_per_instance = sum(row["runtime_seconds"] / row["num_instances"] for row in matching) / len(matching)
            status = "PARTIAL"
            reproduced_auprc = sum(row["auprc"] for row in matching) / len(matching)
            delta_auprc = reproduced_auprc - target_auprc
            delta_runtime = runtime_per_instance - target_runtime
            max_instances = ",".join(sorted({str(row.get("max_instances")) for row in matching}))
            subset_strategy = ",".join(sorted({str(row.get("subset_strategy") or "") for row in matching}))
            datasets = ",".join(sorted({DATASET_NAMES.get(row.get("dataset"), row.get("dataset")) for row in matching}))
            note = f"Average over local subsets ({datasets}) with two local components, not paper's six-dataset/three-component average"
        else:
            runtime_per_instance = ""
            status = "BLOCKED"
            reproduced_auprc = ""
            delta_auprc = ""
            delta_runtime = ""
            max_instances = ""
            subset_strategy = ""
            note = "Requires full Table 2 component caches"
        out.append({
            "method": method,
            "paper_average_auprc": target_auprc,
            "reproduced_auprc": reproduced_auprc,
            "delta_auprc": delta_auprc,
            "paper_runtime_per_instance": target_runtime,
            "reproduced_runtime_per_instance": runtime_per_instance,
            "delta_runtime_per_instance": delta_runtime,
            "status": status,
            "max_instances": max_instances,
            "subset_strategy": subset_strategy,
            "notes": note,
        })
    return out


def write_deviation_report(path, table2_rows, table4_rows, table5_rows):
    partial = [r for r in table2_rows + table5_rows if r["status"] == "PARTIAL"]
    blocked = [r for r in table2_rows + table4_rows + table5_rows if r["status"] == "BLOCKED"]
    lines = [
        "# Deviation Report",
        "",
        "## Summary",
        "",
        f"- Produced metric rows: {len(partial)} partial rows.",
        f"- Blocked metric rows: {len(blocked)} rows.",
        "- No paid API calls are included in the current budget-capped reproduction.",
        "- Current produced values are not exact Table 2/Table 5 values because they use balanced 100-example local subsets and two local components.",
        "",
        "## Produced Values",
        "",
    ]
    for row in partial:
        name = row.get("model") or row.get("method")
        dataset = row.get("dataset")
        value = row.get("reproduced_auprc")
        delta = row.get("delta") if "delta" in row else row.get("delta_auprc")
        label = f"{name} on {dataset}" if dataset else name
        lines.append(f"- {label}: reproduced AUPRC {value}, delta {delta}, status {row['status']}.")
    lines.extend([
        "",
        "## Main Blockers",
        "",
        "- OpenAI, Azure, and Perspective rows require external APIs and are blocked under the $10 budget unless explicitly approved.",
        "- LlamaGuard requires gated Hugging Face access and/or a cached checkpoint.",
        "- CoT baseline is not released as runnable code with the manual demonstrations described in the paper.",
        "- Full R2-Guard Table 2 needs complete component score caches for OpenAI Mod, LlamaGuard, and ToxicChat-T5 on all six datasets.",
        "- Table 4 jailbreak reproduction is blocked because exact generated PAIR/TAP/AutoDAN/GCG-R artifacts are not fully present and new harmful jailbreak generation is out of scope.",
        "- Paper PC reasoning says spectral clustering; released code path uses `--AC_inference` graph partitioning, so it is documented as PC-like unless the missing spectral clustering implementation is recovered.",
        "",
        "## Environment Snapshot",
        "",
        f"- OS: {platform.platform()}",
        f"- Python used for report generation: {platform.python_version()}",
        f"- Git commit: {run_text(['git', 'rev-parse', 'HEAD'])}",
        f"- Docker images are documented in `REPRODUCIBILITY.md`; local smoke run used `r2guard-local5070:latest`.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reproduction_md(path):
    path.write_text(
        """# R2-Guard Reproduction Log

This file records the current budget-capped reproduction state.

## Repository

- Official repo: https://github.com/kangmintong/R-2-Guard
- Local commit: 8cc3ce3f103892886e5e8261bf41b8929f7021e0

## Budget Policy

- Total budget limit: $10.
- Paid API calls are not allowed unless explicitly approved.
- OpenAI, Azure, Perspective, and jailbreak tables are marked `BLOCKED` when they require API calls or missing artifacts.

## Completed Minimal Run

Command:

```bash
docker run --rm --gpus all -v \"${PWD}:/workspace\" -v \"${PWD}/hf_cache:/root/.cache/huggingface\" -v \"${PWD}/torch_cache:/root/.cache/torch\" -w /workspace -e NUM_PROCESSES=4 r2guard-local5070:latest python3.10 repro_runner.py --stage minimal-local --datasets toxicchat xstest overkill ours --max_instances 100 --subset_strategy balanced --result_jsonl results/minimal_local_balanced.jsonl
```

Produced:

- Detoxify on balanced 100-example subsets
- ToxicChat-T5 on balanced 100-example subsets
- Ensemble over Detoxify + ToxicChat-T5
- R2-Guard MLN over Detoxify + ToxicChat-T5 with uniform aggregation
- R2-Guard PC-like `--AC_inference` over the same components

The run used local/free model paths and did not pass API keys into Docker.

## Outputs

- `results/minimal_local_balanced.jsonl`
- `results/table2_reproduction.csv`
- `results/table4_reproduction.csv`
- `results/table5_reproduction.csv`
- `results/deviation_report.md`
- `results/environment_snapshot.txt`
- `requirements-freeze.txt`

See `REPRODUCIBILITY.md` for the broader runbook and blocker inventory.
""",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimal_jsonl", default="results/minimal_local.jsonl")
    parser.add_argument("--jsonl", nargs="+", default=None)
    parser.add_argument("--results_dir", default="results")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    jsonl_paths = args.jsonl or [args.minimal_jsonl]
    rows = []
    for jsonl_path in jsonl_paths:
        rows.extend(read_jsonl(Path(jsonl_path)))

    table2 = build_table2(rows)
    table4 = build_table4()
    table5 = build_table5(rows)

    write_csv(results_dir / "table2_reproduction.csv", table2, [
        "model", "dataset", "paper_auprc", "reproduced_auprc", "delta", "status", "max_instances", "subset_strategy", "notes"
    ])
    write_csv(results_dir / "table4_reproduction.csv", table4, [
        "model", "attack", "paper_udr", "reproduced_udr", "delta", "status", "notes"
    ])
    write_csv(results_dir / "table5_reproduction.csv", table5, [
        "method", "paper_average_auprc", "reproduced_auprc", "delta_auprc",
        "paper_runtime_per_instance", "reproduced_runtime_per_instance",
        "delta_runtime_per_instance", "status", "max_instances", "subset_strategy", "notes"
    ])
    write_deviation_report(results_dir / "deviation_report.md", table2, table4, table5)
    write_reproduction_md(Path("REPRODUCTION.md"))


if __name__ == "__main__":
    main()
