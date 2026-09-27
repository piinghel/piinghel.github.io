"""Attribution component bar charts.

Part 1, Figure 3: full-history P&L and variance share of each sector.
Part 1, Figure 4: full-history P&L and variance share of each component.
Part 2, Figure 2: component P&L over the two rebounds (the sessions after each
market low through the strategy trough).

`--outputs` reads the attribution project's daily stock and component P&L
(projects/performance_attribution/outputs/full_history) and writes the aggregates
to assets/portfolio-attribution/sectors.json, components.json and
rebound-components.json; rendering reads only those files. A variance share is
Cov(contribution, net P&L) / Var(net P&L).
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


def daily_components(outputs: Path):
    """Daily P&L per display component, with sectors combined, plus net P&L."""
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
    components = sorted(c for c in wide.columns if c not in ("date", "long_short_net"))
    net = wide["long_short_net"].to_numpy()
    if np.abs(sum(wide[c].to_numpy() for c in components) - net).max() > 1e-12:
        raise ValueError("components do not reconcile to net P&L")
    return wide, components


def pnl_and_variance_share(wide, columns) -> dict:
    """Total P&L (points) and share of net-P&L variance (%) of each daily column."""
    net = wide["long_short_net"].to_numpy()
    centered = net - net.mean()
    return {
        c: {
            "pnl_points": round(100 * float(wide[c].sum()), 4),
            "variance_share_pct": round(
                100 * float((wide[c].to_numpy() - wide[c].mean()) @ centered / (centered @ centered)), 4
            ),
        }
        for c in columns
    }


def daily_sectors(outputs: Path):
    """Daily gross stock P&L per sector (both books), plus costs and net P&L."""
    import numpy as np
    import polars as pl

    daily = pl.read_parquet(outputs / "daily.parquet").select("date", "cost_pnl", "long_short_net")
    wide = (
        pl.scan_parquet(outputs / "assets.parquet")
        .group_by("date", "sector")
        .agg(pl.col("asset_pnl").sum())
        .collect()
        .pivot(on="sector", index="date", values="asset_pnl")
        .join(daily, on="date", how="right")
        .fill_null(0)
    )
    sectors = sorted(c for c in wide.columns if c not in ("date", "cost_pnl", "long_short_net"))
    total = sum(wide[c].to_numpy() for c in [*sectors, "cost_pnl"])
    if np.abs(total - wide["long_short_net"].to_numpy()).max() > 1e-12:
        raise ValueError("sectors and costs do not reconcile to net P&L")
    return wide, sectors


def export(outputs: Path) -> None:
    import datetime as dt

    import polars as pl

    wide, sectors = daily_sectors(outputs)
    values = pnl_and_variance_share(wide, sectors)
    ranked = dict(sorted(values.items(), key=lambda item: -item[1]["pnl_points"]))
    ranked["costs"] = pnl_and_variance_share(wide, ["cost_pnl"])["cost_pnl"]
    (OUTPUT / "sectors.json").write_text(json.dumps(ranked, indent=1) + "\n")
    wide, components = daily_components(outputs)
    values = pnl_and_variance_share(wide, components)
    (OUTPUT / "components.json").write_text(json.dumps(values, indent=1) + "\n")
    # Rebounds: the sessions after each market low through the strategy trough.
    windows = json.loads((OUTPUT / "beta-history.json").read_text())["windows"]
    rebounds = {}
    for name, _, low, end in windows:
        rows = wide.filter(
            (pl.col("date") > dt.date.fromisoformat(low)) & (pl.col("date") <= dt.date.fromisoformat(end))
        )
        rebounds[name] = {c: round(100 * float(rows[c].sum()), 4) for c in components}
    (OUTPUT / "rebound-components.json").write_text(json.dumps(rebounds, indent=1) + "\n")


def render(panels: list[tuple[str, dict, str]], name: str, dark: bool, mobile: bool,
           shared_scale: bool = False, row_order: list = ROWS, wrap_labels: bool = False) -> None:
    """Draw one horizontal bar panel per (title, {key: value}, format).

    `row_order` lists (key, label) rows top to bottom; None adds a half-row gap.
    `wrap_labels` breaks long labels after their first word on phones and leaves
    more room for them on desktop.
    """
    colors = {
        "bg": "#0d1117" if dark else "#ffffff",
        "ink": "#e4e7ea" if dark else "#25313a",
        "grid": "#37414a" if dark else "#e2e6e9",
        "pos": "#6ab8aa" if dark else "#287d70",
        "neg": "#e5a081" if dark else "#b86642",
    }
    size = 10.5 if mobile else 11
    rows, y, positions = [], 0.0, []
    for row in row_order:
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
        every = [values[k] for _, values, _ in panels for k, _ in rows]
        for ax, (title, values, fmt) in zip(axes, panels, strict=True):
            data = [values[k] for k, _ in rows]
            limits = every if shared_scale else data
            ax.set_facecolor(colors["bg"])
            ax.barh(positions, data, height=0.62,
                    color=[colors["pos"] if v >= 0 else colors["neg"] for v in data])
            span = max(abs(v) for v in limits)
            for p, v in zip(positions, data, strict=True):
                ax.annotate(fmt.format(v if abs(v) >= 0.05 else 0.0).replace("-", "\u2212"), (max(v, 0), p), xytext=(4, 0), textcoords="offset points",
                            va="center", ha="left", fontsize=size - 1, color=colors["ink"])
            # Room for the value labels beside the longest bar.
            ax.set_xlim(min(min(limits), 0) - 0.05 * span, span * (1.7 if mobile else 1.35))
            ax.axvline(0, color=colors["grid"], linewidth=0.9)
            ax.set_title(title, loc="left", color=colors["ink"], fontsize=size + 0.5,
                         weight="semibold", pad=10)
            ax.spines[:].set_visible(False)
            ax.tick_params(axis="x", length=0, colors=colors["ink"], labelsize=size - 1)
            ax.tick_params(axis="y", length=0, colors=colors["ink"], labelsize=size)
            ax.xaxis.set_major_locator(plt.MaxNLocator(3))
            ax.grid(axis="x", color=colors["grid"], linewidth=0.5)
            ax.set_axisbelow(True)
        labels = [label.replace(" ", "\n", 1) if wrap_labels and mobile and len(label) > 15
                  else label for _, label in rows]
        axes[0].set_yticks(positions, labels)
        axes[0].invert_yaxis()
        left = 0.32 if mobile else (0.2 if wrap_labels else 0.17)
        fig.subplots_adjust(left=left, right=0.97, top=0.92, bottom=0.06)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = OUTPUT / f"{name}{suffix}.svg"
        fig.savefig(path, metadata={"Date": None}, facecolor=colors["bg"])
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, help="attribution full_history output folder")
    args = parser.parse_args()
    if args.outputs:
        export(args.outputs)
    sectors = json.loads((OUTPUT / "sectors.json").read_text())
    sectors.pop("costs")  # quoted in the caption; too small to draw
    by_sector = [
        ("P&L (points)", {k: v["pnl_points"] for k, v in sectors.items()}, "{:+.1f}"),
        ("Variance share (%)", {k: v["variance_share_pct"] for k, v in sectors.items()}, "{:.1f}"),
    ]
    components = json.loads((OUTPUT / "components.json").read_text())
    full_history = [
        ("P&L (points)", {k: v["pnl_points"] for k, v in components.items()}, "{:+.1f}"),
        ("Variance share (%)", {k: v["variance_share_pct"] for k, v in components.items()}, "{:.1f}"),
    ]
    rebounds = [
        (f"{episode} rebound", values, "{:+.1f}")
        for episode, values in json.loads((OUTPUT / "rebound-components.json").read_text()).items()
    ]
    for dark in (False, True):
        for mobile in (False, True):
            render(by_sector, "sector-pnl", dark, mobile, row_order=[(k, k) for k in sectors],
                   wrap_labels=True)
            render(full_history, "factor-pnl", dark, mobile)
            render(rebounds, "drawdown-factors", dark, mobile, shared_scale=True)
