import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "figure2_main_results_data.csv"
OUT_PATH = ROOT / "figure2_main_results.svg"
OUT_PDF_PATH = ROOT / "figure2_main_results.pdf"


def load_rows():
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def metric_matrix(rows, metric):
    datasets = ["MTHv2", "HDRC"]
    methods = [
        ("Best adapted STR", "Rot90(k=3)"),
        ("SAQT", "clean"),
        ("SAQT", "bias"),
    ]
    values = []
    for dataset in datasets:
        row_values = []
        for method, decode in methods:
            matched = [
                row
                for row in rows
                if row["dataset"] == dataset
                and row["method"] == method
                and row["decode"] == decode
            ]
            if len(matched) != 1:
                raise ValueError(f"missing row for {dataset}, {method}, {decode}")
            row_values.append(float(matched[0][metric]))
        values.append(row_values)
    return datasets, [f"{m}\n{d}" for m, d in methods], np.array(values)


def plot_panel(ax, rows, metric):
    datasets, method_labels, values = metric_matrix(rows, metric)
    y = np.arange(len(datasets))
    colors = ["#6f747d", "#2f6f9f", "#c8524a"]
    markers = ["o", "s", "D"]
    offsets = np.array([0.18, 0.0, -0.18])

    for idx, label in enumerate(method_labels):
        ax.scatter(
            values[:, idx],
            y + offsets[idx],
            label=label,
            color=colors[idx],
            marker=markers[idx],
            s=52,
            edgecolor="#222222",
            linewidth=0.45,
            zorder=3,
        )
        for x_value, y_value in zip(values[:, idx], y + offsets[idx]):
            ax.text(
                x_value + 0.28,
                y_value,
                f"{x_value:.2f}",
                va="center",
                ha="left",
                fontsize=8,
                color="#222222",
            )

    for dataset_idx in range(len(datasets)):
        ax.plot(
            values[dataset_idx, :],
            np.full(values.shape[1], y[dataset_idx]),
            color="#c7c7c7",
            linewidth=0.8,
            zorder=1,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(datasets, fontsize=10)
    ax.set_xlabel(f"{metric} (%)", fontsize=10)
    ax.set_xlim(70, 100)
    ax.set_ylim(-0.45, len(datasets) - 0.55)
    ax.invert_yaxis()
    ax.grid(axis="x", linestyle="--", linewidth=0.5, alpha=0.45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)


def main():
    rows = load_rows()
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "svg.fonttype": "none",
            "axes.linewidth": 0.8,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.75), constrained_layout=True)
    plot_panel(axes[0], rows, "AR")
    plot_panel(axes[1], rows, "CR")
    axes[0].set_title("(a) Accuracy rate", loc="left", fontsize=10, fontweight="bold")
    axes[1].set_title("(b) Correct rate", loc="left", fontsize=10, fontweight="bold")
    handles, labels = axes[1].get_legend_handles_labels()
    handles = handles[:3]
    labels = labels[:3]
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, -0.05),
        fontsize=9,
    )
    fig.savefig(OUT_PATH, format="svg", bbox_inches="tight")
    fig.savefig(OUT_PDF_PATH, format="pdf", bbox_inches="tight")
    print(OUT_PATH)
    print(OUT_PDF_PATH)


if __name__ == "__main__":
    main()
