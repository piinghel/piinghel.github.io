"""Render the hybrid risk article from retained aggregate comparison results."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render(rows: list[dict], output: Path, *, dark: bool, mobile: bool) -> None:
    """Show calibration spread and tails; exact portfolio metrics belong in a table."""
    colors = dict(bg="#0b1117" if dark else "#ffffff", ink="#c6cdd5" if dark else "#263747",
                  grid="#39434e" if dark else "#d9e0e7", point="#88b4de" if dark else "#356b9a")
    labels = ["Current model", "Current model, adaptive", "Hybrid", "50:50 covariance blend"]
    if mobile:
        labels = ["Current model", "Current model,\nadaptive", "Hybrid", "50:50 covariance\nblend"]
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
    with plt.rc_context({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "svg.fonttype": "none", "svg.hashsalt": "hybrid-risk"}):
        fig, ax = plt.subplots(figsize=(4.5, 3.5) if mobile else (9.75, 3.8))
        fig.patch.set_facecolor(colors["bg"])
        ax.set_facecolor(colors["bg"])
        ax.spines[:].set_visible(False)
        ax.set_ylim(3.6, -.65)
        ax.set_yticks(range(4), labels)
        ax.tick_params(length=0, colors=colors["ink"], labelsize=11 if mobile else 12, pad=6)
        ax.grid(axis="x", color=colors["grid"], lw=.55)
        ax.set_axisbelow(True)
        ax.set_xscale("log")
        ax.set_xlim(.35, 6)
        ax.set_xticks([.5, 1, 2, 4], ["0.5", "1", "2", "4"])
        ax.minorticks_off()
        ax.axvline(1, color=colors["ink"], lw=.9)
        ax.set_title("Realized / forecast volatility\nLog scale" if mobile else "Realized / forecast volatility (log scale)",
                     loc="left", fontsize=11.5 if mobile else 14, fontweight="bold",
                     color=colors["ink"], pad=14)
        stats = [row["volatility_ratio_boxplot"] for row in rows]
        for stat in stats:
            values = [stat[k] for k in ("whislo", "q1", "med", "q3", "whishi")] + stat["fliers"]
            if not all(math.isfinite(v) and .35 < v < 6 for v in values):
                raise ValueError("Boxplot observations outside displayed scale")
        ax.bxp(stats, positions=range(4), orientation="horizontal", widths=.40,
               manage_ticks=False, patch_artist=True,
               boxprops={"facecolor": colors["point"], "edgecolor": colors["point"], "alpha": .30},
               medianprops={"color": colors["ink"], "linewidth": 1.6},
               whiskerprops={"color": colors["point"]}, capprops={"color": colors["point"]},
               flierprops={"marker": ".", "markersize": 3, "markeredgecolor": colors["point"], "alpha": .55})
        fig.subplots_adjust(left=.38 if mobile else .30, right=.96, bottom=.15, top=.80)
        target = output / f"calibration{suffix}.svg"
        fig.savefig(target, metadata={"Date": None})
        target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=Path(__file__).resolve().parents[1] / "assets/hybrid-risk-model")
    parser.add_argument("--windows", type=Path, help="Refresh boxplot summaries from retained target-calibration-02/windows.parquet; no model fitting")
    args = parser.parse_args()
    metrics_path = args.assets / "metrics.json"
    metrics = json.loads(metrics_path.read_text())
    rows = metrics["rows"]
    if [r["arm"] for r in rows] != ["baseline_fixed", "baseline", "B", "C"]:
        raise ValueError("Unexpected model order")
    if args.windows:
        import polars as pl
        from matplotlib.cbook import boxplot_stats

        windows = pl.scan_parquet(args.windows).filter(pl.col("horizon") == 21)
        for row in rows:
            values = windows.filter(pl.col("arm") == row["arm"]).select("volatility_ratio").collect()["volatility_ratio"]
            if len(values) != row["n"] or not math.isclose(values.mean(), row["mean_volatility_ratio"], abs_tol=1e-12):
                raise ValueError(f"Retained calibration summary differs for {row['arm']}")
            if values.null_count() or not values.is_finite().all() or values.min() <= 0:
                raise ValueError("Expected finite positive volatility ratios")
            stats = boxplot_stats(values.to_numpy(), whis=1.5)[0]
            row["volatility_ratio_boxplot"] = {
                **{k: float(stats[k]) for k in ("q1", "med", "q3", "whislo", "whishi")},
                "fliers": sorted(stats["fliers"].tolist()),
            }
        metrics["source_hashes"]["target-calibration-02/windows.parquet"] = hashlib.sha256(args.windows.read_bytes()).hexdigest()
        metrics["conventions"]["distribution"] = "Box: quartiles; line: median; whiskers: furthest observations within 1.5 IQR of quartiles; dots: all observations beyond whiskers. Logarithmic display; summaries computed on original ratios. Overlapping windows describe dispersion, not confidence intervals."
        metrics_path.write_text(json.dumps(metrics, indent=2) + "\n")
    for dark in [False, True]:
        for mobile in [False, True]:
            render(rows, args.assets, dark=dark, mobile=mobile)


if __name__ == "__main__":
    main()
