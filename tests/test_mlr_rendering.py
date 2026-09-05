"""Small synthetic evidence protects the Ridge display contract, not its findings."""

import copy
import csv
import gzip
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from mlr_figures.diagnostics import plot_selected_coefficients
from mlr_figures.performance import plot_performance
from mlr_figures.support import (
    FigureStyle,
    dark_figure_style,
    default_figure_spec,
    load_performance,
    load_selected_coefficients,
)
from render_multiple_linear_regression_figures import render_figures

COEFFICIENT_FILE = "multiple_linear_selected_coefficient_heatmap_source_c0p01.csv.gz"
PERFORMANCE_FILE = "multiple_linear_selected_return_drawdown_figure_source.csv.gz"


def coefficient_rows():
    features = list(default_figure_spec(FigureStyle()).feature_labels)[:9] + [
        "X_feature_price_ret252_shift0"
    ]
    return [
        {
            "feature": feature,
            "fold_id": str(fold),
            "test_date": f"{2010 + fold}-01-01",
            "coefficient": str((-1) ** rank * (13 - fold) / (100 * rank)),
            "heatmap_rank": str(rank),
            "c": "0.01",
            "selected": "true",
        }
        for rank, feature in enumerate(features, start=1)
        for fold in range(1, 13)
    ]


def write_csv(path, rows):
    with gzip.open(path, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_evidence(root):
    write_csv(root / COEFFICIENT_FILE, coefficient_rows())
    rows = []
    for model in default_figure_spec(FigureStyle()).model_order:
        # A first-day loss, recovery and later loss catch initial-peak mistakes.
        for day, growth, drawdown in (
            ("1998-09-22", 0.9, -10.0),
            ("2010-01-04", 1.2, 0.0),
            ("2022-01-03", 1.1, -100 / 12),
            ("2026-05-27", 1.5, 0.0),
        ):
            rows.append(
                {
                    "model": model,
                    "date": day,
                    "cumulative_net_return_pct": (growth - 1) * 100,
                    "drawdown_pct": drawdown,
                }
            )
    write_csv(root / PERFORMANCE_FILE, rows)


class RidgeRenderingTests(unittest.TestCase):
    def test_refit_dates_and_feature_ranks_are_unambiguous(self):
        for column, value in (("test_date", "1990-01-01"), ("heatmap_rank", "2")):
            with self.subTest(column=column):
                rows = copy.deepcopy(coefficient_rows())
                rows[0][column] = value
                with (
                    patch("mlr_figures.support.read_rows", return_value=rows),
                    self.assertRaises(ValueError),
                ):
                    load_selected_coefficients(Path("unused"))

    def test_paths_preserve_source_values_and_initial_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence(root)
            wealth, drawdowns = load_performance(
                root, default_figure_spec(FigureStyle()).model_order
            )
            for model in wealth:
                self.assertEqual(wealth[model].dates[0], date(1998, 9, 21))
                np.testing.assert_allclose(
                    wealth[model].values, [1, 0.9, 1.2, 1.1, 1.5]
                )
                np.testing.assert_allclose(
                    drawdowns[model].values, [0, -10, 0, -100 / 12, 0]
                )
            with gzip.open(root / PERFORMANCE_FILE, "rt") as stream:
                rows = list(csv.DictReader(stream))
            rows[0]["drawdown_pct"] = "0"
            write_csv(root / PERFORMANCE_FILE, rows)
            output = root / "figures"
            with self.assertRaisesRegex(ValueError, "initial capital"):
                render_figures(root, output, FigureStyle())
            self.assertFalse(output.exists())
            rows[0]["cumulative_net_return_pct"] = "-100"
            write_csv(root / PERFORMANCE_FILE, rows)
            with self.assertRaisesRegex(ValueError, "positive"):
                render_figures(root, output, FigureStyle())
            self.assertFalse(output.exists())

    def test_heatmap_uses_one_signed_scale_without_cell_annotations(self):
        for zero in (False, True):
            rows = coefficient_rows()
            if zero:
                for row in rows:
                    row["coefficient"] = "0"
            style = FigureStyle()
            with patch("mlr_figures.diagnostics.save_figure") as save:
                plot_selected_coefficients(
                    rows, Path("unused"), style, default_figure_spec(style)
                )
                fig = save.call_args.args[0]
                try:
                    axis, color_axis = fig.axes
                    norm = axis.collections[0].norm
                    self.assertEqual(norm.vmin, -norm.vmax)
                    self.assertEqual(norm.vcenter, 0)
                    self.assertEqual(axis.get_xlabel(), "Refit year")
                    self.assertEqual(color_axis.get_ylabel(), "Coefficient")
                    self.assertEqual(len(axis.texts), 0)
                    np.testing.assert_allclose(
                        axis.collections[0].get_array().ravel(),
                        [float(row["coefficient"]) for row in rows],
                    )
                finally:
                    plt.close(fig)

    def test_mobile_keeps_paths_and_model_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence(root)
            style = FigureStyle()
            spec = default_figure_spec(style)
            wealth, drawdowns = load_performance(root, spec.model_order)
            for mobile in (False, True):
                with patch("mlr_figures.performance.save_figure") as save:
                    plot_performance(
                        wealth, drawdowns, root, style, spec, mobile=mobile
                    )
                    fig = save.call_args.args[0]
                    try:
                        axis, drawdown_axis = fig.axes
                        lines = {line.get_label(): line for line in axis.lines}
                        self.assertEqual(
                            lines["OLS"].get_linewidth(), lines["Ridge"].get_linewidth()
                        )
                        self.assertNotEqual(
                            lines["OLS"].get_linestyle(), lines["Ridge"].get_linestyle()
                        )
                        np.testing.assert_allclose(
                            lines["OLS"].get_ydata(), [1, 0.9, 1.2, 1.1, 1.5]
                        )
                        self.assertEqual(len(drawdown_axis.collections), 1)
                        self.assertGreaterEqual(axis.get_ylim()[1], 1.5)
                        self.assertLessEqual(axis.get_ylim()[0], 0.9)
                        self.assertEqual(
                            sum(
                                t.get_text() == "Drawdown (%)"
                                for t in drawdown_axis.texts
                            ),
                            1,
                        )
                    finally:
                        plt.close(fig)

    def test_both_themes_export_matching_desktop_and_phone_compositions(self):
        import xml.etree.ElementTree as ET

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_evidence(root)
            output = root / "figures"
            for style in (FigureStyle(), dark_figure_style()):
                render_figures(root, output, style)
            for stem in (
                "top-coefficients",
                "performance-and-drawdowns",
                "performance-and-drawdowns_mobile",
            ):
                light = ET.parse(output / f"{stem}.svg").getroot()
                dark = ET.parse(output / f"{stem}_dark.svg").getroot()
                self.assertEqual(light.attrib["viewBox"], dark.attrib["viewBox"])
                for svg in (light, dark):
                    self.assertFalse(
                        any(node.tag.endswith("}image") for node in svg.iter())
                    )


if __name__ == "__main__":
    unittest.main()
