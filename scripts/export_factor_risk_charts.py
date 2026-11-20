"""Render aggregate portfolio returns and residual diagnostics for the factor-risk article."""

import argparse
from datetime import date, timedelta
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


def render_performance(returns, portfolios, destination, *, colors, grid, mobile):
    dates = returns["date"].to_list()
    dates = [dates[0] - timedelta(days=1), *dates]
    fig, (growth, drawdown) = plt.subplots(
        2, 1, figsize=(4.5 if mobile else 8.4, 4.7),
        layout="constrained", sharex=True,
    )
    for (key, label, _, _, _), color, dash in zip(
        portfolios[:3], colors, ("-", "--", "-."), strict=True,
    ):
        wealth = np.r_[1, np.cumprod(1 + returns[key].to_numpy())]
        growth.plot(dates, wealth, color=color, ls=dash, lw=1.15)
        if mobile and key == "factor":
            label = "Sector and\nstyle factors"
        growth.annotate(
            label, (dates[-1], wealth[-1]), xytext=(5, 0), textcoords="offset points",
            ha="left", va="center", annotation_clip=False,
            color=color, fontsize=9 if mobile else 10,
        )
        drawdown.plot(
            dates, wealth / np.maximum.accumulate(wealth) - 1,
            color=color, ls=dash, lw=0.8, alpha=0.85,
        )
    for axis in (growth, drawdown):
        axis.spines[:].set_visible(False)
        axis.tick_params(which="both", length=0, pad=4)
        axis.grid(axis="y", color=grid, linewidth=0.6)
        axis.set_axisbelow(True)

    growth.set_yscale("log")
    growth.set_yticks([1, 2, 4, 8, 16], labels=["1", "2", "4", "8", "16"])
    growth.set_title("Growth of $1 after fees", loc="left")
    growth.set_xlim(dates[0], dates[-1])
    drawdown.set_title("Drawdown from the previous peak", loc="left")
    drawdown.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    drawdown.xaxis.set_major_locator(mdates.YearLocator(10 if mobile else 5))
    drawdown.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.savefig(destination, transparent=True, metadata={"Date": None})
    destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines()) + "\n")
    plt.close(fig)


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
        render_performance(
            returns, portfolios, output / ("performance" + suffix),
            colors=colors, grid=grid, mobile=mobile,
        )
        fig, (upper, lower) = plt.subplots(2, 1, figsize=(4.5 if mobile else 8.4, 4.7),
                                            layout="constrained", sharex=True)
        for axis in [upper, lower]:
            axis.spines[:].set_visible(False)
            axis.tick_params(length=0, pad=4)
            axis.grid(axis="y", color=grid, linewidth=0.6)
            axis.set_axisbelow(True)
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
        destination = output / ("residuals" + suffix)
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


def export_realized_risk(daily, portfolios, output, sessions, annualization, risk_budget):
    """Report each schedule's trailing net volatility, then average on common month ends."""
    names = [model[0] for model in portfolios]
    keys = ["arm", "schedule"]
    data = (
        pl.scan_parquet(daily).filter(pl.col("arm").is_in(names))
        .select("date", *keys, "long_short_net")
        .with_columns((pl.col("long_short_net").rolling_std(sessions, ddof=1)
                       .over(keys, order_by="date") * np.sqrt(annualization) * 100).alias("risk"))
        .drop_nulls("risk")
        .group_by("date", "arm").agg(pl.mean("risk"), pl.col("schedule").n_unique().alias("offsets"))
        .sort("date").collect()
    )
    if data["offsets"].min() != 3 or data["offsets"].max() != 3:
        raise ValueError("A forecast comparison needs three offset returns per stock model and date")
    monthly = (data.pivot(on="arm", index="date", values="risk").sort("date")
               .group_by(pl.col("date").dt.strftime("%Y-%m").alias("month"), maintain_order=True)
               .last())
    if any(monthly.select(names).null_count().row(0)):
        raise ValueError("Monthly risk comparisons must use identical endpoints")
    dates = monthly["date"].to_list()
    lines = [series(key, label, role, monthly[key].to_list(), dash=dash, visible=visible)
             for key, label, role, dash, visible in portfolios]
    lines.append(series("budget", "Optimizer budget", "comparison", [100*risk_budget]*len(dates), dash="dot", visible=True))
    slug = "realized-risk"
    write_chart(output / (slug + ".json"), [date.isoformat() for date in dates], lines,
                {slug: dict(kind="values", series=[line["id"] for line in lines],
                            unit=f"Trailing {sessions}-session net volatility (%)")})
    for mobile in (False, True):
        for dark in (False, True):
            ink, blue, violet, grid = (("#d3dbe4", "#68a9ed", "#b89be9", "#39434e") if dark
                                       else ("#283542", "#2165a6", "#7950a2", "#d8dee4"))
            style = {"font.size":9 if mobile else 10, "svg.fonttype":"none", "svg.hashsalt":slug,
                     "text.color":ink, "xtick.color":ink, "ytick.color":ink, "axes.titlecolor":ink}
            with plt.rc_context(style):
                fig, ax = plt.subplots(figsize=(4.5 if mobile else 8.4, 3.8), layout="constrained")
                for (key, label, _, _, _), color, dash in zip(
                    portfolios[:3], (ink, blue, violet), ("-", "--", "-."), strict=True
                ):
                    ax.plot(dates, monthly[key].to_numpy(), lw=1.2, color=color, ls=dash, label=label)
                ax.axhline(risk_budget*100, ls=":", color=ink, lw=1, label="Optimizer budget")
                ax.set_title(f"Trailing {sessions}-session net volatility", loc="left")
                ax.set_ylim(bottom=0)
                ax.set_xlim(dates[0], dates[-1])
                ax.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
                ax.xaxis.set_major_locator(mdates.YearLocator(6 if mobile else 5))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
                ax.tick_params(length=0)
                ax.spines[:].set_visible(False)
                ax.grid(axis="y", color=grid, lw=.6)
                ax.set_axisbelow(True)
                fig.legend(*ax.get_legend_handles_labels(), loc="outside lower center", ncol=2,
                           frameon=False, fontsize=8 if mobile else 9, labelcolor=ink)
                suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
                dest = output / f"{slug}{suffix}.svg"
                fig.savefig(dest, transparent=True, metadata={"Date":None})
                dest.write_text("\n".join(row.rstrip() for row in dest.read_text().splitlines()) + "\n")
                plt.close(fig)


def market_exposure(daily: Path, portfolios: tuple, *, window: int, start: date) -> pl.DataFrame:
    """Measure market exposure on each filled schedule before averaging."""
    arms = [f"calibrated_{key}" for key, *_ in portfolios]
    groups = ["arm", "schedule"]
    returns, market = pl.col("long_short_net"), pl.col("benchmark")
    monthly = (
        pl.scan_parquet(daily)
        .filter(pl.col("arm").is_in(arms))
        .select("date", *groups, returns, market)
        .sort(*groups, "date")
        .with_columns(
            (pl.rolling_cov(returns, market, window_size=window) / market.rolling_var(window))
            .over(groups).alias("beta"),
            pl.rolling_corr(returns, market, window_size=window).over(groups).alias("correlation"),
        )
        .filter(pl.col("date") >= start)
        .drop_nulls(["beta", "correlation"])
        .group_by("arm", "date")
        .agg(pl.mean("beta", "correlation"), pl.col("schedule").n_unique().alias("schedules"))
        .sort("date")
        .group_by("arm", pl.col("date").dt.truncate("1mo").alias("month"))
        .last()
        .sort("date")
        .collect()
    )
    if monthly.is_empty() or not (monthly["schedules"] == 3).all():
        raise ValueError("Expected three schedule estimates at each market-exposure endpoint")
    return monthly


def render_market_exposure(monthly, portfolios, output, *, dark, mobile, window):
    ink, blue, violet, grid = (
        ("#d3dbe4", "#68a9ed", "#b89be9", "#39434e") if dark
        else ("#283542", "#2165a6", "#7950a2", "#d8dee4")
    )
    style = {
        "font.size": 9 if mobile else 10, "svg.fonttype": "none",
        "svg.hashsalt": "factor-risk-market-exposure", "text.color": ink,
        "axes.titlecolor": ink, "xtick.color": ink, "ytick.color": ink,
    }
    with plt.rc_context(style):
        fig, (beta, correlation) = plt.subplots(
            2, 1, figsize=(4.5 if mobile else 8.4, 4.7), layout="constrained", sharex=True,
        )
        dates = monthly["date"].unique().sort()
        for (key, label, *_), color, dash in zip(
            portfolios, (ink, blue, violet), ("-", "--", "-."), strict=True,
        ):
            book = monthly.filter(pl.col("arm") == f"calibrated_{key}")
            if not book["date"].equals(dates):
                raise ValueError(f"Market-exposure dates differ for {key}")
            beta.plot(dates, book["beta"], color=color, ls=dash, lw=1.3)
            correlation.plot(dates, book["correlation"], color=color, ls=dash, lw=1.3)
            if mobile and key == "factor":
                label = "Sector and\nstyle factors"
            beta.annotate(
                label, (dates[-1], book["beta"][-1]), xytext=(5, 0),
                textcoords="offset points", ha="left", va="center",
                annotation_clip=False, color=color, fontsize=9 if mobile else 10,
            )
        beta.set_title(f"{window}-session market beta", loc="left")
        correlation.set_title(f"{window}-session correlation with the market", loc="left")
        for axis in (beta, correlation):
            axis.axhline(0, lw=0.9, color=grid)
            axis.grid(axis="y", color=grid, linewidth=0.55, alpha=0.65)
            axis.set_axisbelow(True)
            axis.spines[:].set_visible(False)
            axis.tick_params(length=0, pad=4)
        correlation.set_xlim(dates[0], dates[-1])
        correlation.xaxis.set_major_locator(mdates.YearLocator())
        correlation.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = output / f"market-exposure{suffix}.svg"
        fig.savefig(path, transparent=True, metadata={"Date": None})
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)


def render_funding(data, output, dark, mobile):
    ink, blue, violet, grid = (
        ("#d3dbe4", "#74b7f4", "#c6afea", "#39434e") if dark
        else ("#283542", "#2165a6", "#7950a2", "#d8dee4")
    )
    components = ("mean_funding", "funding_timing", "composition")
    labels = ("Average amount short", "Timing of short exposure", "Choice and size of shorts")
    style = {"font.size": 9 if mobile else 10, "text.color": ink, "xtick.color": ink,
             "ytick.color": ink, "axes.labelcolor": ink, "svg.fonttype": "none",
             "svg.hashsalt": "factor-risk-funding"}
    with plt.rc_context(style):
        fig, ax = plt.subplots(figsize=(4.6 if mobile else 7.6, 3.5), layout="constrained")
        ax.axvline(0, color=ink, linewidth=.9, linestyle=":")
        for period, label, color, marker, offset in (
            ("development", "1999–2021", violet, "s", .13),
            ("later", "2022–May 2026", blue, "o", -.13),
        ):
            series = data.filter(pl.col("reference") == "calibrated_shrinkage",
                                 pl.col("leg") == "short", pl.col("period") == period)
            for i, component in enumerate(components):
                point, low, high = series.filter(pl.col("component") == component).select(
                    "annual_pp", "low95", "high95").row(0)
                y = len(components) - i + offset
                ax.plot([low, high], [y, y], color=color, linewidth=1.5)
                ax.plot(point, y, marker=marker, color=color, markersize=6,
                        label=label if i == 0 else None)
        ax.set_yticks([3, 2, 1], labels=labels)
        ax.set(ylim=(.5, 3.55), xlabel="Difference in annual return (percentage points)")
        ax.xaxis.grid(True, color=grid, linewidth=.55)
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", length=0, pad=5)
        ax.spines[:].set_visible(False)
        ax.legend(ncols=2, frameon=False, loc="lower center", bbox_to_anchor=(.5, 1.0),
                  fontsize=8 if mobile else 10, columnspacing=1.2, labelcolor=ink)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        destination = output / f"short-funding{suffix}.svg"
        fig.savefig(destination, transparent=True, metadata={"Date": None})
        plt.close(fig)
        destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines()) + "\n")


def render_fixed_book(data, output, *, dark, mobile):
    ink, before_color, after_color, grid = (
        ("#d3dbe4", "#c0a1e6", "#78b6fb", "#3d4956") if dark
        else ("#283542", "#79548c", "#2165a6", "#d7dde2")
    )
    style = {"font.size": 10, "svg.fonttype": "none", "svg.hashsalt": "ridge-fixed-book",
             "text.color": ink, "axes.titlecolor": ink, "axes.labelcolor": ink,
             "xtick.color": ink, "ytick.color": ink}
    holdings = data.filter(pl.col("book") == "shrinkage")
    periods = (("development", "2000–2021"), ("later", "2022–May 2026"))
    with plt.rc_context(style):
        fig, axes = plt.subplots(2, 1, figsize=(4.7 if mobile else 7.5, 4.5), layout="constrained", sharex=True)
        bounds = holdings.select("raw", "calibrated", "realized_variance").to_numpy() * 100
        lo, hi = np.floor(bounds.min()), np.ceil(bounds.max())
        for ax, (period, heading) in zip(axes, periods, strict=True):
            rows = holdings.filter(pl.col("period") == period)
            if len(rows) != 2 or rows["realized_variance"].n_unique() != 1:
                raise ValueError("Fixed-book methods must share exactly one realized outcome")
            observed = 100 * rows["realized_variance"][0]
            ax.axvline(observed, color=ink, linestyle="--", linewidth=1)
            ax.set_title(f"{heading}  ·  realized {observed:.2f}%", loc="left", fontsize=11)
            for y, (arm, label) in enumerate((("factor_target", "Factor target"), ("shrinkage", "Stock shrinkage"))):
                row = rows.filter(pl.col("model") == arm)
                if len(row) != 1:
                    raise ValueError("Missing covariance estimate in fixed-book comparison")
                raw, corrected = 100 * row.select("raw", "calibrated").to_numpy()[0]
                ax.plot([raw, corrected], [y, y], color=grid, linewidth=2, zorder=1)
                ax.scatter(raw, y, marker="o", facecolor="none", edgecolor=before_color, linewidth=1.6,
                           s=42, label="Original forecast" if y == 0 else None, zorder=2)
                ax.scatter(corrected, y, marker="D", color=after_color, s=27,
                           label="After calibration" if y == 0 else None, zorder=3)
            ax.set(yticks=(0, 1), yticklabels=("Factor target", "Stock shrinkage"), ylim=(-.38, 1.4),
                   xlim=(lo - .15, hi + .15), xticks=np.arange(lo, hi + 1))
            ax.xaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
            ax.tick_params(length=0, pad=5, labelbottom=True)
            ax.grid(axis="x", lw=.5, color=grid)
            ax.spines[:].set_visible(False)
        axes[-1].set_xlabel("Annualized gross volatility")
        fig.legend(*axes[0].get_legend_handles_labels(), loc="outside upper center",
                   frameon=False, ncol=2, handlelength=.9)
        suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
        path = output / f"fixed-book{suffix}.svg"
        fig.savefig(path, transparent=True, metadata={"Date": None})
        plt.close(fig)
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ["daily", "pair-history", "clusters", "hedge-intervals", "funding-attribution", "fixed-book-forecasts", "output"]:
        parser.add_argument("--" + arg, type=Path, required=True)
    parser.add_argument("--calibrated-daily", type=Path, help="Daily calibrated accounts for the market-exposure figure")
    args = parser.parse_args()
    portfolios = (("shrinkage", "Stock shrinkage", "strategy", "solid", True),
                  ("factor_target", "Factor target", "long", "dash", True),
                  ("factor", "Sector and style factors", "hedged", "dashdot", True),
                  ("volatility", "Volatility scaling", "short", "dot", False))
    returns = portfolio_paths(args.daily, portfolios)
    export_interactive(returns, portfolios, args.output)
    export_realized_risk(args.daily, portfolios, args.output, 252, 252, .07)
    funding = pl.read_csv(args.funding_attribution)
    calibration = pl.read_csv(args.fixed_book_forecasts)
    pairs = pl.read_csv(args.pair_history, try_parse_dates=True).sort("decision")
    clusters = pl.read_csv(args.clusters, try_parse_dates=True).sort("last_forward")
    paired = pl.read_csv(args.hedge_intervals).filter(pl.col("mandate") == "long/short",
                                                    pl.col("weights") == "all names", pl.col("block_weeks") == 13)
    exposure_window = 63
    exposure = None
    if args.calibrated_daily:
        exposure = market_exposure(args.calibrated_daily, portfolios[:3], window=exposure_window, start=date(2022, 1, 1))
    for mobile in [False, True]:
        for dark in [False, True]:
            render_figures(returns, portfolios, pairs, clusters, args.output, dark, mobile)
            render_hedges(paired, args.output, dark, mobile)
            render_funding(funding, args.output, dark, mobile)
            render_fixed_book(calibration, args.output, dark=dark, mobile=mobile)
            if exposure is not None:
                render_market_exposure(
                    exposure, portfolios[:3], args.output, dark=dark, mobile=mobile, window=exposure_window,
                )


if __name__ == "__main__":
    main()
