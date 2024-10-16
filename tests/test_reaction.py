import unittest

from pyology.enzymes import Enzyme
from pyology.exceptions import UnknownMetaboliteError
from pyology.organelle import Organelle
from pyology.reaction import Reaction


class MockEnzyme(Enzyme):
    def __init__(self, name, vmax, km):
        super().__init__(name, vmax, km)

    def calculate_rate(self, substrate_conc, metabolites):
        return 1.0  # Simplified rate calculation for testing


class TestReaction(unittest.TestCase):
    def setUp(self):
        self.enzyme = MockEnzyme("Test Enzyme", vmax=10.0, km=1.0)
        self.organelle = Organelle()

    def test_simple_reaction(self):
        # Set up a simple reaction: A -> B
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Add metabolites to the organelle
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Check results
        self.assertAlmostEqual(actual_rate, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 9.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 1.0)

    def test_multi_step_reaction(self):
        # Set up a multi-step reaction: 2A + B -> C + D
        reaction = Reaction(
            name="2A + B to C + D",
            enzyme=self.enzyme,
            consume={"A": 2.0, "B": 1.0},
            produce={"C": 1.0, "D": 1.0},
        )

        # Add metabolites to the organelle
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="substrate", quantity=5.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "C", type="product", quantity=0.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "D", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Check results
        self.assertAlmostEqual(actual_rate, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 8.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 4.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("C"), 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("D"), 1.0)

    def test_limiting_factor(self):
        # Set up a reaction: 2A -> B
        reaction = Reaction(
            name="2A to B", enzyme=self.enzyme, consume={"A": 2.0}, produce={"B": 1.0}
        )

        # Add metabolites to the organelle
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=1.5, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Check results
        self.assertAlmostEqual(actual_rate, 0.75)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.75)


if __name__ == "__main__":
    unittest.main()
