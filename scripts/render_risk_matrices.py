"""Render an original, illustrative factor-covariance multiplication example."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


def render(output: Path, *, dark: bool, mobile: bool) -> None:
    """Compute every displayed product from a three-stock, two-factor toy model."""
    b = np.array([[1, 1], [1, 0], [1, -1]])
    f = np.array([[4, 1], [1, 2]])
    d = np.eye(3, dtype=int)
    bf, common = b @ f, b @ f @ b.T
    sigma = common + d
    bg, ink = ("#0b1117", "#c6cdd5") if dark else ("#ffffff", "#263747")
    blue, orange = ("#88b4de", "#e5b584") if dark else ("#356b9a", "#a35c20")
    grid = "#39434e" if dark else "#d9e0e7"
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": "risk-matrices"}):
        fig, ax = plt.subplots(figsize=(4.5, 7.1) if mobile else (9.75, 7.1))
        fig.patch.set_facecolor(bg)
        ax.set(xlim=(0, 360 if mobile else 690), ylim=(565, 0))
        ax.axis("off")
        cell = 28 if mobile else 32
        centers = [58, 176, 294] if mobile else [115, 345, 575]
        number_size = 13 if mobile else 16

        def matrix(values, center, top, label, selected):
            nr, nc = values.shape
            left = center - nc * cell / 2
            ax.text(center, top - 15, label, ha="center", color=ink,
                    fontsize=12 if mobile else 15)
            for i in range(nr):
                for j in range(nc):
                    highlighted = (i, j) in selected
                    ax.add_patch(Rectangle((left + j * cell, top + i * cell), cell, cell,
                                          facecolor=blue if highlighted else bg,
                                          alpha=.22 if highlighted else 1,
                                          edgecolor=grid, linewidth=.6))
                    ax.text(left + (j + .5) * cell, top + (i + .5) * cell,
                            str(values[i, j]).replace("-", "−"), ha="center", va="center",
                            fontsize=number_size, color=ink)
            ax.text(center, top + nr * cell + 17, f"{nr} × {nc}", ha="center",
             fontsize=11.5 if mobile else 12, color=ink)

        stages = [
            ("1. Exposures × factor covariance", b, f, bf, "B", "F", "BF", "×",
             {(0, 0), (0, 1)}, {(0, 0), (1, 0)}, {(0, 0)}, "Row × column: 1 × 4 + 1 × 1 = 5"),
            ("2. Multiply by transposed exposures", bf, b.T, common, "BF", "Bᵀ", "BFBᵀ", "×",
             {(0, 0), (0, 1)}, {(0, 1), (1, 1)}, {(0, 1)}, "Stocks 1 and 2: 5 × 1 + 3 × 0 = 5"),
            ("3. Add stock-specific variance", common, d, sigma, "BFBᵀ", "D", "Σ", "+",
             {(0, 0), (1, 1), (2, 2)}, {(0, 0), (1, 1), (2, 2)}, {(0, 0), (1, 1), (2, 2)},
             "D adds 1 to each stock’s variance."),
        ]
        for stage, (title, left, middle, right, llabel, mlabel, rlabel, op, lh, mh, rh, note) in enumerate(stages):
            top = stage * 190
            ax.text(2, top + 7, title, color=ink, fontweight="bold", fontsize=12.5 if mobile else 15)
            for values, center, label, selected in zip([left, middle, right], centers, [llabel, mlabel, rlabel], [lh, mh, rh]):
                matrix(values, center, top + 43, label, selected)
            for x, symbol in zip([(centers[0] + centers[1]) / 2, (centers[1] + centers[2]) / 2], [op, "="]):
                ax.text(x, top + 43 + cell, symbol, color=ink, ha="center", va="center", fontsize=18)
            ax.text(2, top + 177, note, color=orange, fontsize=12.5 if mobile else 13)
        fig.subplots_adjust(left=.025, right=.975, bottom=.01, top=.98)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = output / f"matrix-multiplication{suffix}.svg"
        fig.savefig(path, metadata={"Date": None})
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "assets/hybrid-risk-model"
    for dark in [False, True]:
        for mobile in [False, True]:
            render(output, dark=dark, mobile=mobile)
