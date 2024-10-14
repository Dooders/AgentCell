import unittest
from unittest.mock import patch

from pyology.exceptions import (
    InsufficientMetaboliteError,
    QuantityError,
    UnknownMetaboliteError,
)
from pyology.organelle import Organelle


class TestOrganelle(unittest.TestCase):

    def setUp(self):
        self.organelle = Organelle()

    def test_initial_metabolite_setup(self):
        self.assertIn("glucose", self.organelle.metabolites)
        self.assertIn("atp", self.organelle.metabolites)
        self.assertEqual(self.organelle.metabolites["atp"].quantity, 100)

    def test_validate_initial_state(self):
        # Initial state should be valid
        try:
            self.organelle.validate_initial_state()
        except ValueError:
            self.fail("validate_initial_state raised ValueError unexpectedly")

    def test_invalid_glycolysis_rate(self):
        with self.assertRaises(ValueError):
            self.organelle.set_glycolysis_rate(0)

    def test_add_metabolite(self):
        self.organelle.add_metabolite("test_metabolite", 50, 100)
        self.assertIn("test_metabolite", self.organelle.metabolites)
        self.assertEqual(self.organelle.metabolites["test_metabolite"].quantity, 50)

    def test_add_metabolite_with_existing(self):
        self.organelle.add_metabolite("glucose", 50, 1000)
        self.assertEqual(self.organelle.metabolites["glucose"].quantity, 50)

    def test_add_metabolite_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.organelle.add_metabolite("test_metabolite", -10, 100)

    def test_change_metabolite_quantity(self):
        self.organelle.change_metabolite_quantity("glucose", 100)
        self.assertEqual(self.organelle.metabolites["glucose"].quantity, 100)

    def test_change_metabolite_quantity_invalid(self):
        with self.assertRaises(UnknownMetaboliteError):
            self.organelle.change_metabolite_quantity("unknown_metabolite", 50)

        with self.assertRaises(QuantityError):
            self.organelle.change_metabolite_quantity(
                "glucose", -1000
            )  # would reduce below zero

        with self.assertRaises(QuantityError):
            self.organelle.change_metabolite_quantity(
                "glucose", 2000
            )  # exceed max quantity

    def test_is_metabolite_available(self):
        self.assertTrue(self.organelle.is_metabolite_available("atp", 50))
        self.assertFalse(self.organelle.is_metabolite_available("atp", 200))

    def test_is_metabolite_available_unknown(self):
        with self.assertRaises(UnknownMetaboliteError):
            self.organelle.is_metabolite_available("unknown_metabolite", 10)

    def test_consume_metabolites(self):
        self.organelle.consume_metabolites(atp=50)
        self.assertEqual(self.organelle.metabolites["atp"].quantity, 50)

    def test_consume_metabolites_insufficient(self):
        with self.assertRaises(InsufficientMetaboliteError):
            self.organelle.consume_metabolites(atp=200)

    def test_produce_metabolites(self):
        self.organelle.produce_metabolites(glucose=50)
        self.assertEqual(self.organelle.metabolites["glucose"].quantity, 50)

    def test_produce_metabolites_exceed_max(self):
        with self.assertRaises(QuantityError):
            self.organelle.produce_metabolites(atp=2000)  # exceeding max quantity


if __name__ == "__main__":
    unittest.main()
