import unittest
from cell_modeling.organelles.mitochondrion import KrebsCycle, Mitochondrion

class TestKrebsCycle(unittest.TestCase):
    def setUp(self):
        self.krebs_cycle = KrebsCycle()

    def test_add_substrate(self):
        self.krebs_cycle.add_substrate("Acetyl-CoA", 10)
        self.assertEqual(self.krebs_cycle.metabolites["Acetyl-CoA"].quantity, 10)

    def test_step1_citrate_synthase(self):
        self.krebs_cycle.add_substrate("Acetyl-CoA", 5)
        self.krebs_cycle.add_substrate("Oxaloacetate", 5)
        self.krebs_cycle.step1_citrate_synthase()
        self.assertLess(self.krebs_cycle.metabolites["Acetyl-CoA"].quantity, 5)
        self.assertGreater(self.krebs_cycle.metabolites["Citrate"].quantity, 0)

    # ... other test methods ...

class TestMitochondrion(unittest.TestCase):
    def setUp(self):
        self.mitochondrion = Mitochondrion()

    def test_pyruvate_to_acetyl_coa(self):
        pyruvate_amount = 10
        acetyl_coa = self.mitochondrion.pyruvate_to_acetyl_coa(pyruvate_amount)
        self.assertEqual(acetyl_coa, pyruvate_amount)
        self.assertEqual(self.mitochondrion.metabolites["nadh"].quantity, pyruvate_amount)
        self.assertEqual(self.mitochondrion.metabolites["co2"].quantity, pyruvate_amount)

    def test_cellular_respiration(self):
        pyruvate_amount = 10
        self.mitochondrion.metabolites["oxygen"].quantity = 100  # Ensure enough oxygen
        atp_produced = self.mitochondrion.cellular_respiration(pyruvate_amount)
        self.assertGreater(atp_produced, 0)
        self.assertGreater(self.mitochondrion.krebs_cycle.metabolites["Citrate"].quantity, 0)

    # ... other test methods ...

# ... rest of the test file ...
