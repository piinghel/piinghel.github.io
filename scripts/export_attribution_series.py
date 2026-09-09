"""Export aggregate series exhibits from the saved, validated diagnostics."""

import argparse
import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets/portfolio-attribution"


def export(diagnostics: Path, beta_history: Path) -> None:
    history = json.loads(beta_history.read_text())
    history.update(json.loads((diagnostics / "series-history.json").read_text()))
    history["windows_sessions"] = [126, 252]
    results = json.loads((diagnostics / "results.json").read_text())
    results["original_summaries"] = [
        row for row in results["original_summaries"] if row["period"] == "full"
    ]
    for name, data in [("beta-history.json", history), ("series-diagnostics.json", results)]:
        (ASSETS / name).write_text(json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n")
    # The public explorer now displays only aggregate recovery paths.
    path = ASSETS / "explorer-paths.json"
    paths = json.loads(path.read_text())
    paths = {key: paths[key] for key in ["recovery_columns", "recoveries"]}
    path.write_text(json.dumps(paths, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostics", type=Path, required=True)
    parser.add_argument("--beta-history", type=Path, required=True)
    args = parser.parse_args()
    export(args.diagnostics, args.beta_history)
