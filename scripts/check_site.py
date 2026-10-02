"""Validate built local links and vector assets; maintain intrinsic figure sizes."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


def read_posts(root: Path) -> dict[str, dict]:
    """Load published source identities; URLs are attributes, never identifiers."""
    posts = {}
    for path in sorted((root / "_posts").glob("*.md")):
        parts = path.read_text(encoding="utf-8").split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            raise ValueError(f"{path.name}: missing YAML front matter")
        metadata = yaml.safe_load(parts[1])
        if metadata.get("published", True) is False:
            continue
        if str(metadata.get("date", path.name[:10]))[:10] > date.today().isoformat():
            continue
        posts[path.relative_to(root).as_posix()] = {**metadata, "body": parts[2]}
    return posts


def check_source(root: Path) -> list[str]:
    """Reject source drift before Jekyll can overwrite colliding output files."""
    posts = read_posts(root)
    order = yaml.safe_load((root / "_data/reading_order.yml").read_text()) or []
    errors = []
    for identity, count in Counter(order).items():
        if identity not in posts or count != 1:
            errors.append(f"reading_order: unknown or repeated post {identity}")
    urls: dict[str, str] = {}
    for path in sorted(root.iterdir()):
        if path.suffix not in {".md", ".html"}:
            continue
        parts = path.read_text(encoding="utf-8").split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            continue
        page = yaml.safe_load(parts[1]) or {}
        url = page.get("permalink", f"/{path.stem}.html")
        urls[unquote(url).removesuffix("index.html").rstrip("/")] = path.name
    series: dict[str, list[tuple[int, str]]] = {}
    for identity, post in posts.items():
        if post.get("navigation") is not False and identity not in order:
            errors.append(f"{identity}: missing from reading_order")
        slug = Path(identity).name[11:-3]
        permalink = post.get("permalink", "")
        if permalink != f"/quants/{slug}.html":
            errors.append(
                f"{identity}: permalink must match file slug: /quants/{slug}.html"
            )
        redirects = post.get("redirect_from", [])
        if not isinstance(redirects, list):
            errors.append(f"{identity}: redirect_from must be a list")
            redirects = []
        for url in [permalink, *redirects]:
            if (
                not isinstance(url, str)
                or not url.startswith("/")
                or urlsplit(url).netloc
                or urlsplit(url).query
                or urlsplit(url).fragment
            ):
                errors.append(f"{identity}: invalid local URL {url!r}")
                continue
            normalized = unquote(url).removesuffix("index.html").rstrip("/")
            if normalized in urls:
                errors.append(
                    f"{identity}: URL collision {url} with {urls[normalized]}"
                )
            urls[normalized] = identity
        target = post.get("home_after")
        if target and (
            target not in posts
            or target == identity
            or posts[target].get("navigation") is False
            or posts[target].get("home_after")
        ):
            errors.append(
                f"{identity}: home_after must point to a listed top-level post"
            )
        if re.search(
            r"(?:https?://piinghel\.github\.io)?/quants?/[^\s)\"<]+", post["body"]
        ):
            errors.append(f"{identity}: use a Liquid link tag for article links")
        for field in ("title", "description", "article_label", "categories", "date"):
            if not post.get(field):
                errors.append(f"{identity}: missing {field}")
        if not isinstance(post.get("categories"), list) or len(post["categories"]) != 1:
            errors.append(f"{identity}: use one category for homepage and RSS")
        if bool(post.get("series_id")) != bool(post.get("series_order")):
            errors.append(f"{identity}: series_id and series_order must be paired")
        if post.get("series_id"):
            series.setdefault(post["series_id"], []).append(
                (post["series_order"], identity)
            )
        for repository in post.get("github_repositories", []):
            if not repository.get("label") or not re.fullmatch(
                r"https://github.com/[\w.-]+/[\w.-]+/?", repository.get("url", "")
            ):
                errors.append(f"{identity}: invalid repository metadata")
    for name, members in series.items():
        members.sort()
        identities = [identity for _, identity in members]
        if [number for number, _ in members] != list(range(1, len(members) + 1)):
            errors.append(f"{name}: series numbering must be consecutive")
        positions = [
            order.index(identity) for identity in identities if identity in order
        ]
        if len(positions) != len(members) or positions != list(
            range(min(positions, default=0), min(positions, default=0) + len(members))
        ):
            errors.append(f"{name}: series must be consecutive in reading_order")
    config = yaml.safe_load((root / "_config.yml").read_text())
    for link in config.get("header_links", []):
        if link.get("post") not in posts:
            errors.append(f"header_links: unknown post {link.get('post')}")
    # Documentation points at the actual catalogue instead of duplicating its sequence.
    guides = [root / "README.md", root / "AGENTS.md", *root.glob(".agents/**/*.md")]
    for guide in guides:
        text = guide.read_text()
        for target in re.findall(
            r"`((?:_posts|scripts|_includes|_layouts)/[^`\s]+)`", text
        ):
            if not (root / target).exists():
                errors.append(
                    f"{guide.relative_to(root)}: stale file reference {target}"
                )
    return errors


def check_post_output(source: Path, destination: Path) -> list[str]:
    """Verify redirects and homepage membership against the source catalogue."""
    errors = []
    homepage = Page((destination / "index.html").read_text())
    for identity, post in read_posts(source).items():
        url = post["permalink"]
        target = destination / url.lstrip("/")
        if not target.is_file():
            errors.append(f"{identity}: canonical page missing: {url}")
        if post.get("navigation") is not False and url not in homepage.links:
            errors.append(f"{identity}: missing from homepage")
        for redirect in post.get("redirect_from", []):
            path = destination / redirect.lstrip("/")
            if path.is_dir():
                path /= "index.html"
            if not path.is_file():
                errors.append(f"{identity}: redirect missing: {redirect}")
            elif url not in [
                urlsplit(link).path for link in Page(path.read_text()).links
            ]:
                errors.append(
                    f"{identity}: redirect does not resolve to {url}: {redirect}"
                )
    return errors


class Page(HTMLParser):
    def __init__(self, content: str) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.feed(content)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(str(attributes["id"]))
        for key in ("href", "src"):
            if attributes.get(key):
                self.links.append(str(attributes[key]))
        if tag in {"source", "img"} and attributes.get("srcset"):
            # Site picture sources contain file URLs, never inline data URLs.
            self.links.extend(
                candidate.strip().split()[0]
                for candidate in str(attributes["srcset"]).split(",")
                if candidate.strip()
            )
        if tag == "img":
            self.images.append(attributes)


def figure_dimensions(root: Path) -> dict[str, dict[str, int]]:
    dimensions = {}
    for path in sorted((root / "assets").rglob("*.svg")):
        tree = ET.parse(path)
        svg = tree.getroot()
        ids = {element.attrib["id"] for element in svg.iter() if "id" in element.attrib}
        for element in svg.iter():
            if element.tag.rsplit("}", 1)[-1] == "image":
                raise ValueError(f"Raster embedded in vector figure: {path}")
            for key, value in element.attrib.items():
                references = re.findall(r"url\(#([^)]*)\)", value)
                if key.rsplit("}", 1)[-1] == "href" and value.startswith("#"):
                    references.append(value[1:])
                if any(reference not in ids for reference in references):
                    raise ValueError(f"Unresolved SVG reference in {path}")
        if path.stem.endswith("_dark"):
            continue
        viewbox = [float(value) for value in svg.attrib["viewBox"].split()]
        dark = path.with_name(path.stem + "_dark.svg")
        if (
            dark.exists()
            and ET.parse(dark).getroot().attrib["viewBox"] != svg.attrib["viewBox"]
        ):
            raise ValueError(f"Theme compositions have different dimensions: {path}")
        dimensions["/" + path.relative_to(root).with_suffix("").as_posix()] = {
            "width": round(viewbox[2]),
            "height": round(viewbox[3]),
        }
    return dimensions


def check_site(destination: Path) -> list[str]:
    root = destination.resolve()
    pages = {
        path: Page(path.read_text(encoding="utf-8")) for path in root.rglob("*.html")
    }
    errors = []
    if not (root / "index.html").exists():
        return ["Missing site index.html"]
    for path, page in pages.items():
        for link in page.links:
            target = urlsplit(link)
            if target.scheme in {"mailto", "tel", "data", "javascript"}:
                continue
            if target.netloc and target.hostname not in {
                "piinghel.github.io",
                "localhost",
                "127.0.0.1",
            }:
                continue
            relative = unquote(target.path)
            resolved = (
                (
                    root / relative.lstrip("/")
                    if relative.startswith("/")
                    else path.parent / relative
                ).resolve()
                if relative
                else path
            )
            if resolved.is_dir():
                resolved /= "index.html"
            if not resolved.is_relative_to(root) or not resolved.exists():
                errors.append(f"{path.relative_to(root)}: missing {link}")
            elif (
                target.fragment
                and resolved in pages
                and unquote(target.fragment) not in pages[resolved].ids
            ):
                errors.append(f"{path.relative_to(root)}: missing fragment {link}")
        for attributes in page.images:
            if not attributes.get("alt"):
                errors.append(
                    f"{path.relative_to(root)}: image without meaningful alt text"
                )
    for private in ("AGENTS.md", "README.md", "scripts", "tests", "_drafts"):
        if (root / private).exists():
            errors.append(f"Private development material was published: {private}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", type=Path)
    parser.add_argument("--update-dimensions", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = check_source(root)
    if errors:
        raise SystemExit("\n".join(errors))
    dimensions = figure_dimensions(root)
    metadata = root / "_data" / "figure_dimensions.json"
    if args.update_dimensions:
        metadata.write_text(json.dumps(dimensions, indent=2) + "\n", encoding="utf-8")
    elif json.loads(metadata.read_text(encoding="utf-8")) != dimensions:
        raise SystemExit("Figure dimensions are stale; run --update-dimensions")
    if args.destination:
        errors = check_site(args.destination) + check_post_output(
            root, args.destination
        )
        if errors:
            raise SystemExit("\n".join(errors))
    print(f"Validated {len(dimensions)} vector figure bases and local site references.")


if __name__ == "__main__":
    main()
