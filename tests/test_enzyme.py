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


if __name__ == "__main__":
    unittest.main()
