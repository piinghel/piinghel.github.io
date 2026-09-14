"""Render schematic training-design diagrams; no empirical inputs required."""

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def render(kind: str, *, dark: bool, mobile: bool) -> str:
    width = 358 if mobile else 702
    height = 302 if kind == "date-sampling" else 350
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

    if kind == "date-sampling":
        text(0, 20, "Within one training window", 15)
        text(0, 43, "Each date contributes its full stock cross-section", 13, color=muted)
        start, step = (97, 27) if mobile else (160, 58)
        for model in range(3):
            y = 86 + 59 * model
            text(0, y + 5, f"Model {model + 1}")
            line(start, y, start + 8 * step, y)
            for day in range(9):
                x = start + day * step
                selected = day % 3 == model
                parts.append(f'<circle cx="{x}" cy="{y}" r="{13 if selected else 2}" fill="{train if selected else rule}"/>')
                if selected:
                    text(x, y + 5, str(day + 1), 14, "middle")
            text(start + 8 * step + 28, y + 5, "…", 14, "middle")
        text(width / 2, 254, "Fit each model on its assigned dates", 14, "middle")
        text(width / 2, 279, "↓  Average their prediction scores", 14, "middle")
    else:
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
        text(start, 308, "Training grows; earlier history stays", 14)
        text(start, 334, "Time →", 13, color=muted)
    parts.extend(["</g>", "</svg>"])
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    out = ROOT / "assets" / "multiple-linear-regression"
    for kind in ("date-sampling", "expanding-walk-forward"):
        for mobile in (False, True):
            for dark in (False, True):
                suffix = ("_mobile" if mobile else "") + ("_dark" if dark else "")
                (out / f"{kind}{suffix}.svg").write_text(render(kind, dark=dark, mobile=mobile))
