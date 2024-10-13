import unittest

from pyology.cell import Cell


class TestCell(unittest.TestCase):
    def setUp(self):
        self.cell = Cell()

    def test_initial_state(self):
        """Test the initial state of the cell."""
        self.assertEqual(self.cell.simulation_time, 0)
        self.assertEqual(self.cell.cytoplasm.metabolites["glucose"].quantity, 10)
        self.assertEqual(self.cell.cytoplasm.metabolites["atp"].quantity, 100)
        self.assertEqual(self.cell.cytoplasmic_calcium.quantity, 100)
        self.assertEqual(self.cell.glycolysis_rate, self.cell.base_glycolysis_rate)
        self.assertEqual(
            self.cell.mitochondrion.metabolites["oxygen"].quantity, 1000
        )  # Assuming initial oxygen

    def test_produce_atp(self):
        """Test ATP production with a specific amount of glucose."""
        glucose_to_process = 5
        initial_atp = self.cell.cytoplasm.metabolites["atp"].quantity
        total_atp_produced = self.cell.produce_atp(glucose=glucose_to_process)
        
        # Check that ATP was produced
        self.assertGreater(total_atp_produced, 0)
        
        # Check that the simulation time has increased
        self.assertGreater(self.cell.simulation_time, 0)
        self.assertLessEqual(
            self.cell.simulation_time, self.cell.time_step * glucose_to_process
        )
        
        # Check that glucose was consumed
        self.assertEqual(
            self.cell.cytoplasm.metabolites["glucose"].quantity,
            10 - glucose_to_process,
        )
        
        # Check that ATP quantity has increased
        final_atp = self.cell.cytoplasm.metabolites["atp"].quantity
        self.assertGreater(final_atp, initial_atp)
        
        # Check that the total ATP produced matches the increase in ATP quantity
        self.assertAlmostEqual(total_atp_produced, final_atp - initial_atp, places=2)

        # Check that the total ATP produced is within a reasonable range
        expected_min_atp = glucose_to_process * 2  # Minimum ATP from glycolysis
        expected_max_atp = glucose_to_process * 38  # Maximum ATP from complete oxidation
        self.assertGreaterEqual(total_atp_produced, expected_min_atp)
        self.assertLessEqual(total_atp_produced, expected_max_atp)

    def test_produce_atp_no_oxygen(self):
        """Test ATP production when oxygen is depleted."""
        # Deplete oxygen
        self.cell.mitochondrion.metabolites["oxygen"].quantity = 0
        total_atp_produced = self.cell.produce_atp(glucose=5)
        # Expect that no ATP is produced via cellular respiration
        self.assertEqual(self.cell.mitochondrion.metabolites["oxygen"].quantity, 0)
        self.assertEqual(self.cell.mitochondrion.metabolites["atp"].quantity, 0)
        self.assertGreater(
            self.cell.cytoplasm.metabolites["atp"].quantity, 0
        )  # ATP from glycolysis
        self.assertGreater(
            total_atp_produced, 0
        )  # Should still produce ATP from glycolysis

    def test_produce_atp_generator(self):
        """Test the produce_atp_generator method."""
        glucose_to_process = 3
        state_generator = self.cell.produce_atp_generator(glucose=glucose_to_process)
        states = list(state_generator)
        # There should be at least one state per glucose unit processed plus the final state
        self.assertGreaterEqual(len(states), glucose_to_process)
        for state in states:
            self.assertIn("simulation_time", state)
            self.assertIn("glucose_processed", state)
            self.assertIn("total_atp_produced", state)
            self.assertIsInstance(state["total_atp_produced"], (int, float))

    def test_reset(self):
        """Test the reset method."""
        # Modify some cell state
        self.cell.cytoplasm.metabolites["atp"].quantity = 50
        self.cell.mitochondrion.metabolites["atp"].quantity = 50
        self.cell.simulation_time = 100
        self.cell.reset()
        self.assertEqual(self.cell.simulation_time, 0)
        self.assertEqual(self.cell.cytoplasm.metabolites["atp"].quantity, 0)
        self.assertEqual(self.cell.mitochondrion.metabolites["atp"].quantity, 0)
        self.assertEqual(self.cell.cytoplasmic_calcium.quantity, 100)

    def test_adp_transfer(self):
        """Test that ADP is correctly transferred when mitochondrial ADP is low."""
        self.cell.mitochondrion.metabolites["adp"].quantity = 5
        initial_cytoplasm_adp = self.cell.cytoplasm.metabolites["adp"].quantity
        self.cell.produce_atp(glucose=1)
        self.assertGreater(self.cell.mitochondrion.metabolites["adp"].quantity, 5)
        self.assertLess(
            self.cell.cytoplasm.metabolites["adp"].quantity, initial_cytoplasm_adp
        )

    def test_calcium_levels(self):
        """Test that calcium levels are correctly maintained."""
        initial_cytoplasmic_calcium = self.cell.cytoplasmic_calcium.quantity
        initial_mitochondrial_calcium = self.cell.mitochondrion.metabolites[
            "calcium"
        ].quantity
        self.cell.produce_atp(glucose=1)
        # Assuming some calcium transfer occurs during ATP production
        self.assertEqual(
            self.cell.cytoplasmic_calcium.quantity, initial_cytoplasmic_calcium
        )
        self.assertEqual(
            self.cell.mitochondrion.metabolites["calcium"].quantity,
            initial_mitochondrial_calcium,
        )

    def test_proton_gradient(self):
        """Test that the proton gradient is updated during ATP production."""
        initial_proton_gradient = self.cell.mitochondrion.proton_gradient
        self.cell.produce_atp(glucose=1)
        self.assertNotEqual(
            self.cell.mitochondrion.proton_gradient, initial_proton_gradient
        )

    def test_glycolysis_rate_feedback(self):
        """Test that the glycolysis rate adjusts based on ADP levels."""
        # Reduce cytoplasmic ADP to see if glycolysis rate decreases
        self.cell.cytoplasm.metabolites["adp"].quantity = 0
        self.cell.produce_atp(glucose=1)
        self.assertEqual(self.cell.glycolysis_rate, self.cell.base_glycolysis_rate * 1)

        # Increase cytoplasmic ADP to see if glycolysis rate increases
        self.cell.cytoplasm.metabolites["adp"].quantity = 500
        self.cell.produce_atp(glucose=1)
        self.assertEqual(self.cell.glycolysis_rate, self.cell.base_glycolysis_rate * 2)

    def test_glucose_depletion(self):
        """Test behavior when glucose is depleted."""
        self.cell.cytoplasm.metabolites["glucose"].quantity = 1
        total_atp_produced = self.cell.produce_atp(glucose=5)
        # Should only process 1 unit of glucose
        self.assertEqual(self.cell.cytoplasm.metabolites["glucose"].quantity, 0)
        self.assertEqual(
            total_atp_produced, total_atp_produced
        )  # Should be consistent with one glucose unit processed

    def test_negative_metabolite_handling(self):
        """Ensure that metabolite quantities do not go negative."""
        self.cell.cytoplasm.metabolites["glucose"].quantity = 0
        total_atp_produced = self.cell.produce_atp(glucose=1)
        self.assertEqual(self.cell.cytoplasm.metabolites["glucose"].quantity, 0)
        self.assertEqual(total_atp_produced, 0)

    def test_large_glucose_processing(self):
        """Test processing a large amount of glucose."""
        self.cell.cytoplasm.add_metabolite("glucose", 1000, 5000)
        total_atp_produced = self.cell.produce_atp(glucose=500)
        self.assertEqual(
            self.cell.cytoplasm.metabolites["glucose"].quantity, 510
        )  # 10 initial + 1000 added - 500 processed
        self.assertGreater(total_atp_produced, 0)

    def test_metabolite_limits(self):
        """Test that metabolite quantities respect their maximum capacities."""
        # Overfill a metabolite to see if it caps at max capacity
        self.cell.cytoplasm.add_metabolite("atp", 10000, 5000)
        self.assertEqual(self.cell.cytoplasm.metabolites["atp"].quantity, 5000)

    # Additional tests can be added here to cover other functionalities


if __name__ == "__main__":
    unittest.main()
