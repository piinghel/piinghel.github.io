"""Illustrate false discoveries and power under simple correlated z-tests.

Run with: python3 scripts/simulate_multiple_testing.py
Requires NumPy and SciPy. Each scenario has 20,000 independent repetitions.
"""

import numpy as np
from scipy.stats import norm


def summarize(p_values: np.ndarray, true_effects: int) -> None:
    """Print the rate of any false rejection, FDR, and per-signal power."""
    n_tests = p_values.shape[1]
    order = np.argsort(p_values, axis=1)
    ordered_p = np.take_along_axis(p_values, order, axis=1)
    ranks = np.arange(1, n_tests + 1)
    holm = np.logical_and.accumulate(
        ordered_p <= 0.05 / (n_tests - ranks + 1), axis=1
    )
    bh_count = np.where(ordered_p <= 0.05 * ranks / n_tests, ranks, 0).max(axis=1)
    bh = ranks <= bh_count[:, None]
    methods = {
        "Unadjusted": ordered_p <= 0.05,
        "Bonferroni": ordered_p <= 0.05 / n_tests,
        "Holm": holm,
        "Benjamini-Hochberg": bh,
    }
    for name, rejected in methods.items():
        false = ((order >= true_effects) & rejected).sum(axis=1)
        true = ((order < true_effects) & rejected).sum(axis=1)
        total = rejected.sum(axis=1)
        any_false = (false > 0).mean()
        fdr = (false / np.maximum(total, 1)).mean()
        power = true.mean() / true_effects if true_effects else float("nan")
        print(f"{name:19s} any false={any_false:.4f}  FDR={fdr:.4f}  power={power:.4f}")


def main() -> None:
    rng = np.random.default_rng(20261027)
    repetitions, n_tests = 20_000, 100
    for rho in (0.0, 0.5):
        for true_effects in (0, 10):
            common = rng.standard_normal((repetitions, 1))
            individual = rng.standard_normal((repetitions, n_tests))
            z = np.sqrt(rho) * common + np.sqrt(1 - rho) * individual
            z[:, :true_effects] += 2.5
            print(f"\nrho={rho}, true signals={true_effects}")
            summarize(norm.sf(z), true_effects)


if __name__ == "__main__":
    main()
