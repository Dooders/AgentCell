import unittest

from pyology.cytoplasm import Cytoplasm
from pyology.exceptions import GlycolysisError


class TestCytoplasm(unittest.TestCase):
    def setUp(self):
        self.cytoplasm = Cytoplasm()

    def test_initial_metabolite_quantities(self):
        """Test that initial metabolite quantities are set correctly."""
        self.assertEqual(self.cytoplasm.metabolites["glucose"].quantity, 100)
        self.assertEqual(self.cytoplasm.metabolites["atp"].quantity, 100)
        self.assertEqual(self.cytoplasm.metabolites["adp"].quantity, 100)
        self.assertEqual(self.cytoplasm.metabolites["nad"].quantity, 100)
        self.assertEqual(self.cytoplasm.metabolites["nadh"].quantity, 0)
        self.assertEqual(self.cytoplasm.metabolites["pyruvate"].quantity, 0)
        self.assertEqual(self.cytoplasm.glycolysis_rate, 1.0)

    def test_glycolysis_with_positive_glucose_units(self):
        """Test glycolysis with a positive number of glucose units."""
        initial_pyruvate = self.cytoplasm.get_metabolite_quantity("pyruvate")
        initial_glucose = self.cytoplasm.get_metabolite_quantity("glucose")
        pyruvate_produced = self.cytoplasm.glycolysis(2)
        final_pyruvate = self.cytoplasm.get_metabolite_quantity("pyruvate")
        final_glucose = self.cytoplasm.get_metabolite_quantity("glucose")
        self.assertEqual(pyruvate_produced, final_pyruvate)
        self.assertEqual(
            final_pyruvate, initial_pyruvate + 4
        )  # 2 glucose units produce 4 pyruvate
        self.assertEqual(final_glucose, initial_glucose - 2)

    def test_glycolysis_with_zero_glucose_units(self):
        """Test glycolysis with zero glucose units."""
        initial_pyruvate = self.cytoplasm.get_metabolite_quantity("pyruvate")
        pyruvate_produced = self.cytoplasm.glycolysis(0)
        final_pyruvate = self.cytoplasm.get_metabolite_quantity("pyruvate")
        self.assertEqual(pyruvate_produced, 0)
        self.assertEqual(final_pyruvate, initial_pyruvate)

    def test_glycolysis_with_negative_glucose_units(self):
        """Test glycolysis with negative glucose units."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.glycolysis(-1)
        self.assertIn("cannot be negative", str(context.exception))

    def test_glycolysis_with_insufficient_glucose(self):
        """Test glycolysis when there is insufficient glucose."""
        self.cytoplasm.metabolites["glucose"].quantity = 0
        with self.assertRaises(GlycolysisError) as context:
            self.cytoplasm.glycolysis(1)
        self.assertIn("Glycolysis failed", str(context.exception))

    def test_ensure_metabolite_availability_sufficient(self):
        """Test ensure_metabolite_availability when metabolite is sufficient."""
        try:
            self.cytoplasm.ensure_metabolite_availability("atp", 50)
        except Exception as e:
            self.fail(
                f"ensure_metabolite_availability raised an exception unexpectedly: {e}"
            )

    def test_ensure_metabolite_availability_insufficient(self):
        """Test ensure_metabolite_availability when metabolite is insufficient."""
        self.cytoplasm.metabolites["atp"].quantity = 0
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.ensure_metabolite_availability("atp", 1)
        self.assertIn("Insufficient atp", str(context.exception))

    def test_consume_metabolites_success(self):
        """Test consuming metabolites successfully."""
        result = self.cytoplasm.consume_metabolites(glucose=10, atp=5)
        self.assertTrue(result)
        self.assertEqual(self.cytoplasm.metabolites["glucose"].quantity, 90)
        self.assertEqual(self.cytoplasm.metabolites["atp"].quantity, 95)

    def test_consume_metabolites_insufficient(self):
        """Test consuming metabolites when insufficient quantity is available."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.consume_metabolites(glucose=1000)
        self.assertIn("Insufficient glucose", str(context.exception))

    def test_produce_metabolites_success(self):
        """Test producing metabolites successfully."""
        result = self.cytoplasm.produce_metabolites(nadh=10)
        self.assertTrue(result)
        self.assertEqual(self.cytoplasm.metabolites["nadh"].quantity, 10)

    def test_produce_metabolites_exceeding_max(self):
        """Test producing metabolites exceeding maximum capacity."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.produce_metabolites(nadh=2000)
        self.assertIn("Cannot exceed max quantity for nadh", str(context.exception))

    def test_step1_hexokinase_success(self):
        """Test hexokinase step under normal conditions."""
        initial_glucose = self.cytoplasm.metabolites["glucose"].quantity
        initial_atp = self.cytoplasm.metabolites["atp"].quantity
        initial_adp = self.cytoplasm.metabolites["adp"].quantity

        self.cytoplasm.step1_hexokinase()

        self.assertEqual(
            self.cytoplasm.metabolites["glucose"].quantity, initial_glucose - 1
        )
        self.assertEqual(self.cytoplasm.metabolites["atp"].quantity, initial_atp - 1)
        self.assertEqual(self.cytoplasm.metabolites["adp"].quantity, initial_adp + 1)

    def test_step1_hexokinase_insufficient_atp(self):
        """Test hexokinase step when ATP is insufficient."""
        self.cytoplasm.metabolites["atp"].quantity = 0
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.step1_hexokinase()
        self.assertIn("Insufficient atp", str(context.exception))

    def test_reset(self):
        """Test reset method."""
        # Modify metabolite quantities
        self.cytoplasm.metabolites["glucose"].quantity = 50
        self.cytoplasm.metabolites["atp"].quantity = 50

        self.cytoplasm.reset()

        self.assertEqual(self.cytoplasm.metabolites["glucose"].quantity, 100)
        self.assertEqual(self.cytoplasm.metabolites["atp"].quantity, 100)
        self.assertEqual(self.cytoplasm.glycolysis_rate, 1.0)

    def test_get_metabolite_quantity_valid(self):
        """Test getting a valid metabolite quantity."""
        quantity = self.cytoplasm.get_metabolite_quantity("glucose")
        self.assertEqual(quantity, 100)

    def test_get_metabolite_quantity_invalid(self):
        """Test getting a quantity for an invalid metabolite."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.get_metabolite_quantity("invalid_metabolite")
        self.assertIn("Unknown metabolite", str(context.exception))

    def test_is_metabolite_available_true(self):
        """Test is_metabolite_available returns True when sufficient."""
        self.assertTrue(self.cytoplasm.is_metabolite_available("atp", 50))

    def test_is_metabolite_available_false(self):
        """Test is_metabolite_available returns False when insufficient."""
        self.assertFalse(self.cytoplasm.is_metabolite_available("atp", 1000))

    def test_is_metabolite_available_unknown(self):
        """Test is_metabolite_available with an unknown metabolite."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.is_metabolite_available("unknown_metabolite", 10)
        self.assertIn("Unknown metabolite", str(context.exception))

    def test_consume_metabolites_invalid_metabolite(self):
        """Test consuming an invalid metabolite."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.consume_metabolites(unknown_metabolite=10)
        self.assertIn("Unknown metabolite", str(context.exception))

    def test_consume_metabolites_negative_amount(self):
        """Test consuming a negative amount of a metabolite."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.consume_metabolites(glucose=-10)
        self.assertIn("Cannot consume a negative amount", str(context.exception))

    def test_produce_metabolites_invalid_metabolite(self):
        """Test producing an invalid metabolite."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.produce_metabolites(unknown_metabolite=10)
        self.assertIn("Unknown metabolite", str(context.exception))

    def test_produce_metabolites_negative_amount(self):
        """Test producing a negative amount of a metabolite."""
        with self.assertRaises(ValueError) as context:
            self.cytoplasm.produce_metabolites(nadh=-10)
        self.assertIn("Cannot produce a negative amount", str(context.exception))

    def test_full_glycolysis_pathway(self):
        """Test the full glycolysis pathway execution."""
        initial_glucose = self.cytoplasm.get_metabolite_quantity("glucose")
        initial_pyruvate = self.cytoplasm.get_metabolite_quantity("pyruvate")
        initial_atp = self.cytoplasm.get_metabolite_quantity("atp")
        initial_adp = self.cytoplasm.get_metabolite_quantity("adp")
        initial_nad = self.cytoplasm.get_metabolite_quantity("nad")
        initial_nadh = self.cytoplasm.get_metabolite_quantity("nadh")

        pyruvate_produced = self.cytoplasm.glycolysis(1)
        final_glucose = self.cytoplasm.get_metabolite_quantity("glucose")
        final_pyruvate = self.cytoplasm.get_metabolite_quantity("pyruvate")
        final_atp = self.cytoplasm.get_metabolite_quantity("atp")
        final_adp = self.cytoplasm.get_metabolite_quantity("adp")
        final_nad = self.cytoplasm.get_metabolite_quantity("nad")
        final_nadh = self.cytoplasm.get_metabolite_quantity("nadh")

        # Check metabolite changes according to glycolysis stoichiometry
        self.assertEqual(final_glucose, initial_glucose - 1)
        self.assertEqual(final_pyruvate, initial_pyruvate + 2)
        self.assertEqual(final_atp, initial_atp + 2 - 2)  # Net gain of 2 ATP
        self.assertEqual(final_adp, initial_adp - 2 + 2)  # Consumed and produced
        self.assertEqual(final_nad, initial_nad - 2)
        self.assertEqual(final_nadh, initial_nadh + 2)
        self.assertEqual(pyruvate_produced, final_pyruvate)

    def test_glycolysis_invalid_steps(self):
        """Test glycolysis when a step raises an exception."""
        # Override a step to raise an exception
        original_step = self.cytoplasm.step6_glyceraldehyde_3_phosphate_dehydrogenase

        def faulty_step():
            raise ValueError("Faulty step")

        self.cytoplasm.step6_glyceraldehyde_3_phosphate_dehydrogenase = faulty_step

        with self.assertRaises(GlycolysisError) as context:
            self.cytoplasm.glycolysis(1)
        self.assertIn("Glycolysis failed", str(context.exception))

        # Restore the original step
        self.cytoplasm.step6_glyceraldehyde_3_phosphate_dehydrogenase = original_step


if __name__ == "__main__":
    unittest.main()
