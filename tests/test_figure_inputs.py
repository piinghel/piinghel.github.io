import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_site import check_site, figure_dimensions


class FigureInputTests(unittest.TestCase):
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
        self.assertIn("/assets/tranching/calendar-grid", dimensions)

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
