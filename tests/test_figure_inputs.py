import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_site import check_site


class FigureInputTests(unittest.TestCase):
    def test_build_checker_rejects_unlinked_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text("<h1>Test</h1>", encoding="utf-8")
            assets = root / "assets"
            assets.mkdir()
            (assets / "results.csv").write_text("a,b\n1,2\n", encoding="utf-8")
            self.assertEqual(
                check_site(root), ["CSV file was published: assets/results.csv"]
            )

    def test_exhibit_numbers_follow_separate_sequences_in_each_article(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            article = root / "index.html"
            figure = '<p id="figure-1" class="figure-caption"><span>Figure 1.</span> Growth.</p>'
            table = '<table id="table-1" class="research-table"><caption>Table 1. Settings.</caption></table>'
            matrix = '<table class="worked-matrix"><caption>Covariance matrix</caption></table>'
            article.write_text(figure + matrix + table)
            self.assertEqual(check_site(root), [])
            article.write_text(figure.replace('id="figure-1"', '') + table)
            self.assertIn("missing anchor for Figure 1.", check_site(root)[0])
            article.write_text(figure + table + figure)
            self.assertIn("expected Figure 2.", check_site(root)[0])

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
