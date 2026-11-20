"""Render aggregate portfolio returns and residual diagnostics for the factor-risk article."""

import argparse
from datetime import timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.ticker import FuncFormatter, PercentFormatter

from blog_charts import series, write_chart


def portfolio_paths(daily: Path, portfolios: tuple) -> pl.DataFrame:
    names = [row[0] for row in portfolios]
    data = pl.read_parquet(daily, columns=["date", "arm", "schedule", "long_short_net"])
    rows = data.filter(pl.col("arm").is_in(names)).group_by("date", "arm").agg(
        pl.mean("long_short_net"), pl.len().alias("rows"), pl.col("schedule").n_unique().alias("offsets")
    )
    if rows.filter((pl.col("rows") != 3) | (pl.col("offsets") != 3)).height:
        raise ValueError("Expected one daily return from each of three schedules")
    return rows.pivot(on="arm", index="date", values="long_short_net").sort("date")


def export_interactive(returns, portfolios, output):
    dates = returns["date"].to_list()
    origin = dates[0] - timedelta(days=1)
    lines = [
        series(key, label, role, [0.0, *returns[key]], dash=dash, visible=visible)
        for key, label, role, dash, visible in portfolios
    ]
    chart = dict(kind="performance", series=[line["id"] for line in lines], log=True, drawdown=True,
                 episodes=[["Development", origin.isoformat(), "2021-12-31"],
                           ["Later period", "2021-12-31", dates[-1].isoformat()]],
                 note="Compounded mean daily net return of the three schedules. Table entries average each schedule’s own statistic.")
    write_chart(output / "performance.json", [origin.isoformat(), *[d.isoformat() for d in dates]],
                lines, {"performance": chart})


def render_figures(returns, portfolios, pairs, clusters, output, dark, mobile):
    ink, blue, violet, grid = (
        ("#d3dbe4", "#68a9ed", "#b89be9", "#39434e") if dark
        else ("#283542", "#2165a6", "#7950a2", "#d8dee4")
    )
    colors = [ink, blue, violet]
    suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "") + ".svg"
    style = {"font.size": 9 if mobile else 10, "text.color": ink, "xtick.color": ink,
             "ytick.color": ink, "axes.labelcolor": ink, "axes.titlecolor": ink,
             "svg.fonttype": "none", "svg.hashsalt": "factor-risk-sizing"}
    with plt.rc_context(style):
        for slug in ["performance", "residuals"]:
            fig, (upper, lower) = plt.subplots(2, 1, figsize=(4.5 if mobile else 8.4, 4.7),
                                                layout="constrained", sharex=True)
            for axis in [upper, lower]:
                axis.spines[:].set_visible(False)
                axis.tick_params(length=0, pad=4)
                axis.grid(axis="y", color=grid, linewidth=0.6)
                axis.set_axisbelow(True)
            if slug == "performance":
                dates = returns["date"].to_list()
                dates = [dates[0] - timedelta(days=1), *dates]
                for (key, label, _, _, _), color, dash in zip(portfolios[:3], colors, ["-", "--", "-."], strict=True):
                    wealth = np.r_[1, np.cumprod(1 + returns[key].to_numpy())]
                    upper.plot(dates, wealth, color=color, ls=dash, lw=1.15, label=label)
                    lower.plot(dates, wealth / np.maximum.accumulate(wealth) - 1, color=color, ls=dash, lw=0.95)
                upper.set_yscale("log")
                upper.set_yticks([1, 2, 4, 8, 16], labels=["1", "2", "4", "8", "16"])
                upper.set_title("Growth of $1 after costs", loc="left")
                lower.set_title("Loss from the previous peak", loc="left")
                upper.legend(loc="upper left", frameon=False, fontsize=8, labelcolor=ink)
                lower.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
            else:
                upper.plot(pairs["decision"], pairs["raw_pair_correlation"], color=blue, lw=1)
                upper.plot(pairs["decision"], pairs["residual_pair_correlation"], color=violet, lw=1.5, ls="--")
                for col, label, color in [("raw_pair_correlation", "Stocks", blue),
                                          ("residual_pair_correlation", "Residuals", violet)]:
                    upper.annotate(label, (pairs["decision"][-1], pairs[col][-1]), xytext=(4, 0),
                                   textcoords="offset points", color=color, va="center", fontsize=9)
                upper.margins(x=0)
                upper.set_title("Average one-year pairwise correlation", loc="left")
                upper.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
                lower.scatter(clusters["last_forward"], 100 * clusters["forward_contrast"], color=blue, s=19)
                lower.scatter(clusters["last_forward"], 100 * clusters["within_sector_upper95"],
                              color=ink, s=18, marker="_")
                lower.axhline(0, color=grid, linewidth=0.7)
                lower.set_title("Within-group minus outside, next year", loc="left")
                lower.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: f"{value:g} pp"))
                # Leave space inside the exported figure for the two direct labels.
                upper.set_xlim(pairs["decision"][0], pairs["decision"][-1] + timedelta(days=6*365 if mobile else 3*365))
            lower.xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 5))
            lower.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
            destination = output / (slug + suffix)
            fig.savefig(destination, transparent=True, metadata={"Date": None})
            destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines()) + "\n")
            plt.close(fig)


def render_hedges(paired, output, dark, mobile):
    ink, blue, violet, grid = (("#d3dbe4", "#68a9ed", "#b89be9", "#39434e") if dark
                              else ("#283542", "#2165a6", "#7950a2", "#d8dee4"))
    labels = [("factor", "Original factors", violet, "s"), ("residual_lw", "Shrunk residuals", blue, "o"),
              ("factor_target", "Factor target", ink, "D")]
    style = {"font.size": 10 if mobile else 11, "svg.fonttype": "none", "svg.hashsalt": "factor-risk-hedges",
             "text.color": ink, "axes.labelcolor": ink, "axes.titlecolor": ink, "xtick.color": ink, "ytick.color": ink}
    with plt.rc_context(style):
        fig, axes = plt.subplots(2, 1, figsize=(4.5 if mobile else 8.4, 6.0), layout="constrained", sharex=True)
        for ax, (period, heading) in zip(axes, [("development","1999–2021"), ("later","2022–May 2026")], strict=True):
            ax.set_title(heading, loc="left")
            ax.axvline(0, color=ink, lw=.8, ls=":")
            for shift, (model, label, color, marker) in zip([.23, 0, -.23], labels, strict=True):
                rows = paired.filter(pl.col("model") == model, pl.col("period") == period).sort("size")
                if rows["size"].to_list() != [75, 100, 150]:
                    raise ValueError("Missing portfolio size in hedge figure")
                y = np.array([2, 1, 0]) + shift
                ax.hlines(y, rows["joint_low95"], rows["joint_high95"], color=color, lw=1.2)
                ax.scatter(rows["difference"], y, label=label, color=color, marker=marker, s=23, zorder=3)
            ax.set_yticks([2,1,0], labels=["75 stocks","100 stocks","150 stocks"])
            ax.set_ylim(-.5, 2.5)
            ax.tick_params(length=0)
            ax.grid(axis="x", color=grid, lw=.6)
            ax.set_axisbelow(True)
            ax.spines[:].set_visible(False)
        fig.legend(*axes[0].get_legend_handles_labels(), loc="outside upper center",
                   ncol=3, labelcolor=ink, fontsize=8 if mobile else 10, frameon=False,
                   handletextpad=.25, columnspacing=.8)
        axes[-1].set_xlabel("Volatility minus stock shrinkage (percentage points)")
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        destination = output / f"hedges{suffix}.svg"
        fig.savefig(destination, transparent=True, metadata={"Date":None})
        destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines()) + "\n")
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ["daily", "pair-history", "clusters", "hedge-intervals", "output"]:
        parser.add_argument("--" + arg, type=Path, required=True)
    args = parser.parse_args()
    portfolios = (("shrinkage", "Stock shrinkage", "strategy", "solid", True),
                  ("factor_target", "Factor target", "long", "dash", True),
                  ("factor", "Sector and style factors", "hedged", "dashdot", True),
                  ("volatility", "Volatility scaling", "short", "dot", False))
    returns = portfolio_paths(args.daily, portfolios)
    export_interactive(returns, portfolios, args.output)
    pairs = pl.read_csv(args.pair_history, try_parse_dates=True).sort("decision")
    clusters = pl.read_csv(args.clusters, try_parse_dates=True).sort("last_forward")
    paired = pl.read_csv(args.hedge_intervals).filter(pl.col("mandate") == "long/short",
                                                    pl.col("weights") == "all names", pl.col("block_weeks") == 13)
    for mobile in [False, True]:
        for dark in [False, True]:
            render_figures(returns, portfolios, pairs, clusters, args.output, dark, mobile)
            render_hedges(paired, args.output, dark, mobile)


if __name__ == "__main__":
    main()
