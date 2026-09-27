"""Part 1, Figure 4: full-history P&L and variance share of each attribution component.

`--outputs` reads the attribution project's daily component P&L
(projects/performance_attribution/outputs/full_history) and writes the aggregate
values to assets/portfolio-attribution/components.json; rendering reads only that
file. A component's variance share is Cov(component, net P&L) / Var(net P&L).
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT = Path(__file__).resolve().parents[1] / "assets/portfolio-attribution"
# Display order, grouped: market, styles, sectors, stock-specific, costs.
ROWS = [
    ("market", "Common return"),
    None,
    ("size", "Size"),
    ("beta", "Beta"),
    ("momentum", "Momentum"),
    ("volatility", "Volatility"),
    ("reversal", "Reversal"),
    None,
    ("sector", "Sector effects"),
    None,
    ("idio_pnl", "Residual"),
    ("unmodeled_pnl", "Uncovered holdings"),
    None,
    ("costs", "Trading costs"),
]


def export(outputs: Path) -> None:
    import numpy as np
    import polars as pl

    daily = pl.read_parquet(outputs / "factors/daily.parquet")
    group = (
        pl.when(pl.col("factor").str.starts_with("sector:"))
        .then(pl.lit("sector"))
        .otherwise(pl.col("factor"))
    )
    wide = (
        daily.with_columns(group.alias("component"))
        .group_by("date", "component")
        .agg(pl.col("pnl").sum())
        .pivot(on="component", index="date", values="pnl")
        .fill_null(0)
        .join(pl.read_parquet(outputs / "daily.parquet").select("date", "long_short_net"), on="date")
    )
    net = wide["long_short_net"].to_numpy()
    components = [c for c in wide.columns if c not in ("date", "long_short_net")]
    if np.abs(sum(wide[c].to_numpy() for c in components) - net).max() > 1e-12:
        raise ValueError("components do not reconcile to net P&L")
    centered = net - net.mean()
    values = {
        c: {
            "pnl_points": round(100 * float(wide[c].sum()), 4),
            "variance_share_pct": round(
                100 * float((wide[c].to_numpy() - wide[c].mean()) @ centered / (centered @ centered)), 4
            ),
        }
        for c in components
    }
    (OUTPUT / "components.json").write_text(json.dumps(values, indent=1) + "\n")


def render(values: dict, dark: bool, mobile: bool) -> None:
    colors = {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4e7ea" if dark else "#25313a",
        "grid": "#37414a" if dark else "#e2e6e9",
        "pos": "#6ab8aa" if dark else "#287d70",
        "neg": "#e5a081" if dark else "#b86642",
    }
    size = 10.5 if mobile else 11
    rows, y, positions = [], 0.0, []
    for row in ROWS:
        if row is None:
            y += 0.5
            continue
        rows.append(row)
        positions.append(y)
        y += 1
    with plt.rc_context(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "svg.fonttype": "none",
            "svg.hashsalt": "attribution-components",
        }
    ):
        fig, axes = plt.subplots(
            1, 2, figsize=(5, 6.4) if mobile else (9, 5.6), sharey=True,
            gridspec_kw={"wspace": 0.55 if mobile else 0.45},
        )
        fig.set_facecolor(colors["bg"])
        for ax, key, title, fmt in (
            (axes[0], "pnl_points", "P&L (points)", "{:+.1f}"),
            (axes[1], "variance_share_pct", "Variance share (%)", "{:.1f}"),
        ):
            data = [values[k][key] for k, _ in rows]
            ax.set_facecolor(colors["bg"])
            ax.barh(positions, data, height=0.62,
                    color=[colors["pos"] if v >= 0 else colors["neg"] for v in data])
            span = max(abs(v) for v in data)
            for p, v in zip(positions, data, strict=True):
                ax.annotate(fmt.format(v if abs(v) >= 0.05 else 0.0), (max(v, 0), p), xytext=(4, 0), textcoords="offset points",
                            va="center", ha="left", fontsize=size - 1, color=colors["ink"])
            ax.set_xlim(min(min(data), 0) - 0.05 * span, span * 1.35)
            ax.axvline(0, color=colors["grid"], linewidth=0.9)
            ax.set_title(title, loc="left", color=colors["ink"], fontsize=size + 0.5,
                         weight="semibold", pad=10)
            ax.spines[:].set_visible(False)
            ax.tick_params(axis="x", length=0, colors=colors["ink"], labelsize=size - 1)
            ax.tick_params(axis="y", length=0, colors=colors["ink"], labelsize=size)
            ax.xaxis.set_major_locator(plt.MaxNLocator(3))
            ax.grid(axis="x", color=colors["grid"], linewidth=0.5)
            ax.set_axisbelow(True)
        axes[0].set_yticks(positions, [label for _, label in rows])
        axes[0].invert_yaxis()
        fig.subplots_adjust(left=0.32 if mobile else 0.17, right=0.97, top=0.92, bottom=0.06)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = OUTPUT / f"factor-pnl{suffix}.svg"
        fig.savefig(path, metadata={"Date": None}, facecolor=colors["bg"])
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, help="attribution full_history output folder")
    args = parser.parse_args()
    if args.outputs:
        export(args.outputs)
    components = json.loads((OUTPUT / "components.json").read_text())
    for dark in (False, True):
        for mobile in (False, True):
            render(components, dark, mobile)
