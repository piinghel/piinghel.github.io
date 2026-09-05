import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_site import check_site, figure_dimensions
from mlr_figures.support import load_daily_series, load_selected_coefficients


class FigureInputTests(unittest.TestCase):
    def test_size_check_preserves_selection_for_monotone_scores(self):
        import datetime

        import polars as pl
        from check_benchmark_size import summarize_size_choices

        factors = [
            "defensive",
            "momentum",
            "short_positioning",
            "size",
            "return_consistency",
        ]
        frame = pl.DataFrame(
            {
                "date": [datetime.date(2020, 1, 2)] * 160,
                "asset_id_bb_global": [f"stock-{i:03d}" for i in range(160)],
                **{name: [i / 160 for i in range(160)] for name in factors},
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scores.parquet"
            frame.write_parquet(path)
            result = summarize_size_choices(path)
            self.assertEqual(result["replaced_names"].to_list(), [0.0, 0.0])
            for correlation in result["rank_correlation"]:
                self.assertAlmostEqual(correlation, 1.0)
            pl.concat([frame, frame.head(1)]).write_parquet(path)
            with self.assertRaisesRegex(ValueError, "duplicate"):
                summarize_size_choices(path)

    def test_series_sort_and_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "series.csv"
            rows = [
                ["A", "2022-01-04", "0.2"],
                ["A", "2022-01-03", "0.1"],
                ["B", "2022-01-03", "0.3"],
                ["B", "2022-01-04", "0.4"],
            ]

            def write(values):
                with path.open("w", newline="", encoding="utf-8") as output:
                    writer = csv.writer(output)
                    writer.writerow(["model", "date", "value"])
                    writer.writerows(values)

            write(rows)
            result = load_daily_series(
                path, value_column="value", model_order=("A", "B")
            )
            self.assertEqual(result["A"].values.tolist(), [0.1, 0.2])
            for corrupted in (
                rows + [rows[0]],
                rows[:-1],
                [["A", "2022-01-04", "nan"], *rows[1:]],
            ):
                write(corrupted)
                with self.assertRaises(ValueError):
                    load_daily_series(
                        path, value_column="value", model_order=("A", "B")
                    )

    def test_coefficient_duplicates_are_not_silently_overwritten(self):
        rows = [{"feature": "x", "fold_id": "1", "heatmap_rank": "1"}] * 2
        with (
            patch("mlr_figures.support.read_rows", return_value=rows),
            self.assertRaisesRegex(ValueError, "duplicate"),
        ):
            load_selected_coefficients(Path("unused"))

    def test_local_link_checker_checks_fragments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                '<h1 id="ok">Test</h1><a href="#ok">Good</a>', encoding="utf-8"
            )
            self.assertEqual(check_site(root), [])
            (root / "index.html").write_text(
                '<a href="#missing">Bad</a>', encoding="utf-8"
            )
            self.assertIn("missing fragment", check_site(root)[0])

    def test_published_svgs_have_resolved_vector_references(self):
        dimensions = figure_dimensions(Path(__file__).resolve().parents[1])
        self.assertIn("/assets/tranching/timing-dispersion", dimensions)

    def test_local_link_checker_checks_mobile_picture_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text(
                '<picture><source media="(max-width:600px)" '
                'srcset="/mobile.svg?v=1 1x, /mobile-dark.svg 2x"></picture>',
                encoding="utf-8",
            )
            errors = check_site(root)
            self.assertEqual(len(errors), 2)
            (root / "mobile.svg").touch()
            (root / "mobile-dark.svg").touch()
            self.assertEqual(check_site(root), [])


if __name__ == "__main__":
    unittest.main()
