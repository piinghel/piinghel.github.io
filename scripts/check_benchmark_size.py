"""Measure the ranking effect of removing or reversing the benchmark's size input.

Input: retained daily factor scores, with date, asset_id_bb_global and five
factor columns. Output: aggregate development-period ranking diagnostics.
Requires Polars; the input contains security-level data and stays local.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import polars as pl


def summarize_size_choices(source: Path) -> pl.DataFrame:
    scores = (
        pl.scan_parquet(source)
        .filter(pl.col("date").is_between(date(1998, 9, 22), date(2021, 12, 31)))
        .select(
            "date",
            "asset_id_bb_global",
            "defensive",
            "momentum",
            "short_positioning",
            "size",
            "return_consistency",
        )
        .sort("date", "asset_id_bb_global")
        .with_columns(
            pl.sum_horizontal(
                "defensive", "momentum", "short_positioning", "return_consistency"
            ).alias("other")
        )
        .with_columns(
            ((pl.col("other") + pl.col("size")) / 5).alias("original"),
            (pl.col("other") / 4).alias("no_size"),
            ((pl.col("other") + 1 - pl.col("size")) / 5).alias("reverse_size"),
        )
        .collect()
    )
    keys = ["date", "asset_id_bb_global"]
    if scores.is_empty() or scores.select(keys).n_unique() != scores.height:
        raise ValueError("Empty or duplicate stock-date observations")
    factors = [
        "defensive",
        "momentum",
        "short_positioning",
        "size",
        "return_consistency",
    ]
    if scores.select(
        pl.any_horizontal(
            pl.col(c).is_null() | ~pl.col(c).is_finite() for c in factors
        ).any()
    ).item():
        raise ValueError("All five factors must be available on the same rows")
    if scores.group_by("date").len()["len"].min() < 150:
        raise ValueError("Need at least 150 eligible stocks on every date")
    ranked = (
        scores.lazy()
        .with_columns(
            pl.col(name)
            .rank(method="ordinal", descending=True)
            .over("date")
            .alias(f"{name}_rank")
            for name in ("original", "no_size", "reverse_size")
        )
        .with_columns(pl.len().over("date").alias("count"))
    )
    selections = ranked.with_columns(
        (
            (pl.col(f"{name}_rank") <= 75)
            | (pl.col(f"{name}_rank") > pl.col("count") - 75)
        ).alias(f"{name}_selected")
        for name in ("original", "no_size", "reverse_size")
    )
    results = []
    for variant in ("no_size", "reverse_size"):
        daily = selections.group_by("date").agg(
            pl.corr("original", variant, method="spearman").alias("rank_correlation"),
            (pl.col("original_selected") & ~pl.col(f"{variant}_selected"))
            .sum()
            .alias("replaced_names"),
        )
        results.append(
            daily.select(
                pl.lit(variant).alias("variant"),
                pl.col("date").min().alias("start"),
                pl.col("date").max().alias("end"),
                pl.len().alias("dates"),
                pl.col("rank_correlation", "replaced_names").mean(),
            ).collect()
        )
    return pl.concat(results)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize_size_choices(args.scores)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.write_csv(args.output)
    print(result)


if __name__ == "__main__":
    main()
