import unittest
from fractions import Fraction
from pathlib import Path

import yaml


def multiply(left, right):
    columns = tuple(zip(*right, strict=True))
    return tuple(
        tuple(sum(x * y for x, y in zip(row, column, strict=True)) for column in columns)
        for row in left
    )


class FactorRiskExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "_data/factor_risk_example.yml"
        tables = yaml.safe_load(path.read_text())
        cls.matrices = {
            name: tuple(
                tuple(Fraction(str(value)) for value in row) for row in table["values"]
            )
            for name, table in tables.items()
        }

    def test_factor_risk_and_spread(self):
        matrices = self.matrices
        exposures = matrices["exposures"]
        self.assertEqual(tuple(row[0] for row in exposures), (1, 1, 1))
        transposed = tuple(zip(*exposures, strict=True))
        self.assertEqual(transposed, matrices["transposed_exposures"])
        scaled = multiply(exposures, matrices["factor_covariance"])
        self.assertEqual(scaled, matrices["scaled_exposures"])
        factor_risk = multiply(scaled, transposed)
        self.assertEqual(factor_risk, matrices["factor_stock_covariance"])
        variance = (4, 4, 1)
        total = tuple(
            tuple(value + variance[i] if i == j else value for j, value in enumerate(row))
            for i, row in enumerate(factor_risk)
        )
        self.assertEqual(total, matrices["total_stock_covariance"])
        spread = ((Fraction(1, 2),), (Fraction(-1, 2),), (0,))
        self.assertEqual(multiply(transposed, spread), ((0,), (1,)))
        self.assertEqual(
            multiply(tuple(zip(*spread, strict=True)), multiply(total, spread)),
            ((3,),),
        )

    def test_residual_covariance_and_pca(self):
        matrices = self.matrices
        observations = matrices["standardized_residuals"]
        transposed = tuple(zip(*observations, strict=True))
        self.assertTrue(all(sum(column) == 0 for column in transposed))
        cross_products = multiply(transposed, observations)
        standardized_correlation = tuple(
            tuple(value / len(observations) for value in row) for row in cross_products
        )
        correlation = matrices["residual_correlations"]
        self.assertEqual(standardized_correlation, correlation)
        scale = ((2, 0, 0), (0, 2, 0), (0, 0, 1))
        scaled = multiply(correlation, scale)
        self.assertEqual(scaled, matrices["scaled_correlations"])
        residual_risk = multiply(scale, scaled)
        self.assertEqual(residual_risk, matrices["residual_covariance"])
        total = tuple(
            tuple(x + y for x, y in zip(a, b, strict=True))
            for a, b in zip(matrices["factor_stock_covariance"], residual_risk, strict=True)
        )
        spread = ((Fraction(1, 2),), (Fraction(-1, 2),), (0,))
        self.assertEqual(
            multiply(tuple(zip(*spread, strict=True)), multiply(total, spread)),
            ((Fraction(9, 5),),),
        )
        self.assertEqual(
            multiply(correlation, ((1,), (1,), (0,))),
            ((Fraction(8, 5),), (Fraction(8, 5),), (0,)),
        )
