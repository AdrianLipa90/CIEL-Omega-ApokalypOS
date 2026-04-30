"""ASCII terminal renderer for the Poincaré disk layout — for debugging and verification."""

from __future__ import annotations

import math

from .layout import build_layout, DiskLayout

_WIDTH = 60
_HEIGHT = 30

_NODE_CHARS = {
    "sector": "@",
    "entity": ".",
}

_HORIZON_CHARS = {
    "SEALED":        "#",
    "POROUS":        "o",
    "TRANSMISSIVE":  "*",
    "OBSERVATIONAL": "+",
}


def render(layout: DiskLayout, width: int = _WIDTH, height: int = _HEIGHT) -> str:
    grid = [[" "] * width for _ in range(height)]

    def disk_to_grid(x: float, y: float) -> tuple[int, int]:
        # x,y ∈ (-1,1) → col,row
        col = int((x + 1.0) / 2.0 * (width - 1))
        row = int((1.0 - y) / 2.0 * (height - 1))
        return max(0, min(width - 1, col)), max(0, min(height - 1, row))

    # Draw unit circle outline
    for deg in range(360):
        rad = math.radians(deg)
        cx, cy = math.cos(rad) * 0.98, math.sin(rad) * 0.98
        col, row = disk_to_grid(cx, cy)
        grid[row][col] = "·"

    # Draw geodesic edges (light)
    for edge in layout.edges:
        for x, y in edge.arc_points[1:-1]:
            col, row = disk_to_grid(x, y)
            if grid[row][col] in (" ", "·"):
                grid[row][col] = "-"

    # Draw nodes
    labels: list[tuple[int, int, str]] = []
    for node in layout.nodes:
        col, row = disk_to_grid(node.x, node.y)
        char = _HORIZON_CHARS.get(node.horizon_class, _NODE_CHARS.get(node.node_type, "x"))
        grid[row][col] = char
        labels.append((col, row, node.label[:8]))

    # Build string
    lines = ["+" + "-" * width + "+"]
    for row_idx, row in enumerate(grid):
        line = "|" + "".join(row) + "|"
        lines.append(line)
    lines.append("+" + "-" * width + "+")

    # Legend
    lines.append("")
    lines.append("Nodes:")
    for node in layout.nodes:
        char = _HORIZON_CHARS.get(node.horizon_class, "x")
        lines.append(f"  {char} {node.label:20s}  ({node.x:+.3f}, {node.y:+.3f})  [{node.horizon_class}]")

    lines.append("")
    lines.append(f"System: health={layout.metadata['system_health']:.3f}  "
                 f"coherence={layout.metadata['coherence_index']:.3f}  "
                 f"mode={layout.metadata['mode']}")

    return "\n".join(lines)


if __name__ == "__main__":
    layout = build_layout()
    print(render(layout))
