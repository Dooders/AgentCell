import unittest
from cell_modeling import Cell

class TestCell(unittest.TestCase):
    def setUp(self):
        self.cell = Cell()

    def test_metabolize_glucose(self):
        initial_energy = self.cell.energy
        glucose_amount = 10
        self.cell.metabolize_glucose(glucose_amount)
        self.assertGreater(self.cell.energy, initial_energy)

    def test_synthesize_protein(self):
        self.cell.nucleus.add_gene("test_gene", "ATCG")
        protein = self.cell.synthesize_protein("test_gene")
        self.assertIsNotNone(protein)
        self.assertTrue(protein.startswith("Sorted Processed Protein from mRNA"))

if __name__ == '__main__':
    unittest.main()