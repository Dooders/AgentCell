import unittest

from pyology.enzymes import Enzyme
from pyology.metabolite import Metabolite


class TestEnzymeActivation(unittest.TestCase):
    def test_default_activation_state(self):
        enzyme = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0})
        self.assertTrue(enzyme.active)

    def test_activate_method(self):
        enzyme = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0}, active=False)
        enzyme.activate()
        self.assertTrue(enzyme.active)

    def test_deactivate_method(self):
        enzyme = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0})
        enzyme.deactivate()
        self.assertFalse(enzyme.active)

    def test_inactive_enzyme_calculate_rate(self):
        enzyme = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0}, active=False)
        rate = enzyme.calculate_rate(
            {"A": Metabolite(name="A", quantity=50.0, max_quantity=100.0)}
        )
        self.assertEqual(rate, 0.0)


class TestEnzymeRegulation(unittest.TestCase):
    def test_regulate_enzyme_activate(self):
        enzyme1 = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0})
        enzyme2 = Enzyme(name="Enzyme2", k_cat=1.0, k_m={"B": 10.0}, active=False)
        enzyme1.regulate_enzyme(enzyme2, "activate")
        self.assertTrue(enzyme2.active)

    def test_regulate_enzyme_deactivate(self):
        enzyme1 = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0})
        enzyme2 = Enzyme(name="Enzyme2", k_cat=1.0, k_m={"B": 10.0})
        enzyme1.regulate_enzyme(enzyme2, "deactivate")
        self.assertFalse(enzyme2.active)

    def test_regulate_enzyme_invalid_action(self):
        enzyme1 = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0})
        enzyme2 = Enzyme(name="Enzyme2", k_cat=1.0, k_m={"B": 10.0})
        with self.assertRaises(ValueError):
            enzyme1.regulate_enzyme(enzyme2, "invalid_action")


class TestEnzymeCascades(unittest.TestCase):
    def test_downstream_enzyme_activation(self):
        enzyme1 = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0})
        enzyme2 = Enzyme(name="Enzyme2", k_cat=1.0, k_m={"B": 10.0}, active=False)
        enzyme1.downstream_enzymes.append(enzyme2)

        # Activate enzyme1 and ensure it activates enzyme2
        enzyme1.activate()
        self.assertTrue(enzyme2.active)

    def test_downstream_enzyme_no_deactivation(self):
        enzyme1 = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0})
        enzyme2 = Enzyme(name="Enzyme2", k_cat=1.0, k_m={"B": 10.0}, active=True)
        enzyme1.downstream_enzymes.append(enzyme2)

        # Deactivate enzyme1 and ensure it does not deactivate enzyme2
        enzyme1.deactivate()
        self.assertTrue(enzyme2.active)


class TestEnzymeKinetics(unittest.TestCase):
    def test_calculate_rate_basic(self):
        enzyme = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"A": 10.0})
        metabolites = {"A": Metabolite(name="A", quantity=50.0, max_quantity=100.0)}
        rate = enzyme.calculate_rate(metabolites)
        self.assertAlmostEqual(rate, 0.8333333, places=6)

    def test_calculate_rate_with_inhibitor(self):
        enzyme = Enzyme(
            name="Enzyme1",
            k_cat=1.0,
            k_m={"A": 10.0},
            inhibitors={"I": {"type": "competitive", "ki": 5.0}},
        )
        metabolites = {
            "A": Metabolite(name="A", quantity=50.0, max_quantity=100.0),
            "I": Metabolite(name="I", quantity=2.5, max_quantity=10.0),
        }
        rate = enzyme.calculate_rate(metabolites)
        self.assertLess(rate, 0.8333333)  # Rate should be lower due to inhibition

    def test_calculate_rate_with_activator(self):
        enzyme = Enzyme(
            name="Enzyme1", k_cat=1.0, k_m={"A": 10.0}, activators={"C": 1.0}
        )
        metabolites = {
            "A": Metabolite(name="A", quantity=50.0, max_quantity=100.0),
            "C": Metabolite(name="C", quantity=1.0, max_quantity=10.0),
        }
        rate = enzyme.calculate_rate(metabolites)
        self.assertGreater(rate, 0.8333333)  # Rate should be higher due to activation

    def test_calculate_rate_with_hill_coefficient(self):
        enzyme = Enzyme(
            name="Enzyme1", k_cat=1.0, k_m={"A": 10.0}, hill_coefficients={"A": 2.0}
        )
        metabolites = {"A": Metabolite(name="A", quantity=50.0, max_quantity=100.0)}
        rate = enzyme.calculate_rate(metabolites)
        self.assertNotAlmostEqual(
            rate, 0.8333333, places=6
        )  # Rate should be different due to Hill coefficient


class TestEnzymeCatalysis(unittest.TestCase):
    def test_catalyze_basic(self):
        enzyme = Enzyme(name="Enzyme1", k_cat=1.0, k_m={"substrate1": 10.0})
        metabolites = {
            "substrate1": Metabolite(
                name="substrate1", quantity=50.0, max_quantity=100.0
            ),
            "product1": Metabolite(name="product1", quantity=0.0, max_quantity=100.0),
        }
        enzyme.catalyze(metabolites, dt=1.0)
        self.assertLess(metabolites["substrate1"].quantity, 50.0)
        self.assertGreater(metabolites["product1"].quantity, 0.0)

    def test_catalyze_multiple_substrates_products(self):
        enzyme = Enzyme(
            name="Enzyme1", k_cat=1.0, k_m={"substrate1": 10.0, "substrate2": 20.0}
        )
        metabolites = {
            "substrate1": Metabolite(
                name="substrate1", quantity=50.0, max_quantity=100.0
            ),
            "substrate2": Metabolite(
                name="substrate2", quantity=60.0, max_quantity=100.0
            ),
            "product1": Metabolite(name="product1", quantity=0.0, max_quantity=100.0),
            "product2": Metabolite(name="product2", quantity=0.0, max_quantity=100.0),
        }
        enzyme.catalyze(metabolites, dt=1.0)
        self.assertLess(metabolites["substrate1"].quantity, 50.0)
        self.assertLess(metabolites["substrate2"].quantity, 60.0)
        self.assertGreater(metabolites["product1"].quantity, 0.0)
        self.assertGreater(metabolites["product2"].quantity, 0.0)


if __name__ == "__main__":
    unittest.main()
