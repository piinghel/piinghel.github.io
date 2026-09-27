"""Render the expanding walk-forward schematic; no empirical inputs required."""

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def render(*, dark: bool, mobile: bool) -> str:
    width = 358 if mobile else 702
    height = 322
    ink, muted, rule, train, predict, gap = (
        ("#e0e6ec", "#aab6c2", "#53616d", "#294c69", "#285b52", "#72522f")
        if dark else
        ("#24333f", "#52616e", "#c2ccd4", "#dbeaf5", "#d8eee6", "#f3e3cc")
    )
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             f'<g font-family="Arial, DejaVu Sans, sans-serif" fill="{ink}">']

    def text(x, y, value, size=14, anchor="start", color=None):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color or ink}">{escape(value)}</text>')

    def rect(x, y, w, h, fill):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{fill}"/>')

    def line(x1, y1, x2, y2, dashed=False):
        dash = ' stroke-dasharray="3 4"' if dashed else ""
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{rule}"{dash}/>')

    # All three rows share a schematic time axis. Each new training window
    # ends one gap before the previous prediction block's endpoint.
    start = 9 if mobile else 12
    initial, block, gap_width = (96, 70, 10) if mobile else (225, 142, 18)
    for i, (fill, label) in enumerate(((train, "Training"), (gap, "Gap"), (predict, "Prediction"))):
        x = i * (116 if mobile else 170)
        rect(x, 5, 13, 13, fill)
        text(x + 19, 17, label, 13)
    text(start, 49, "January 1995 · fixed start", 13, color=muted)
    line(start, 58, start, 288, True)
    for fold in range(3):
        y = 86 + 79 * fold
        train_width = initial + fold * block
        text(start, y - 10, f"Fit {fold + 1}", 13, color=muted)
        rect(start, y, train_width, 32, train)
        rect(start + train_width, y, gap_width, 32, gap)
        rect(start + train_width + gap_width, y, block, 32, predict)
        text(start + train_width / 2, y + 21, f"{900 + fold * 600:,} dates", 13, "middle")
        text(start + train_width + gap_width + block / 2, y + 21, "Predict", 13, "middle")
    text(start, 312, "Time →", 13, color=muted)
    parts.extend(["</g>", "</svg>"])
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    out = ROOT / "assets" / "multiple-linear-regression"
    for mobile in (False, True):
        for dark in (False, True):
            suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
            (out / f"expanding-walk-forward{suffix}.svg").write_text(render(dark=dark, mobile=mobile))
