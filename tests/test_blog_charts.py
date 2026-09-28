import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from blog_charts import series, statistics, write_chart


class ChartExportTests(unittest.TestCase):
    def test_rejects_invalid_returns_and_unapproved_metadata(self):
        for value in [float("nan"), float("inf"), -1]:
            with self.assertRaises(ValueError):
                series("test", "Test", "strategy", [value])
        with self.assertRaises(ValueError):
            series("test", "Test", "strategy", [0], raw_metadata="private")

    def test_rejects_missing_calendar_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                write_chart(Path(temp) / "test.json", ["2025-01-01", "2025-01-02"],
                            [series("test", "Test", "strategy", [0])], {})

    def test_decile_full_window_matches_article(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "assets/2024-12-15-low-volatility-factor/deciles.json").read_text())
        values = [statistics([v / data["scale"] for v in s["values"]]) for s in data["series"] if s["id"].startswith("decile_")]
        self.assertEqual([f'{values[i]["sharpe"]:.2f}' for i in [0, 9]], ["0.90", "0.20"])
        self.assertEqual(f'{values[-1]["annual_return"] * 100:.1f}', "0.3")
        self.assertEqual(f'{min(v["annual_return"] for v in values[:7]) * 100:.1f}', "10.5")
        self.assertEqual(f'{max(v["annual_return"] for v in values[:7]) * 100:.1f}', "11.6")
