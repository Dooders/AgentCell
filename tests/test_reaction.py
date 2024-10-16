import unittest
from unittest.mock import MagicMock, patch
import logging

# Assuming the necessary classes are imported from the pyology package
from pyology.enzymes import Enzyme
from pyology.exceptions import UnknownMetaboliteError
from pyology.organelle import Organelle
from pyology.reaction import Reaction

# Configure logging to capture log outputs for testing
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pyology.reaction")


class MockEnzyme(Enzyme):
    def __init__(self, name, vmax, km, calculate_rate_return=1.0):
        super().__init__(name, vmax, km)
        self.calculate_rate_return = calculate_rate_return

    def calculate_rate(self, substrate_conc, metabolites):
        return self.calculate_rate_return


class TestReaction(unittest.TestCase):
    def setUp(self):
        # Update the Enzyme creation
        self.enzyme = Enzyme(
            name="Test Enzyme",
            k_cat=10.0,
            k_m={"A": 2.0, "B": 3.0}  # Dictionary of k_m values for substrates A and B
        )
        
        self.organelle = Organelle()

    def test_simple_reaction(self):
        """Test a simple reaction A -> B."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions
        self.assertAlmostEqual(actual_rate, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 9.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 1.0)

    def test_multi_step_reaction(self):
        """Test a multi-step reaction 2A + B -> C + D."""
        reaction = Reaction(
            name="2A + B to C + D",
            enzyme=self.enzyme,
            consume={"A": 2.0, "B": 1.0},
            produce={"C": 1.0, "D": 1.0},
        )

        # Initialize metabolites
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

        # Assertions
        self.assertAlmostEqual(actual_rate, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 8.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 4.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("C"), 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("D"), 1.0)

    def test_limiting_factor_substrate(self):
        """Test reaction where substrate availability limits the reaction rate."""
        reaction = Reaction(
            name="2A to B", enzyme=self.enzyme, consume={"A": 2.0}, produce={"B": 1.0}
        )

        # Initialize metabolites with limited A
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=1.5, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions
        self.assertAlmostEqual(actual_rate, 0.75)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.75)

    def test_limiting_factor_multiple(self):
        """Test reaction with multiple substrates where one of them limits the rate."""
        reaction = Reaction(
            name="3A + 2B to C",
            enzyme=self.enzyme,
            consume={"A": 3.0, "B": 2.0},
            produce={"C": 1.0},
        )

        # Initialize metabolites with B being limiting
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="substrate", quantity=3.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "C", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # B can support 3/2 = 1.5 rate
        self.assertAlmostEqual(actual_rate, 1.5)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 5.5)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("C"), 1.5)

    def test_zero_time_step(self):
        """Test reaction execution with zero time_step."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction with zero time_step
        actual_rate = reaction.execute(self.organelle, time_step=0.0)

        # Assertions: No change should occur
        self.assertAlmostEqual(actual_rate, 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 10.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.0)

    def test_negative_time_step(self):
        """Test reaction execution with negative time_step."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction with negative time_step
        with self.assertRaises(ValueError):
            reaction.execute(self.organelle, time_step=-1.0)

    def test_zero_consumption(self):
        """Test reaction with zero consumption of a metabolite."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 0.0}, produce={"B": 1.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions: No consumption of A, production of B based on reaction_rate
        self.assertAlmostEqual(actual_rate, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 10.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 1.0)

    def test_zero_production(self):
        """Test reaction with zero production of a metabolite."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 0.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=5.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions: Consumption of A, no change to B
        self.assertAlmostEqual(actual_rate, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 9.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 5.0)

    def test_missing_metabolite_consumption(self):
        """Test reaction where a consumed metabolite is missing from the organelle."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Only initialize metabolite B
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction and expect an error
        with self.assertRaises(UnknownMetaboliteError):
            reaction.execute(self.organelle, time_step=1.0)

    def test_missing_metabolite_production(self):
        """Test reaction where a produced metabolite is missing from the organelle."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Only initialize metabolite A
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )

        # Execute reaction and expect an error
        with self.assertRaises(UnknownMetaboliteError):
            reaction.execute(self.organelle, time_step=1.0)

    def test_enzyme_rate_zero(self):
        """Test reaction where the enzyme's calculate_rate returns zero."""
        # Create a mock enzyme that always returns zero rate
        mock_enzyme = Enzyme(
            name="Zero Rate Enzyme",
            k_cat=0.0,  # Set k_cat to 0 to ensure zero rate
            k_m={"A": 1.0}
        )

        reaction = Reaction(
            name="A to B", enzyme=mock_enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions: No change due to zero rate
        self.assertAlmostEqual(actual_rate, 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 10.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.0)

    def test_production_exceeds_max_quantity(self):
        """Test reaction where production would exceed the metabolite's max_quantity."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Initialize metabolites with B close to max
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=99.5, max_quantity=100.0
        )

        # Mock the enzyme to allow rate that would exceed max_quantity
        self.enzyme.calculate_rate_return = 1.0  # Would produce 1.0 * 1.0 = 1.0, exceeding max by 0.5

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Depending on Organelle's implementation, it might cap the production or raise an error
        # Here, we assume it caps the production rate to not exceed max_quantity
        expected_rate = 0.5  # Can only produce 0.5 before reaching max
        self.assertAlmostEqual(actual_rate, expected_rate)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 9.5)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 100.0)

    def test_multiple_reactions_sequential_execution(self):
        """Test executing multiple reactions sequentially."""
        # First reaction: A -> B
        reaction1 = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )
        # Second reaction: B -> C
        reaction2 = Reaction(
            name="B to C", enzyme=self.enzyme, consume={"B": 1.0}, produce={"C": 1.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=5.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="intermediate", quantity=0.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "C", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute first reaction
        rate1 = reaction1.execute(self.organelle, time_step=1.0)
        self.assertAlmostEqual(rate1, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 4.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("C"), 0.0)

        # Execute second reaction
        rate2 = reaction2.execute(self.organelle, time_step=1.0)
        self.assertAlmostEqual(rate2, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 4.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("C"), 1.0)

    @patch('pyology.reaction.logger')
    def test_logging_intermediate_values(self, mock_logger):
        """Test that appropriate logging occurs during reaction execution."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=5.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        reaction.execute(self.organelle, time_step=1.0)

        # Check that debug logs were called
        self.assertTrue(mock_logger.debug.called)
        self.assertTrue(mock_logger.info.called)

        # Optionally, check specific log messages
        debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]
        info_calls = [call.args[0] for call in mock_logger.info.call_args_list]

        self.assertIn("Reaction 'A to B': Initial reaction rate: 1.000000", debug_calls)
        self.assertIn("Reaction 'A to B': Potential limiting factors:", debug_calls)
        self.assertIn("- reaction_rate: 1.000000", debug_calls)
        self.assertIn("- substrate_conc: 5.000000", debug_calls)
        self.assertIn(
            "Executed reaction 'A to B' with rate 1.0000. Consumed: A: 1.0000. Produced: B: 1.0000",
            info_calls,
        )

    def test_large_time_step(self):
        """Test reaction execution with a large time_step."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 1.0}, produce={"B": 1.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=1000.0, max_quantity=10000.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=10000.0
        )

        # Execute reaction with large time_step
        actual_rate = reaction.execute(self.organelle, time_step=100.0)

        # Assertions
        self.assertAlmostEqual(actual_rate, 100.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 900.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 100.0)

    def test_fractional_reaction_rate(self):
        """Test reaction with a fractional reaction rate."""
        reaction = Reaction(
            name="A to B", enzyme=self.enzyme, consume={"A": 2.0}, produce={"B": 3.0}
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=5.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions
        # Enzyme rate is 1.0, so actual_rate = min(1.0, 5.0 / 2.0) = 1.0
        self.assertAlmostEqual(actual_rate, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 3.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 3.0)

    def test_multiple_substrates_producers(self):
        """Test reaction with multiple substrates and multiple products."""
        reaction = Reaction(
            name="2A + 3B to 4C + D",
            enzyme=self.enzyme,
            consume={"A": 2.0, "B": 3.0},
            produce={"C": 4.0, "D": 1.0},
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=10.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="substrate", quantity=9.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "C", type="product", quantity=0.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "D", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions
        # A can support 10/2 = 5.0, B can support 9/3 = 3.0, so actual_rate = 3.0
        self.assertAlmostEqual(actual_rate, 3.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 4.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("C"), 12.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("D"), 3.0)

    def test_reaction_with_non_integer_coefficients(self):
        """Test reaction with non-integer stoichiometric coefficients."""
        reaction = Reaction(
            name="1.5A to 2.5B",
            enzyme=self.enzyme,
            consume={"A": 1.5},
            produce={"B": 2.5},
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=3.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions
        self.assertAlmostEqual(actual_rate, 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 1.5)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 2.5)

    def test_reaction_with_multiple_limiting_factors(self):
        """Test reaction where multiple metabolites limit the reaction rate equally."""
        reaction = Reaction(
            name="2A + 2B to C",
            enzyme=self.enzyme,
            consume={"A": 2.0, "B": 2.0},
            produce={"C": 1.0},
        )

        # Initialize metabolites such that both A and B limit the rate equally
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=4.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="substrate", quantity=4.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "C", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions
        self.assertAlmostEqual(actual_rate, 2.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("C"), 2.0)

    def test_reaction_no_consumption_no_production(self):
        """Test reaction with no consumption and no production."""
        reaction = Reaction(
            name="Null Reaction",
            enzyme=self.enzyme,
            consume={},
            produce={},
        )

        # Initialize metabolites (no change expected)
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=5.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=5.0, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions
        self.assertAlmostEqual(actual_rate, self.enzyme.calculate_rate_return * 1.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 5.0)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 5.0)

    def test_reaction_with_negative_consumption(self):
        """Test reaction with negative consumption coefficients (should raise error)."""
        reaction = Reaction(
            name="Invalid Reaction",
            enzyme=self.enzyme,
            consume={"A": -1.0},
            produce={"B": 1.0},
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=5.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.0, max_quantity=100.0
        )

        # Execute reaction and expect an error
        with self.assertRaises(ValueError):
            reaction.execute(self.organelle, time_step=1.0)

    def test_reaction_with_negative_production(self):
        """Test reaction with negative production coefficients (should raise error)."""
        reaction = Reaction(
            name="Invalid Reaction",
            enzyme=self.enzyme,
            consume={"A": 1.0},
            produce={"B": -1.0},
        )

        # Initialize metabolites
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=5.0, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=5.0, max_quantity=100.0
        )

        # Execute reaction and expect an error
        with self.assertRaises(ValueError):
            reaction.execute(self.organelle, time_step=1.0)

    def test_reaction_with_nonexistent_metabolites(self):
        """Test reaction where both consumed and produced metabolites are missing."""
        reaction = Reaction(
            name="Missing Metabolites",
            enzyme=self.enzyme,
            consume={"A": 1.0, "B": 2.0},
            produce={"C": 1.0, "D": 2.0},
        )

        # No metabolites initialized

        # Execute reaction and expect an error for missing A first
        with self.assertRaises(UnknownMetaboliteError):
            reaction.execute(self.organelle, time_step=1.0)

    def test_reaction_with_high_precision_quantities(self):
        """Test reaction handling high-precision floating point quantities."""
        reaction = Reaction(
            name="High Precision Reaction",
            enzyme=self.enzyme,
            consume={"A": 0.333333},
            produce={"B": 0.666666},
        )

        # Initialize metabolites with high precision
        self.organelle.add_metabolite(
            "A", type="substrate", quantity=1.000000, max_quantity=100.0
        )
        self.organelle.add_metabolite(
            "B", type="product", quantity=0.000000, max_quantity=100.0
        )

        # Execute reaction
        actual_rate = reaction.execute(self.organelle, time_step=1.0)

        # Assertions
        expected_rate = min(
            self.enzyme.calculate_rate_return * 1.0,
            self.organelle.get_metabolite_quantity("A") / 0.333333,
        )
        self.assertAlmostEqual(actual_rate, 1.0, places=5)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("A"), 1.0 - 0.333333 * 1.0, places=5)
        self.assertAlmostEqual(self.organelle.get_metabolite_quantity("B"), 0.666666 * 1.0, places=5)


if __name__ == "__main__":
    unittest.main()