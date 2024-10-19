import unittest
from unittest.mock import Mock, patch

from pyology.cell import Cell
from pyology.simulation import Reporter, SimulationController


class TestSimulationController(unittest.TestCase):

    def setUp(self):
        self.cell = Cell()
        self.reporter = Mock(spec=Reporter)
        self.sim_controller = SimulationController(self.cell, self.reporter)

        # Set initial ATP levels
        self.cell.cytoplasm.metabolites["ATP"].quantity = 10.0
        self.cell.mitochondrion.metabolites["ATP"].quantity = 0.0

    def test_initial_atp_levels(self):
        # Test that initial ATP levels are correctly set
        expected_initial_atp = 10.0
        self.assertEqual(self.sim_controller.initial_atp, expected_initial_atp)

    def test_initial_adenine_nucleotide_balance(self, debug: bool = False):
        # Test that initial adenine nucleotide balance is correct
        initial_atp = int(self.cell.cytoplasm.metabolites["ATP"].quantity)
        initial_adp = int(self.cell.cytoplasm.metabolites["ADP"].quantity)
        initial_amp = int(self.cell.cytoplasm.metabolites["AMP"].quantity)
        expected_total = initial_atp + initial_adp + initial_amp

        if debug:
            # Print values for debugging
            print(f"Initial ATP: {initial_atp}")
            print(f"Initial ADP: {initial_adp}")
            print(f"Initial AMP: {initial_amp}")
            print(f"Expected total: {expected_total}")
            print(f"SimController Initial ATP: {self.sim_controller.initial_atp}")
            print(f"SimController Initial ADP: {self.sim_controller.initial_adp}")
            print(f"SimController Initial AMP: {self.sim_controller.initial_amp}")
            print(
                f"SimController Initial Total: {self.sim_controller.initial_adenine_nucleotides}"
            )

        # Check initial values before running simulation
        self.assertEqual(self.sim_controller.initial_atp, initial_atp)
        self.assertEqual(self.sim_controller.initial_adp, initial_adp)
        self.assertEqual(self.sim_controller.initial_amp, initial_amp)
        self.assertEqual(
            self.sim_controller.initial_adenine_nucleotides, expected_total
        )

        self.sim_controller.run_simulation(1)  # Run with 1 glucose unit

        # Check that initial values haven't changed after simulation
        self.assertEqual(self.sim_controller.initial_atp, initial_atp)
        self.assertEqual(self.sim_controller.initial_adp, initial_adp)
        self.assertEqual(self.sim_controller.initial_amp, initial_amp)
        self.assertEqual(
            self.sim_controller.initial_adenine_nucleotides, expected_total
        )

        if debug:
            print(f"After simulation:")
            print(f"SimController Initial ATP: {self.sim_controller.initial_atp}")
            print(f"SimController Initial ADP: {self.sim_controller.initial_adp}")
            print(f"SimController Initial AMP: {self.sim_controller.initial_amp}")
            print(
                f"SimController Initial Total: {self.sim_controller.initial_adenine_nucleotides}"
            )

    @patch("pyology.glycolysis.Glycolysis.perform")
    def test_run_simulation_basic(self, mock_glycolysis, debug: bool = False):
        # Mock glycolysis to return a tuple of (net_atp_produced, pyruvate_produced)
        mock_glycolysis.return_value = (2, 2)  # 2 ATP and 2 pyruvate produced

        if debug:
            print(f"Initial ATP: {self.cell.cytoplasm.metabolites['ATP'].quantity}")
            print(f"Initial glucose: {self.cell.metabolites['glucose'].quantity}")

        # Run simulation with 1 glucose unit
        results = self.sim_controller.run_simulation(1)

        # Check if glycolysis was called
        mock_glycolysis.assert_called_once()

        if debug:
            print(f"Simulation results: {results}")
            print(f"Final ATP: {self.cell.cytoplasm.metabolites['ATP'].quantity}")
            print(f"Final glucose: {self.cell.metabolites['glucose'].quantity}")

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
            if debug:
                print(f"{key}: {results[key]}")

        if debug:
            print(f"Mock glycolysis called with args: {mock_glycolysis.call_args}")

    def test_atp_production(self):
        """
        Test that ATP is produced during simulation
        """
        pass

    def test_glucose_consumption(self, debug: bool = False):
        """
        Test that glucose is consumed during simulation
        """
        if debug:
            print(f"Initial glucose: {self.cell.metabolites['glucose'].quantity}")

        initial_glucose = self.cell.metabolites["glucose"].quantity

        self.sim_controller.run_simulation(1)  # Run with 1 glucose unit

        final_glucose = self.cell.metabolites["glucose"].quantity

        if debug:
            print(f"Final glucose: {final_glucose}")

        self.assertLess(final_glucose, initial_glucose)


if __name__ == "__main__":
    unittest.main()
