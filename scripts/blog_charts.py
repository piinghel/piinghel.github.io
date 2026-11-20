"""Shared, allowlisted exports for static interactive research charts.

Only pass finalized aggregate returns. Raw input metadata is never serialized.
"""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path
from statistics import mean, stdev

def statistics(returns: list[float], annualization: int = 252) -> dict:
    """Geometric annual return; sample volatility; arithmetic zero-cash Sharpe."""
    if len(returns) < 2:
        raise ValueError("At least two returns are required")
    growth = peak = 1.0
    drawdown = 0.0
    for value in returns:
        if not math.isfinite(value) or value <= -1:
            raise ValueError("Returns must be finite and greater than -1")
        growth *= 1 + value
        peak = max(peak, growth)
        drawdown = min(drawdown, growth / peak - 1)
    volatility = stdev(returns) * math.sqrt(annualization)
    return dict(annual_return=growth ** (annualization / len(returns)) - 1,
                volatility=volatility,
                sharpe=mean(returns) * annualization / volatility if volatility else None,
                drawdown=drawdown)


def series(key: str, label: str, role: str, returns: list[float], **options) -> dict:
    allowed = {"dash", "visible", "contribution", "parent", "tick", "group", "category", "additive", "drawdown"}
    if options.keys() - allowed:
        raise ValueError("Unsupported series option")
    if not all(math.isfinite(x) and x > -1 for x in returns):
        raise ValueError("Missing or invalid aggregate return")
    return dict(id=key, label=label, role=role,
                values=list(returns), **options)


def write_chart(
    path: Path, dates: list[str], series_data: list[dict], charts: dict, *,
    scale: int = 10_000_000_000, annualization: int = 252,
) -> None:
    """Encode all series once using the scale declared in the output file."""
    if scale < 1 or annualization < 1:
        raise ValueError("Scale and annualization must be positive")
    if len(dates) < 2 or dates != sorted(set(dates)):
        raise ValueError("Dates must be unique and increasing")
    for value in dates:
        date.fromisoformat(value)
    if len({s["id"] for s in series_data}) != len(series_data):
        raise ValueError("Duplicate series identifier")
    if any(len(s["values"]) != len(dates) for s in series_data):
        raise ValueError("Every series must cover the complete common calendar")
    encoded = [
        {**item, "values": [round(value * scale) for value in item["values"]]}
        for item in series_data
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(version=1, scale=scale, annualization=annualization,
                                   dates=dates, series=encoded, charts=charts),
                               separators=(",", ":"), allow_nan=False) + "\n")
