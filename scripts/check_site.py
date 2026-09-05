"""Validate built local links and vector assets; maintain intrinsic figure sizes."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


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
    dimensions = figure_dimensions(root)
    metadata = root / "_data" / "figure_dimensions.json"
    if args.update_dimensions:
        metadata.write_text(json.dumps(dimensions, indent=2) + "\n", encoding="utf-8")
    elif json.loads(metadata.read_text(encoding="utf-8")) != dimensions:
        raise SystemExit("Figure dimensions are stale; run --update-dimensions")
    if args.destination:
        errors = check_site(args.destination)
        if errors:
            raise SystemExit("\n".join(errors))
    print(f"Validated {len(dimensions)} vector figure bases and local site references.")


if __name__ == "__main__":
    main()
