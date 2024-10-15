import unittest
from threading import Thread
from unittest.mock import Mock

from pyology.exceptions import (
    InsufficientMetaboliteError,
    QuantityError,
    UnknownMetaboliteError,
)
from pyology.metabolite import Metabolite, Metabolites


class TestMetabolite(unittest.TestCase):
    def setUp(self):
        self.callback = Mock()
        self.metabolite = Metabolite(
            name="Glucose",
            type="Sugar",
            quantity=100.0,
            max_quantity=1000.0,
            min_quantity=50.0,
            unit="mM",
            metadata={"source": "blood"},
            on_change=self.callback,
        )

    def test_initialization(self):
        self.assertEqual(self.metabolite.name, "Glucose")
        self.assertEqual(self.metabolite.type, "Sugar")
        self.assertEqual(self.metabolite.quantity, 100.0)
        self.assertEqual(self.metabolite.max_quantity, 1000.0)
        self.assertEqual(self.metabolite.min_quantity, 50.0)
        self.assertEqual(self.metabolite.unit, "mM")
        self.assertEqual(self.metabolite.metadata, {"source": "blood"})
        self.assertIsNotNone(self.metabolite.lock)

    def test_adjust_quantity_within_limits(self):
        self.metabolite.adjust_quantity(200.0)
        self.assertEqual(self.metabolite.quantity, 300.0)
        self.callback.assert_called_once_with(self.metabolite)

    def test_adjust_quantity_below_minimum(self):
        with self.assertRaises(QuantityError):
            self.metabolite.adjust_quantity(-60.0)  # 100 - 60 = 40 < min_quantity=50
        self.callback.assert_not_called()

    def test_adjust_quantity_above_maximum(self):
        with self.assertRaises(QuantityError):
            self.metabolite.adjust_quantity(
                950.0
            )  # 100 + 950 = 1050 > max_quantity=1000
        self.callback.assert_not_called()

    def test_reset(self):
        self.metabolite.adjust_quantity(200.0)  # Quantity becomes 300
        self.callback.reset_mock()
        self.metabolite.reset()
        self.assertEqual(self.metabolite.quantity, self.metabolite.min_quantity)
        self.callback.assert_called_once_with(self.metabolite)

    def test_percentage_filled(self):
        percentage = self.metabolite.percentage_filled
        expected = (100.0 / 1000.0) * 100
        self.assertEqual(percentage, expected)

    def test_to_dict(self):
        expected_dict = {
            "name": "Glucose",
            "type": "Sugar",
            "quantity": 100.0,
            "max_quantity": 1000.0,
            "min_quantity": 50.0,
            "unit": "mM",
            "metadata": {"source": "blood"},
        }
        self.assertEqual(self.metabolite.to_dict(), expected_dict)

    def test_from_dict(self):
        data = {
            "name": "ATP",
            "type": "Energy",
            "quantity": 50.0,
            "max_quantity": 500.0,
            "min_quantity": 10.0,
            "unit": "mM",
            "metadata": {"source": "mitochondria"},
        }
        metabolite = Metabolite.from_dict(data)
        self.assertEqual(metabolite.name, "ATP")
        self.assertEqual(metabolite.type, "Energy")
        self.assertEqual(metabolite.quantity, 50.0)
        self.assertEqual(metabolite.max_quantity, 500.0)
        self.assertEqual(metabolite.min_quantity, 10.0)
        self.assertEqual(metabolite.unit, "mM")
        self.assertEqual(metabolite.metadata, {"source": "mitochondria"})

    def test_repr(self):
        expected_repr = (
            "Metabolite(name='Glucose', quantity=100.0, "
            "max_quantity=1000.0, unit='mM', type='Sugar')"
        )
        self.assertEqual(repr(self.metabolite), expected_repr)

    def test_thread_safety_adjust_quantity(self):
        """
        Tests that multiple threads adjusting the quantity do not cause race conditions.
        """

        def adjust(amount, times):
            for _ in range(times):
                try:
                    self.metabolite.adjust_quantity(amount)
                except QuantityError:
                    pass  # Ignore quantity errors for this test

        threads = []
        for _ in range(10):
            t = Thread(target=adjust, args=(10.0, 10))  # Each thread tries to add 100
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # The maximum quantity is 1000. Starting from 100, adding up to 1000
        self.assertLessEqual(self.metabolite.quantity, self.metabolite.max_quantity)


class TestMetabolites(unittest.TestCase):
    def setUp(self):
        self.metabolites = Metabolites()
        self.metabolites.register(
            glucose=(100, 1000),
            atp=(50, 500),
        )

    def test_initialization(self):
        self.assertEqual(len(self.metabolites), 2)
        self.assertIn("glucose", self.metabolites)
        self.assertIn("atp", self.metabolites)

    def test_register_individual(self):
        self.metabolites.register(name="pyruvate", quantity=30, max_quantity=300)
        self.assertIn("pyruvate", self.metabolites)
        self.assertEqual(self.metabolites["pyruvate"].quantity, 30)
        self.assertEqual(self.metabolites["pyruvate"].max_quantity, 300)

    def test_register_bulk(self):
        self.metabolites.register(
            lactate=(20, 200),
            citrate=(10, 100),
        )
        self.assertIn("lactate", self.metabolites)
        self.assertIn("citrate", self.metabolites)
        self.assertEqual(self.metabolites["lactate"].quantity, 20)
        self.assertEqual(self.metabolites["citrate"].quantity, 10)

    def test_register_update_existing(self):
        self.metabolites.register(name="glucose", quantity=200, max_quantity=1000)
        self.assertEqual(self.metabolites["glucose"].quantity, 300)

    def test_register_invalid_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.metabolites.register(
                name="invalid_met", quantity=-10, max_quantity=100
            )

    def test_register_invalid_exceeds_max_quantity(self):
        with self.assertRaises(ValueError):
            self.metabolites.register(
                name="invalid_met", quantity=1500, max_quantity=1000
            )

    def test_change_quantity_normal(self):
        self.metabolites.change_quantity("glucose", 100.0)
        self.assertEqual(self.metabolites["glucose"].quantity, 200.0)

    def test_change_quantity_unknown_metabolite(self):
        with self.assertRaises(UnknownMetaboliteError):
            self.metabolites.change_quantity("unknown", 50.0)

    def test_change_quantity_invalid_name_type(self):
        with self.assertRaises(TypeError):
            self.metabolites.change_quantity(123, 50.0)

    def test_change_quantity_invalid_amount_type(self):
        with self.assertRaises(TypeError):
            self.metabolites.change_quantity("glucose", "fifty")

    def test_change_quantity_below_zero(self):
        with self.assertRaises(QuantityError):
            self.metabolites.change_quantity("atp", -100.0)  # ATP quantity is 50

    def test_change_quantity_above_max(self):
        with self.assertRaises(QuantityError):
            self.metabolites.change_quantity("atp", 500.0)  # ATP max is 500

    def test_is_available_true(self):
        self.assertTrue(self.metabolites.is_available("glucose", 50.0))

    def test_is_available_false(self):
        self.assertFalse(self.metabolites.is_available("atp", 100.0))

    def test_is_available_unknown_metabolite(self):
        with self.assertRaises(UnknownMetaboliteError):
            self.metabolites.is_available("unknown", 10.0)

    def test_consume_successful(self):
        self.metabolites.consume(glucose=50.0, atp=20.0)
        self.assertEqual(self.metabolites["glucose"].quantity, 50.0)
        self.assertEqual(self.metabolites["atp"].quantity, 30.0)

    def test_consume_insufficient_metabolite(self):
        with self.assertRaises(InsufficientMetaboliteError):
            self.metabolites.consume(glucose=150.0)  # Only 100 available

    def test_consume_unknown_metabolite(self):
        with self.assertRaises(InsufficientMetaboliteError):
            self.metabolites.consume(unknown=10.0)

    def test_produce_successful(self):
        self.metabolites.produce(glucose=200.0, atp=100.0)
        self.assertEqual(self.metabolites["glucose"].quantity, 300.0)
        self.assertEqual(self.metabolites["atp"].quantity, 150.0)

    def test_produce_unknown_metabolite(self):
        with self.assertRaises(UnknownMetaboliteError):
            self.metabolites.produce(unknown=50.0)

    def test_validate_all_successful(self):
        try:
            self.metabolites.validate_all()
        except ValueError:
            self.fail("validate_all() raised ValueError unexpectedly!")

    def test_validate_all_failure(self):
        # Manually set an invalid quantity
        self.metabolites["glucose"].quantity = -10.0
        with self.assertRaises(ValueError):
            self.metabolites.validate_all()

    def test_dict_like_behavior_get(self):
        glucose = self.metabolites["glucose"]
        self.assertIsInstance(glucose, Metabolite)
        self.assertEqual(glucose.name, "glucose")

    def test_dict_like_behavior_set(self):
        new_met = Metabolite(
            name="fructose",
            type="Sugar",
            quantity=80.0,
            max_quantity=800.0,
        )
        self.metabolites["fructose"] = new_met
        self.assertIn("fructose", self.metabolites)
        self.assertEqual(self.metabolites["fructose"].quantity, 80.0)

    def test_dict_like_behavior_delete(self):
        del self.metabolites["atp"]
        self.assertNotIn("atp", self.metabolites)
        self.assertEqual(len(self.metabolites), 1)

    def test_dict_like_behavior_iter(self):
        keys = set()
        for key in self.metabolites:
            keys.add(key)
        self.assertEqual(keys, {"glucose", "atp"})

    def test_dict_like_behavior_len(self):
        self.assertEqual(len(self.metabolites), 2)
        self.metabolites.register(name="pyruvate", quantity=30, max_quantity=300)
        self.assertEqual(len(self.metabolites), 3)

    def test_dict_like_behavior_contains(self):
        self.assertIn("glucose", self.metabolites)
        self.assertNotIn("lactate", self.metabolites)

    def test_items_keys_values(self):
        items = self.metabolites.items()
        keys = self.metabolites.keys()
        values = self.metabolites.values()
        self.assertIn(("glucose", self.metabolites["glucose"]), items)
        self.assertIn("glucose", keys)
        self.assertIn(self.metabolites["glucose"], values)


if __name__ == "__main__":
    unittest.main()
