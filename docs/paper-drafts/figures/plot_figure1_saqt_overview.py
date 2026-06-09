from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "figure1_saqt_overview.svg"
OUT_PDF_PATH = ROOT / "figure1_saqt_overview.pdf"


def box(ax, xy, wh, text, fc="#f7f7f7", ec="#222222", lw=1.0, fs=8.5):
    rect = Rectangle(xy, wh[0], wh[1], facecolor=fc, edgecolor=ec, linewidth=lw)
    ax.add_patch(rect)
    ax.text(
        xy[0] + wh[0] / 2,
        xy[1] + wh[1] / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        wrap=True,
    )
    return rect


def arrow(ax, start, end, text=None, rad=0.0):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=1.0,
        color="#222222",
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(patch)
    if text:
        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2 + 0.18,
            text,
            ha="center",
            va="center",
            fontsize=7.5,
        )


def draw_text_crop(ax):
    box(ax, (0.4, 3.25), (1.0, 2.5), "Vertical\nline image", fc="#fff8e6")
    for idx, y in enumerate([5.25, 4.75, 4.25, 3.75]):
        rect = Rectangle((0.62, y), 0.55, 0.32, fill=False, edgecolor="#d62728", linewidth=0.9)
        ax.add_patch(rect)
    ax.text(0.9, 5.95, "line-level\ntranscription", ha="center", fontsize=7.5)
    ax.text(0.9, 3.02, "boxes: training only", ha="center", fontsize=7.5, color="#b22222")


def main():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "svg.fonttype": "none",
            "axes.linewidth": 0.8,
        }
    )
    fig, ax = plt.subplots(figsize=(9.2, 4.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.6)
    ax.axis("off")

    ax.text(0.35, 6.35, "(a) Structure learning", fontsize=10, fontweight="bold")
    draw_text_crop(ax)
    box(ax, (1.9, 4.0), (1.25, 0.85), "Visual\nbackbone", fc="#e8f1fb")
    box(ax, (3.55, 3.75), (1.45, 1.25), "Transformer\nqueries", fc="#e8f1fb")
    box(ax, (5.35, 4.1), (1.25, 0.75), "class logits\n+ boxes", fc="#eef7ee")
    box(ax, (5.35, 3.05), (1.25, 0.75), "matching loss\n+ query budget", fc="#f3ecff")
    arrow(ax, (1.4, 4.5), (1.9, 4.45))
    arrow(ax, (3.15, 4.45), (3.55, 4.38))
    arrow(ax, (5.0, 4.38), (5.35, 4.48))
    arrow(ax, (5.95, 4.1), (5.95, 3.8))

    ax.text(0.35, 2.55, "(b) Charset adaptation and CTC recognition", fontsize=10, fontweight="bold")
    box(ax, (0.4, 1.25), (1.45, 0.85), "reference charset\nA_s", fc="#f7f7f7")
    box(ax, (2.35, 1.25), (1.55, 0.85), "target charset\nA_t", fc="#f7f7f7")
    box(ax, (4.35, 1.3), (1.4, 0.75), "adapted\nclassifier", fc="#eef7ee")
    box(ax, (6.2, 1.3), (1.25, 0.75), "sort queries\nby y", fc="#e8f1fb")
    box(ax, (7.9, 1.3), (1.35, 0.75), "CTC loss /\ngreedy decode", fc="#fff2e8")
    arrow(ax, (1.85, 1.68), (2.35, 1.68), "shared rows copied")
    arrow(ax, (3.9, 1.68), (4.35, 1.68), "new rows initialized")
    arrow(ax, (5.75, 1.68), (6.2, 1.68))
    arrow(ax, (7.45, 1.68), (7.9, 1.68))
    ax.text(8.55, 0.82, "Output text string", ha="center", fontsize=8.5)
    ax.text(8.55, 2.35, "No character boxes at inference", ha="center", fontsize=8.5, color="#b22222")

    fig.savefig(OUT_PATH, format="svg", bbox_inches="tight")
    fig.savefig(OUT_PDF_PATH, format="pdf", bbox_inches="tight")
    print(OUT_PATH)
    print(OUT_PDF_PATH)


if __name__ == "__main__":
    main()
