import unittest

from pyology.cell import Cell


class TestCell(unittest.TestCase):
    def setUp(self):
        self.cell = Cell()

    def test_initial_state(self):
        """Test the initial state of the cell."""
        self.assertEqual(self.cell.simulation_time, 0)
        self.assertEqual(self.cell.glycolysis_rate, self.cell.base_glycolysis_rate)

    def test_get_cell_state(self):
        """Test the get_cell_state method."""
        state = self.cell.get_cell_state(glucose_processed=5, total_atp_produced=100)
        self.assertIsInstance(state, dict)
        self.assertIn("simulation_time", state)
        self.assertIn("glucose_processed", state)
        self.assertIn("total_atp_produced", state)
        self.assertIn("cytoplasm_atp", state)
        self.assertIn("mitochondrion_atp", state)
        self.assertIn("cytoplasm_nadh", state)
        self.assertIn("mitochondrion_nadh", state)
        self.assertIn("mitochondrion_fadh2", state)
        self.assertIn("mitochondrial_calcium", state)
        self.assertIn("proton_gradient", state)
        self.assertIn("oxygen_remaining", state)

    def test_reset(self):
        """Test the reset method."""
        self.cell.simulation_time = 100
        self.cell.reset()
        self.assertEqual(self.cell.simulation_time, 0)


if __name__ == "__main__":
    unittest.main()
