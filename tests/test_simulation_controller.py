import unittest
from unittest.mock import Mock, patch

from pyology.cell import Cell
from pyology.simulation import Reporter, SimulationController


class TestSimulationController(unittest.TestCase):

    def setUp(self):
        self.cell = Cell()
        self.reporter = Mock(spec=Reporter)
        self.sim_controller = SimulationController(self.cell, self.reporter)

    def test_initial_atp_levels(self):
        # Test that initial ATP levels are correctly set
        expected_initial_atp = 20.0  # Assuming this is the correct initial value
        self.assertEqual(self.sim_controller.initial_atp, expected_initial_atp)

    def test_initial_adenine_nucleotide_balance(self):
        # Test that initial adenine nucleotide balance is correct
        initial_atp = self.cell.cytoplasm.metabolites["ATP"].quantity
        initial_adp = self.cell.metabolites["ADP"].quantity
        initial_amp = self.cell.metabolites["AMP"].quantity
        expected_total = initial_atp + initial_adp + initial_amp

        self.sim_controller.run_simulation(1)  # Run with 1 glucose unit

        self.assertEqual(
            self.sim_controller.initial_adenine_nucleotides, expected_total
        )

    @patch("pyology.glycolysis.Glycolysis.perform")
    def test_run_simulation_basic(self, mock_glycolysis):
        # Mock glycolysis to return a known value
        mock_glycolysis.return_value = 2  # 2 pyruvate produced

        # Run simulation with 1 glucose unit
        results = self.sim_controller.run_simulation(1)

        # Check if glycolysis was called
        mock_glycolysis.assert_called_once()

        # Check if results contain expected keys
        expected_keys = [
            "total_atp_produced",
            "glucose_processed",
            "glucose_consumed",
            "pyruvate_produced",
            "simulation_time",
            "oxygen_remaining",
            "final_cytoplasm_atp",
            "final_mitochondrion_atp",
            "final_phosphoglycerate_2",
            "final_phosphoenolpyruvate",
        ]
        for key in expected_keys:
            self.assertIn(key, results)

    def test_atp_production(self):
        # Test that ATP is produced during simulation
        initial_atp = (
            self.cell.cytoplasm.metabolites["ATP"].quantity
            + self.cell.mitochondrion.metabolites["ATP"].quantity
        )

        self.sim_controller.run_simulation(1)  # Run with 1 glucose unit

        final_atp = (
            self.cell.cytoplasm.metabolites["ATP"].quantity
            + self.cell.mitochondrion.metabolites["ATP"].quantity
        )

        self.assertGreater(final_atp, initial_atp)

    def test_glucose_consumption(self):
        # Test that glucose is consumed during simulation
        initial_glucose = self.cell.metabolites["glucose"].quantity

        self.sim_controller.run_simulation(1)  # Run with 1 glucose unit

        final_glucose = self.cell.metabolites["glucose"].quantity

        self.assertLess(final_glucose, initial_glucose)


if __name__ == "__main__":
    unittest.main()
