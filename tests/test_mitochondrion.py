import logging
import math
import unittest
from unittest.mock import MagicMock, patch

from cell_modeling.pyology.constants import *
from cell_modeling.pyology.mitochondrion import Mitochondrion

# Define constants for testing
CALCIUM_THRESHOLD = 500
CALCIUM_BOOST_FACTOR = 1.5
MAX_PROTON_GRADIENT = 1000
LEAK_RATE = 10
LEAK_STEEPNESS = 0.1
LEAK_MIDPOINT = 500
PROTONS_PER_NADH = 10
PROTONS_PER_FADH2 = 6
PROTONS_PER_ATP = 4
SHUTTLE_EFFICIENCY = 0.8


# Simple Metabolite class for testing
class Metabolite:
    def __init__(self, name, quantity, max_quantity=None):
        self.name = name
        self.quantity = quantity
        self.max_quantity = max_quantity if max_quantity is not None else float("inf")


# Simple Organelle base class for testing
class Organelle:
    def __init__(self):
        self.metabolites = {}

    def add_metabolite(self, name, quantity, max_quantity=None):
        self.metabolites[name] = Metabolite(name, quantity, max_quantity)


# Mock KrebsCycle class for testing
class KrebsCycle:
    def __init__(self):
        self.cofactors = {"NADH": 0, "FADH2": 0, "GTP": 0}
        self.enzymes = {
            "citrate_synthase": MagicMock(activity=1.0),
            "isocitrate_dehydrogenase": MagicMock(activity=1.0),
        }

    def add_substrate(self, substrate, amount):
        pass

    def krebs_cycle_iterator(self, num_cycles):
        for _ in range(num_cycles):
            yield ({}, {"NADH": 3, "FADH2": 1, "GTP": 1})

    def reaction_iterator(self):
        yield ("reaction1", True)

    def metabolite_iterator(self):
        return iter(self.cofactors.items())

    def reset(self):
        self.cofactors = {"NADH": 0, "FADH2": 0, "GTP": 0}


# Import the Mitochondrion class code provided above
# Assuming it is available in the current context

# Configure logger for testing
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)

import unittest


class TestMitochondrion(unittest.TestCase):
    def setUp(self):
        self.mito = Mitochondrion()

    def test_change_metabolite_quantity_increase(self):
        initial_quantity = self.mito.metabolites["nadh"].quantity
        self.mito.change_metabolite_quantity("nadh", 10)
        self.assertEqual(self.mito.metabolites["nadh"].quantity, initial_quantity + 10)

    def test_change_metabolite_quantity_decrease(self):
        self.mito.metabolites["nadh"].quantity = 20
        self.mito.change_metabolite_quantity("nadh", -10)
        self.assertEqual(self.mito.metabolites["nadh"].quantity, 10)

    def test_change_metabolite_quantity_not_negative(self):
        self.mito.metabolites["nadh"].quantity = 5
        self.mito.change_metabolite_quantity("nadh", -10)
        self.assertEqual(self.mito.metabolites["nadh"].quantity, 0)

    def test_consume_metabolites_success(self):
        self.mito.metabolites["nadh"].quantity = 100
        result = self.mito.consume_metabolites(nadh=50)
        self.assertTrue(result)
        self.assertEqual(self.mito.metabolites["nadh"].quantity, 50)

    def test_consume_metabolites_insufficient(self):
        self.mito.metabolites["nadh"].quantity = 30
        result = self.mito.consume_metabolites(nadh=50)
        self.assertFalse(result)
        self.assertEqual(
            self.mito.metabolites["nadh"].quantity, 30
        )  # Quantity should remain unchanged

    def test_produce_metabolites(self):
        self.mito.metabolites["nadh"].quantity = 50
        self.mito.produce_metabolites(nadh=25)
        self.assertEqual(self.mito.metabolites["nadh"].quantity, 75)

    def test_calculate_oxygen_needed(self):
        oxygen_needed = self.mito.calculate_oxygen_needed(pyruvate_amount=2)
        self.assertEqual(oxygen_needed, 5.0)

    def test_calculate_proton_leak(self):
        self.mito.proton_gradient = 500  # Set to midpoint
        leak = self.mito.calculate_proton_leak()
        expected_leak = self.mito.leak_rate / (
            1 + math.exp(-self.mito.leak_steepness * (500 - self.mito.leak_midpoint))
        )
        self.assertAlmostEqual(leak, expected_leak, places=5)

    def test_update_proton_gradient(self):
        self.mito.proton_gradient = 500
        self.mito.calculate_proton_leak = MagicMock(return_value=50)
        self.mito.update_proton_gradient(100)
        self.assertEqual(self.mito.proton_gradient, 550)
        self.mito.calculate_proton_leak.assert_called_once()

    def test_is_metabolite_available_true(self):
        self.mito.metabolites["nadh"].quantity = 100
        result = self.mito.is_metabolite_available("nadh", 50)
        self.assertTrue(result)

    def test_is_metabolite_available_false(self):
        self.mito.metabolites["nadh"].quantity = 30
        result = self.mito.is_metabolite_available("nadh", 50)
        self.assertFalse(result)

    def test_is_metabolite_available_unknown(self):
        with self.assertLogs(logger, level="WARNING") as log:
            result = self.mito.is_metabolite_available("unknown_metabolite", 10)
            self.assertFalse(result)
            self.assertIn("Unknown metabolite", log.output[0])

    def test_buffer_calcium(self):
        self.mito.metabolites["calcium"].quantity = 400
        cytoplasmic_calcium = 200
        buffered = self.mito.buffer_calcium(cytoplasmic_calcium)
        self.assertEqual(buffered, 200)
        self.assertEqual(self.mito.metabolites["calcium"].quantity, 600)

    def test_buffer_calcium_over_threshold(self):
        self.mito.metabolites["calcium"].quantity = 600
        cytoplasmic_calcium = 500
        with self.assertLogs(logger, level="WARNING") as log:
            buffered = self.mito.buffer_calcium(cytoplasmic_calcium)
            self.assertEqual(buffered, 400)
            self.assertEqual(self.mito.metabolites["calcium"].quantity, 1000)
            self.assertIn("Calcium overload detected", log.output[0])

    def test_release_calcium(self):
        self.mito.metabolites["calcium"].quantity = 500
        released = self.mito.release_calcium(200)
        self.assertEqual(released, 200)
        self.assertEqual(self.mito.metabolites["calcium"].quantity, 300)

    def test_release_calcium_more_than_available(self):
        self.mito.metabolites["calcium"].quantity = 100
        released = self.mito.release_calcium(200)
        self.assertEqual(released, 100)
        self.assertEqual(self.mito.metabolites["calcium"].quantity, 0)

    def test_reset(self):
        self.mito.metabolites["nadh"].quantity = 100
        self.mito.proton_gradient = 500
        self.mito.reset()
        self.assertEqual(self.mito.metabolites["nadh"].quantity, 0)
        self.assertEqual(self.mito.proton_gradient, 0)

    def test_transfer_cytoplasmic_nadh(self):
        cytoplasmic_nadh = 100
        mitochondrial_nadh = self.mito.transfer_cytoplasmic_nadh(cytoplasmic_nadh)
        expected_mitochondrial_nadh = int(cytoplasmic_nadh * SHUTTLE_EFFICIENCY)
        self.assertEqual(mitochondrial_nadh, expected_mitochondrial_nadh)
        self.assertEqual(
            self.mito.metabolites["nadh"].quantity, expected_mitochondrial_nadh
        )

    def test_atp_synthase(self):
        self.mito.proton_gradient = 100
        self.mito.metabolites["adp"].quantity = 50
        atp_produced = self.mito.atp_synthase()
        protons_required_per_atp = PROTONS_PER_ATP
        possible_atp = int(self.mito.proton_gradient / protons_required_per_atp)
        expected_atp_produced = min(possible_atp, 50)
        self.assertEqual(atp_produced, expected_atp_produced)
        self.assertEqual(self.mito.metabolites["atp"].quantity, expected_atp_produced)
        self.assertEqual(
            self.mito.metabolites["adp"].quantity, 50 - expected_atp_produced
        )
        self.assertEqual(
            self.mito.proton_gradient, 100 - atp_produced * protons_required_per_atp
        )

    def test_atp_synthase_insufficient_adp(self):
        self.mito.proton_gradient = 100
        self.mito.metabolites["adp"].quantity = 0
        atp_produced = self.mito.atp_synthase()
        self.assertEqual(atp_produced, 0)
        self.assertEqual(self.mito.metabolites["atp"].quantity, 0)
        self.assertEqual(self.mito.proton_gradient, 100)

    def test_complex_I_success(self):
        self.mito.metabolites["nadh"].quantity = 100
        self.mito.metabolites["ubiquinone"].quantity = 50
        self.mito.proton_gradient = 0
        reaction_rate = self.mito.complex_I()
        expected_rate = min(100, 50)
        self.assertEqual(reaction_rate, expected_rate)
        self.assertEqual(self.mito.metabolites["nadh"].quantity, 100 - expected_rate)
        self.assertEqual(
            self.mito.metabolites["ubiquinone"].quantity, 50 - expected_rate
        )
        self.assertEqual(self.mito.metabolites["ubiquinol"].quantity, expected_rate)
        self.assertEqual(self.mito.proton_gradient, PROTONS_PER_NADH * expected_rate)

    def test_complex_I_insufficient_metabolites(self):
        self.mito.metabolites["nadh"].quantity = 0
        self.mito.metabolites["ubiquinone"].quantity = 50
        with self.assertLogs(logger, level="WARNING") as log:
            reaction_rate = self.mito.complex_I()
            self.assertEqual(reaction_rate, 0)
            self.assertIn(
                "Insufficient NADH or ubiquinone for Complex I", log.output[0]
            )

    def test_complex_II_success(self):
        self.mito.metabolites["fadh2"].quantity = 60
        self.mito.metabolites["ubiquinone"].quantity = 50
        reaction_rate = self.mito.complex_II()
        expected_rate = min(60, 50)
        self.assertEqual(reaction_rate, expected_rate)
        self.assertEqual(self.mito.metabolites["fadh2"].quantity, 60 - expected_rate)
        self.assertEqual(
            self.mito.metabolites["ubiquinone"].quantity, 50 - expected_rate
        )
        self.assertEqual(self.mito.metabolites["ubiquinol"].quantity, expected_rate)

    def test_complex_II_insufficient_metabolites(self):
        self.mito.metabolites["fadh2"].quantity = 0
        self.mito.metabolites["ubiquinone"].quantity = 50
        with self.assertLogs(logger, level="WARNING") as log:
            reaction_rate = self.mito.complex_II()
            self.assertEqual(reaction_rate, 0)
            self.assertIn(
                "Insufficient FADH2 or ubiquinone for Complex II", log.output[0]
            )

    def test_complex_III_success(self):
        self.mito.metabolites["ubiquinol"].quantity = 40
        self.mito.metabolites["cytochrome_c_oxidized"].quantity = 30
        self.mito.proton_gradient = 0
        reaction_rate = self.mito.complex_III()
        expected_rate = min(40, 30)
        self.assertEqual(reaction_rate, expected_rate)
        self.assertEqual(
            self.mito.metabolites["ubiquinol"].quantity, 40 - expected_rate
        )
        self.assertEqual(
            self.mito.metabolites["cytochrome_c_oxidized"].quantity, 30 - expected_rate
        )
        self.assertEqual(
            self.mito.metabolites["ubiquinone"].quantity, 100 + expected_rate
        )  # Initial quantity was 100
        self.assertEqual(
            self.mito.metabolites["cytochrome_c_reduced"].quantity, expected_rate
        )
        self.assertEqual(self.mito.proton_gradient, PROTONS_PER_FADH2 * expected_rate)

    def test_complex_III_insufficient_metabolites(self):
        self.mito.metabolites["ubiquinol"].quantity = 0
        self.mito.metabolites["cytochrome_c_oxidized"].quantity = 30
        with self.assertLogs(logger, level="WARNING") as log:
            reaction_rate = self.mito.complex_III()
            self.assertEqual(reaction_rate, 0)
            self.assertIn(
                "Insufficient ubiquinol or cytochrome c for Complex III", log.output[0]
            )

    def test_complex_IV_success(self):
        self.mito.metabolites["cytochrome_c_reduced"].quantity = 20
        self.mito.metabolites["oxygen"].quantity = 10
        self.mito.proton_gradient = 0
        reaction_rate = self.mito.complex_IV()
        expected_rate = min(20, 10 * 2)
        oxygen_consumed = expected_rate / 2
        self.assertEqual(reaction_rate, expected_rate)
        self.assertEqual(
            self.mito.metabolites["cytochrome_c_reduced"].quantity, 20 - expected_rate
        )
        self.assertEqual(self.mito.metabolites["oxygen"].quantity, 10 - oxygen_consumed)
        self.assertEqual(
            self.mito.metabolites["cytochrome_c_oxidized"].quantity, 100 + expected_rate
        )  # Initial was 100
        self.assertEqual(self.mito.proton_gradient, PROTONS_PER_FADH2 * expected_rate)

    def test_complex_IV_insufficient_metabolites(self):
        self.mito.metabolites["cytochrome_c_reduced"].quantity = 0
        self.mito.metabolites["oxygen"].quantity = 10
        with self.assertLogs(logger, level="WARNING") as log:
            reaction_rate = self.mito.complex_IV()
            self.assertEqual(reaction_rate, 0)
            self.assertIn(
                "Insufficient reduced cytochrome c for Complex IV", log.output[0]
            )

    def test_replenish_ubiquinone(self):
        self.mito.metabolites["ubiquinol"].quantity = 50
        self.mito.metabolites["ubiquinone"].quantity = 950
        self.mito.replenish_ubiquinone()
        self.assertEqual(self.mito.metabolites["ubiquinol"].quantity, 0)
        self.assertEqual(self.mito.metabolites["ubiquinone"].quantity, 1000)

    def test_replenish_cytochrome_c(self):
        self.mito.metabolites["cytochrome_c_reduced"].quantity = 50
        self.mito.metabolites["cytochrome_c_oxidized"].quantity = 950
        self.mito.replenish_cytochrome_c()
        self.assertEqual(self.mito.metabolites["cytochrome_c_reduced"].quantity, 0)
        self.assertEqual(self.mito.metabolites["cytochrome_c_oxidized"].quantity, 1000)


if __name__ == "__main__":
    unittest.main()

