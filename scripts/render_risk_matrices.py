"""Render the hybrid model's factor-to-stock covariance map in both themes."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


def render(output: Path, *, dark: bool, mobile: bool) -> None:
    """Use labelled symbolic blocks; colours do not encode empirical magnitudes."""
    palette = (
        dict(bg="#0c1015", ink="#e0e6ec", muted="#aab6c2", line="#758594",
             named="#294c69", residual="#72522f", cross="#285b52",
             common="#26333f", specific="#b2c5d5")
        if dark else
        dict(bg="#ffffff", ink="#24333f", muted="#52616e", line="#8798a5",
             named="#dbeaf5", residual="#f3e3cc", cross="#d8eee6",
             common="#e7edf2", specific="#66859e")
    )
    width, height = (358, 780) if mobile else (702, 324)
    with plt.rc_context({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "mathtext.fontset": "stix",
        "svg.fonttype": "none", "svg.hashsalt": "hybrid-covariance-map",
    }):
        fig = plt.figure(figsize=(width / 72, height / 72))
        fig.patch.set_facecolor(palette["bg"])
        ax = fig.add_axes((0, 0, 1, 1))
        ax.set(xlim=(0, width), ylim=(height, 0))
        ax.set_axis_off()

        def text(x, y, label, size=14, *, color=None, ha="center", weight="normal"):
            ax.text(x, y, label, fontsize=size, color=color or palette["ink"],
                    ha=ha, va="center", fontweight=weight)

        def arrow(start, end):
            ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                         mutation_scale=11, linewidth=1.2, color=palette["muted"]))

        def rectangle(x, y, w, h, fill, *, edge=False):
            ax.add_patch(Rectangle((x, y), w, h, facecolor=palette[fill],
                         edgecolor=palette["line"] if edge else "none", linewidth=.8))

        def factor_covariance(x, y, size):
            text(x + size / 2, y - 43, "Factor covariance", 15, weight="semibold")
            text(x + size / 2, y - 19, r"$F_H$", 22)
            half = size / 2
            blocks = (
                (0, 0, "named", "Named factors", r"$F_{ff}$"),
                (half, 0, "cross", "Cross-covariance", r"$F_{fg}$"),
                (0, half, "cross", "Cross-covariance", r"$F_{fg}^{\top}$"),
                (half, half, "residual", "Residual PCs", r"$F_{gg}$"),
            )
            for dx, dy, fill, label, symbol in blocks:
                rectangle(x + dx, y + dy, half, half, fill)
                text(x + dx + half / 2, y + dy + half / 2 - 15, label, 12)
                text(x + dx + half / 2, y + dy + half / 2 + 13, symbol, 25)
            ax.plot([x + half, x + half], [y, y + size], color=palette["bg"], lw=2)
            ax.plot([x, x + size], [y + half, y + half], color=palette["bg"], lw=2)
            text(x + size / 2, y + size + 19, r"$(K+J)\times(K+J)$", 13,
                 color=palette["muted"])

        def diagonal(x, y, size):
            # Identical schematic tiles mark the diagonal; they are not data.
            step = size / 6
            for i in range(6):
                rectangle(x + i * step + 1, y + i * step + 1,
                          step - 2, step - 2, "specific")

        def stock_covariance(x, y, size, *, total=False):
            text(x + size / 2, y - 43, "Total stock risk" if total else "Shared stock risk",
                 14, weight="semibold")
            text(x + size / 2, y - 19, r"$\Sigma_H$" if total else r"$C$", 23)
            rectangle(x, y, size, size, "common")
            if total:
                diagonal(x, y, size)
            text(x + size / 2, y + size + 19, r"$N\times N$", 13,
                 color=palette["muted"])

        def specific_covariance(x, y, size):
            rectangle(x, y, size, size, "bg", edge=True)
            diagonal(x, y, size)
            text(x + size / 2, y + size + 16, "Specific risk", 12,
                 color=palette["muted"])

        if mobile:
            factor_covariance(74, 60, 210)
            arrow((179, 308), (179, 340))
            text(286, 313, r"$L F_H L^\top$", 20)
            text(286, 338, r"$L=[\,B\;P\,]$", 16)
            stock_covariance(125, 392, 108)
            arrow((179, 548), (179, 580))
            text(220, 560, r"$+\,D$", 21)
            specific_covariance(254, 535, 50)
            stock_covariance(125, 632, 108, total=True)
        else:
            factor_covariance(10, 62, 224)
            arrow((248, 180), (330, 180))
            text(289, 123, "Apply exposures", 12)
            text(289, 149, r"$L F_H L^\top$", 21)
            text(289, 213, r"$L=[\,B\;P\,]$", 16)
            stock_covariance(344, 116, 128)
            arrow((483, 180), (543, 180))
            text(513, 151, r"$+\,D$", 22)
            specific_covariance(484, 220, 58)
            stock_covariance(559, 116, 128, total=True)

        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = output / f"matrix-multiplication{suffix}.svg"
        fig.savefig(path, metadata={"Date": None})
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "assets/hybrid-risk-model"
    for dark in (False, True):
        for mobile in (False, True):
            render(output, dark=dark, mobile=mobile)
