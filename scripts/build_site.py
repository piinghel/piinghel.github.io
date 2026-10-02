"""Build only validated sources, then check the rendered site before publishing."""

from pathlib import Path
import subprocess
import sys

from check_site import check_source


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    errors = check_source(root)
    if errors:
        raise SystemExit("\n".join(errors))
    subprocess.run(["bundle", "exec", "jekyll", "build"], cwd=root, check=True)
    subprocess.run(
        [sys.executable, "scripts/check_site.py", "_site"], cwd=root, check=True
    )


if __name__ == "__main__":
    main()
