import csv
from pathlib import Path


DATASET_ORDER = ["OpenAI Mod", "ToxicChat", "XSTest", "Overkill", "BeaverTails", "TwinSafety"]


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(value):
    return float(value)


def fmt(value):
    return f"{value:.4f}"


def model_map(rows, auprc_field):
    mapped = {}
    for row in rows:
        mapped[(row["model"], row["dataset"])] = {
            "auprc": fnum(row[auprc_field]),
            "runtime": fnum(row["runtime_seconds"]),
        }
    return mapped


def make_records():
    local_rows = read_csv("results/table2_local_full.csv")
    subset_rows = read_csv("results/table2_official_style_balanced_n64.csv")

    local = model_map(local_rows, "reproduced_auprc")
    subset = model_map(subset_rows, "subset_auprc")

    configs = [
        {
            "scenario": "Full local-components",
            "source": local,
            "ensemble": "Ensemble",
            "mln": "R2-Guard MLN local-components",
            "pc": "R2-Guard PC-like released AC_inference",
            "note": "Full datasets, but only Detoxify + ToxicChat-T5 components.",
        },
        {
            "scenario": "Official-style balanced n64",
            "source": subset,
            "ensemble": "Ensemble",
            "mln": "R2-Guard MLN",
            "pc": "R2-Guard PC-like",
            "note": "Balanced n64 subset using OpenAI current API + LlamaGuard-8bit + ToxicChat-T5.",
        },
    ]

    records = []
    for cfg in configs:
        for dataset in DATASET_ORDER:
            source = cfg["source"]
            ens = source[(cfg["ensemble"], dataset)]
            mln = source[(cfg["mln"], dataset)]
            pc = source[(cfg["pc"], dataset)]
            speedup = mln["runtime"] / pc["runtime"] if pc["runtime"] > 0 else 0.0
            records.append(
                {
                    "scenario": cfg["scenario"],
                    "dataset": dataset,
                    "ensemble_auprc": ens["auprc"],
                    "mln_auprc": mln["auprc"],
                    "pc_like_auprc": pc["auprc"],
                    "mln_delta_vs_ensemble": mln["auprc"] - ens["auprc"],
                    "pc_delta_vs_ensemble": pc["auprc"] - ens["auprc"],
                    "pc_delta_vs_mln": pc["auprc"] - mln["auprc"],
                    "mln_runtime_seconds": mln["runtime"],
                    "pc_like_runtime_seconds": pc["runtime"],
                    "pc_like_speedup_vs_mln": speedup,
                    "note": cfg["note"],
                }
            )
    return records


def write_csv(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def summarize(records):
    lines = []
    lines.append("# Extension: R2-Guard Reasoning Contribution Analysis")
    lines.append("")
    lines.append(
        "This extension analyzes the R2 reasoning layer by comparing Ensemble, MLN reasoning, "
        "and the released PC-like `--AC_inference` path. It uses only saved result summaries; "
        "no paid APIs, model generation, or raw prompts are used."
    )
    lines.append("")

    for scenario in sorted({r["scenario"] for r in records}):
        subset = [r for r in records if r["scenario"] == scenario]
        avg_ens = sum(r["ensemble_auprc"] for r in subset) / len(subset)
        avg_mln = sum(r["mln_auprc"] for r in subset) / len(subset)
        avg_pc = sum(r["pc_like_auprc"] for r in subset) / len(subset)
        avg_mln_delta = sum(r["mln_delta_vs_ensemble"] for r in subset) / len(subset)
        avg_pc_delta = sum(r["pc_delta_vs_ensemble"] for r in subset) / len(subset)
        avg_speedup = sum(r["pc_like_speedup_vs_mln"] for r in subset) / len(subset)
        mln_wins = sum(1 for r in subset if r["mln_delta_vs_ensemble"] > 0)
        pc_wins = sum(1 for r in subset if r["pc_delta_vs_ensemble"] > 0)
        pc_same = sum(1 for r in subset if abs(r["pc_delta_vs_mln"]) < 1e-12)

        lines.append(f"## {scenario}")
        lines.append("")
        lines.append(f"Note: {subset[0]['note']}")
        lines.append("")
        lines.append("| Dataset | Ensemble | MLN | PC-like | MLN-Ens | PC-Ens | PC/MLN speedup |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for r in subset:
            lines.append(
                "| "
                + " | ".join(
                    [
                        r["dataset"],
                        fmt(r["ensemble_auprc"]),
                        fmt(r["mln_auprc"]),
                        fmt(r["pc_like_auprc"]),
                        fmt(r["mln_delta_vs_ensemble"]),
                        fmt(r["pc_delta_vs_ensemble"]),
                        fmt(r["pc_like_speedup_vs_mln"]),
                    ]
                )
                + " |"
            )
        lines.append("")
        lines.append(
            f"Average AUPRC: Ensemble {fmt(avg_ens)}, MLN {fmt(avg_mln)}, PC-like {fmt(avg_pc)}. "
            f"Average reasoning delta: MLN {fmt(avg_mln_delta)}, PC-like {fmt(avg_pc_delta)}. "
            f"MLN beats Ensemble on {mln_wins}/6 datasets; PC-like beats Ensemble on {pc_wins}/6 datasets. "
            f"PC-like exactly matched MLN AUPRC on {pc_same}/6 datasets and was {fmt(avg_speedup)}x faster on average."
        )
        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "The reasoning layer is not uniformly beneficial under every component configuration. "
        "In the full local-components setting, MLN/PC-like improves over Ensemble on OpenAI Mod, "
        "XSTest, and TwinSafety but decreases AUPRC on ToxicChat, Overkill, and BeaverTails. "
        "In the official-style n64 setting, reasoning improves on Overkill, XSTest, and TwinSafety "
        "but decreases on OpenAI Mod, ToxicChat, and BeaverTails. This supports a cautious conclusion: "
        "R2-style logical inference can add signal, but its benefit depends on the component score distribution "
        "and rule/weight configuration."
    )
    lines.append("")
    lines.append(
        "Across both settings, the released PC-like path produced the same AUPRC as MLN while running faster. "
        "We therefore report it as `PC-like released-code AC_inference`, not as a verified implementation of "
        "the paper's exact spectral-clustering PC algorithm."
    )
    lines.append("")
    return "\n".join(lines)


def main():
    records = make_records()
    write_csv(records, Path("results/extension_reasoning_ablation.csv"))
    Path("results/extension_reasoning_ablation.md").write_text(summarize(records), encoding="utf-8")
    print("Wrote results/extension_reasoning_ablation.csv")
    print("Wrote results/extension_reasoning_ablation.md")


if __name__ == "__main__":
    main()
