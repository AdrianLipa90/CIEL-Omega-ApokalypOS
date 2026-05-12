from __future__ import annotations

import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def read_matrix(path: Path):
    rows = list(csv.reader(path.open(encoding="utf-8")))
    cols = rows[0][1:]
    labels = [r[0] for r in rows[1:]]
    data = np.array([[float(x) for x in r[1:]] for r in rows[1:]])
    return labels, cols, data


def heatmap(csv_rel: str, output_rel: str, title: str):
    labels, cols, data = read_matrix(ROOT / csv_rel)
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(data)
    ax.set_xticks(range(len(cols)), labels=cols, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)), labels=labels)
    ax.set_title(title)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    out = ROOT / output_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)


def graph_preview(output_rel: str):
    nodes = {
        "water": (0, 0), "life": (1, 1), "flow": (1, 0.35), "cleansing": (1, -0.35),
        "danger": (1, -1), "drought": (-1, -0.6), "fire": (-1, 0.6)
    }
    edges = [("water","life"),("water","flow"),("water","cleansing"),("water","danger"),("water","drought"),("water","fire")]
    fig, ax = plt.subplots(figsize=(8,6))
    for a,b in edges:
        x1,y1=nodes[a]; x2,y2=nodes[b]
        ax.annotate("", xy=(x2,y2), xytext=(x1,y1), arrowprops={"arrowstyle":"->"})
    for n,(x,y) in nodes.items():
        ax.scatter([x],[y], s=300)
        ax.text(x, y+0.08, n, ha="center")
    ax.set_title("Water concept graph")
    ax.axis("off")
    fig.tight_layout()
    out = ROOT / output_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    heatmap("data/heatmaps/grammar_operator_distance.csv", "outputs/heatmaps/grammar_operator_distance.png", "Grammar operator distance")
    heatmap("data/heatmaps/cross_language_semantic_similarity.csv", "outputs/heatmaps/cross_language_semantic_similarity.png", "Cross-language semantic similarity")
    heatmap("data/heatmaps/water_semantic_affective_gradient.csv", "outputs/heatmaps/water_semantic_affective_gradient.png", "Water semantic-affective gradient")
    graph_preview("outputs/graphs/water_concept_graph.png")
