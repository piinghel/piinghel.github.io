import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_site import check_source, check_site, check_post_output


class SiteMetadataTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "_posts").mkdir()
        (self.root / "_data").mkdir()
        for name, text in (("_config.yml", "{}"), ("README.md", ""), ("AGENTS.md", "")):
            (self.root / name).write_text(text)
        self.first = "_posts/2020-01-01-first.md"
        self.second = "_posts/2020-01-02-second.md"
        self.post(self.first)
        self.post(self.second)
        self.order([self.first, self.second])

    def order(self, identities):
        (self.root / "_data/reading_order.yml").write_text(yaml.safe_dump(identities))

    def post(self, identity, body="", **changes):
        data = dict(
            title="Title",
            description="Description",
            article_label="Research",
            categories=["Research"],
            date=identity[7:17],
            permalink=f"/quants/{Path(identity).name[11:-3]}.html",
        )
        data.update(changes)
        (self.root / identity).write_text(
            "---\n" + yaml.safe_dump(data) + "---\n" + body
        )

    def errors(self):
        return "\n".join(check_source(self.root))

    def test_reading_order_requires_each_visible_post_once(self):
        self.assertEqual(self.errors(), "")
        self.order([self.first, self.first, "missing.md"])
        self.assertIn("missing from reading_order", self.errors())
        self.assertIn("unknown or repeated", self.errors())
        self.post(self.second, navigation=False)
        self.order([self.first])
        self.assertEqual(self.errors(), "")

    def test_slug_and_url_collisions(self):
        self.post(self.first, permalink="/quants/wrong.html")
        self.assertIn("permalink must match", self.errors())
        self.post(self.first, redirect_from=["/quants/second.html"])
        self.assertIn("URL collision", self.errors())
        self.post(self.first, redirect_from=["/old.html", "/old.html"])
        self.assertIn("URL collision", self.errors())

    def test_home_after_rejects_stale_targets_and_cycles(self):
        self.post(self.second, home_after=self.first)
        self.assertEqual(self.errors(), "")
        self.post(self.first, home_after=self.second)
        self.assertIn("home_after", self.errors())
        self.post(self.first)
        self.post(self.second, home_after="/quants/first.html")
        self.assertIn("home_after", self.errors())

    def test_redirect_cannot_overwrite_a_standalone_page(self):
        (self.root / "about.md").write_text("---\npermalink: /about/\n---\nAbout")
        self.post(self.first, redirect_from=["/about/index.html"])
        self.assertIn("URL collision", self.errors())

    def test_article_links_use_source_paths(self):
        for url in ("/quant/2020/01/01/first.html", "/quants/first.html"):
            self.post(self.second, body=f"[First]({url})")
            self.assertIn("Liquid link", self.errors())
        self.post(
            self.second, body="[First]({% link _posts/2020-01-01-first.md %}#section)"
        )
        self.assertEqual(self.errors(), "")

    def test_cross_article_fragment_validation(self):
        (self.root / "index.html").write_text('<a href="/other.html#missing">Other</a>')
        (self.root / "other.html").write_text('<h1 id="present">Other</h1>')
        self.assertIn("missing fragment", "\n".join(check_site(self.root)))

    def test_numbered_series_cannot_be_reversed(self):
        self.post(self.first, series_id="series", series_order=1)
        self.post(self.second, series_id="series", series_order=2)
        self.assertEqual(self.errors(), "")
        self.order([self.second, self.first])
        self.assertIn("series must be consecutive", self.errors())

    def test_redirect_target_and_homepage_membership(self):
        self.post(self.first, redirect_from=["/old.html"])
        (self.root / "index.html").write_text(
            '<a href="/quants/second.html">Second</a>'
        )
        (self.root / "quants").mkdir()
        for slug in ("first", "second"):
            (self.root / f"quants/{slug}.html").write_text("Article")
        (self.root / "old.html").write_text('<a href="/quants/second.html">Wrong</a>')
        errors = "\n".join(check_post_output(self.root, self.root))
        self.assertIn("missing from homepage", errors)
        self.assertIn("redirect does not resolve", errors)


if __name__ == "__main__":
    unittest.main()
