"""Render symbolic block-matrix structure for the hybrid covariance model."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def render(output: Path, *, dark: bool, mobile: bool) -> None:
    """Show conformable factor blocks and diagonal specific risk, without sample values."""
    bg, ink = ("#0b1117", "#c6cdd5") if dark else ("#ffffff", "#263747")
    named, statistical, cross = (
        ("#34536e", "#715438", "#3d5c52") if dark
        else ("#dce9f4", "#f2e2cc", "#dceae3")
    )
    neutral = "#222f3b" if dark else "#eef1f4"
    rule = "#73818d" if dark else "#8b9ba8"
    width = 360 if mobile else 690
    with plt.rc_context({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "mathtext.fontset": "stix", "svg.fonttype": "none", "svg.hashsalt": "risk-blocks",
    }):
        fig, ax = plt.subplots(figsize=(4.5, 5.9) if mobile else (9.75, 6.4))
        fig.patch.set_facecolor(bg)
        ax.set(xlim=(0, width), ylim=(425 if mobile else 505, 0))
        ax.axis("off")
        math_size = 15 if mobile else 20
        small = 11.5 if mobile else 13

        def text(x, y, label, *, size=math_size, ha="center", weight="normal"):
            ax.text(x, y, label, color=ink, fontsize=size, ha=ha, va="center", fontweight=weight)

        def block(x, y, w, h, label, fill, *, size=math_size):
            ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=rule, linewidth=.7))
            text(x + w / 2, y + h / 2, label, size=size)

        def bracket(x, y, w, h):
            for edge, direction in [(x - 4, 1), (x + w + 4, -1)]:
                ax.plot([edge + direction * 3, edge, edge, edge + direction * 3],
                        [y - 2, y - 2, y + h + 2, y + h + 2], color=ink, lw=.8)

        # Relative block dimensions are schematic; symbols specify the actual sizes.
        n, m = (116, 72) if mobile else (150, 104)
        k = .58 * m
        centers = [50, 162, 292] if mobile else [145, 342, 557]
        text(8, 17, r"$C = L F_H L^\top$", ha="left", size=18 if mobile else 23)
        text(width - 8, 17, "Common stock covariance", ha="right", size=small)
        mid = 112 if mobile else 132
        for center, role in zip(centers, ["loadings", "covariance", "transpose"]):
            if role == "loadings":
                x, y = center - m / 2, mid - n / 2
                block(x, y, k, n, r"$B$", named)
                block(x + k, y, m - k, n, r"$P$", statistical)
                bracket(x, y, m, n)
                text(center, y - 16, r"$L$")
                text(center, mid + n / 2 + 20, r"$N \times (K+J)$", size=small)
            elif role == "covariance":
                x, y = center - m / 2, mid - m / 2
                for dx, dy, w, h, label, fill in [
                    (0, 0, k, k, r"$F_{BB}$", named),
                    (k, 0, m-k, k, r"$F_{BP}$", cross),
                    (0, k, k, m-k, r"$F_{PB}$", cross),
                    (k, k, m-k, m-k, r"$F_{PP}$", statistical),
                ]:
                    block(x+dx, y+dy, w, h, label, fill, size=13 if mobile else 18)
                bracket(x, y, m, m)
                text(center, y - 16, r"$F_H$")
                text(center, mid + n / 2 + 20, r"$(K+J)\times(K+J)$", size=small)
            else:
                x, y = center - n / 2, mid - m / 2
                block(x, y, n, k, r"$B^\top$", named)
                block(x, y+k, n, m-k, r"$P^\top$", statistical)
                bracket(x, y, n, m)
                text(center, y - 16, r"$L^\top$")
                text(center, mid + n / 2 + 20, r"$(K+J)\times N$", size=small)
        for x in ([106, 216] if mobile else [241, 440]):
            text(x, mid, r"$\times$")

        heading_y = 225 if mobile else 265
        text(8, heading_y, r"$\Sigma_H = C + D$", ha="left", size=18 if mobile else 23)
        text(width - 8, heading_y, "Total stock covariance", ha="right", size=small)
        size = 80 if mobile else 130
        centers = [52, 180, 308] if mobile else [130, 345, 560]
        top = 262 if mobile else 302
        for center, label in zip(centers, [r"$C$", r"$D$", r"$\Sigma_H$"]):
            x = center - size / 2
            if label == r"$D$":
                block(x, top, size, size, "", bg)
                ax.plot([x+5, x+size-5], [top+5, top+size-5],
                        color=rule, linewidth=5 if mobile else 8, alpha=.45)
            else:
                block(x, top, size, size, "", neutral)
            bracket(x, top, size, size)
            text(center, top - 17, label)
            text(center, top + size + 18, r"$N\times N$", size=small)
        for x, symbol in zip(([116, 244] if mobile else [237, 452]), [r"$+$", r"$=$"]):
            text(x, top + size / 2, symbol)
        text(width / 2, 407 if mobile else 479, r"$K$ named factors   ·   $J$ residual statistical factors", size=small)
        fig.subplots_adjust(left=.02, right=.98, bottom=.01, top=.99)
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
