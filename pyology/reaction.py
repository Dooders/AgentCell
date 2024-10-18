import logging
from typing import TYPE_CHECKING, Dict
from .exceptions import ReactionError  # Add this import

if TYPE_CHECKING:
    from .enzymes import Enzyme


logger = logging.getLogger(__name__)


class Reaction:
    def __init__(
        self,
        name: str,
        enzyme: "Enzyme",
        substrates: Dict[str, float],
        products: Dict[str, float],
        reversible: bool = False,
    ):
        self.name = name
        self.enzyme = enzyme
        self.substrates = substrates
        self.products = products
        self.reversible = reversible

    def can_react(self, organelle) -> bool:
        for substrate, amount in self.substrates.items():
            if organelle.get_metabolite_quantity(substrate) < amount:
                return False
        return True

    def execute(
        self, organelle, time_step: float = 1.0, use_rates: bool = False
    ) -> float:
        logger.info(f"Executing {self.name} reaction")
        logger.info(f"Substrates: {self.substrates}")
        logger.info(f"Products: {self.products}")
        for substrate, amount in self.substrates.items():
            available = organelle.get_metabolite_quantity(substrate)
            logger.info(f"{substrate} - Required: {amount}, Available: {available}")

        if time_step < 0:
            raise ValueError("Time step cannot be negative")

        if use_rates:
            result = self._execute_with_rates(organelle, time_step)
        else:
            result = self._execute_without_rates(organelle, time_step)

        if result == 0.0:
            logger.error(f"Reaction '{self.name}' failed to execute")
            raise ReactionError(f"Reaction '{self.name}' failed to execute")

        logger.info(f"Reaction '{self.name}' executed successfully")
        return result

    def _execute_with_rates(self, organelle, time_step: float) -> float:
        # Calculate reaction rate using the updated Enzyme.calculate_rate method
        metabolites = {met: organelle.get_metabolite(met) for met in self.substrates}

        # Check if k_m is a dictionary or a single value
        if isinstance(self.enzyme.k_m, dict):
            metabolites.update(
                {met: organelle.get_metabolite(met) for met in self.enzyme.k_m.keys()}
            )

        reaction_rate = self.enzyme.calculate_rate(metabolites)

        # Log intermediate values
        logger.debug(
            f"Reaction '{self.name}': Initial reaction rate: {reaction_rate:.6f}"
        )

        # Calculate potential limiting factors
        limiting_factors = {"reaction_rate": reaction_rate * time_step}
        for met, amount in self.substrates.items():
            if amount > 0:
                limiting_factors[f"{met}_conc"] = (
                    organelle.get_metabolite_quantity(met) / amount
                )

        # Determine actual rate based on available metabolites
        actual_rate = min(limiting_factors.values())

        # Log all limiting factors
        logger.debug(f"Reaction '{self.name}': Potential limiting factors:")
        for factor_name, factor_value in limiting_factors.items():
            logger.debug(f"  - {factor_name}: {factor_value:.6f}")

        # Identify the actual limiting factor(s)
        limiting_factor_names = [
            name for name, value in limiting_factors.items() if value == actual_rate
        ]
        logger.debug(
            f"Reaction '{self.name}': Rate limited by {', '.join(limiting_factor_names)}. "
            f"Actual rate: {actual_rate:.6f}"
        )

        # Consume metabolites
        for metabolite, amount in self.substrates.items():
            organelle.change_metabolite_quantity(metabolite, -amount * actual_rate)

        # Produce metabolites
        for metabolite, amount in self.products.items():
            organelle.change_metabolite_quantity(metabolite, amount * actual_rate)

        # Add log entry
        logger.info(
            f"Executed reaction '{self.name}' with rate {actual_rate:.4f}. "
            f"Consumed: {', '.join([f'{m}: {a * actual_rate:.4f}' for m, a in self.substrates.items()])}. "
            f"Produced: {', '.join([f'{m}: {a * actual_rate:.4f}' for m, a in self.products.items()])}"
        )

        return actual_rate

    def _execute_without_rates(self, organelle, time_step: float) -> float:
        # Check if all substrates are available in sufficient quantities
        for metabolite, amount in self.substrates.items():
            available = organelle.get_metabolite_quantity(metabolite)
            if available < amount:
                logger.error(f"Reaction '{self.name}': Insufficient {metabolite}. "
                             f"Required: {amount}, Available: {available}")
                return 0.0

        # Consume substrates
        for metabolite, amount in self.substrates.items():
            organelle.change_metabolite_quantity(metabolite, -amount)
            logger.debug(f"Reaction '{self.name}': Consumed {amount} {metabolite}")

        # Produce products
        for metabolite, amount in self.products.items():
            organelle.change_metabolite_quantity(metabolite, amount)
            logger.debug(f"Reaction '{self.name}': Produced {amount} {metabolite}")

        # Add log entry
        logger.info(
            f"Executed reaction '{self.name}' without rates. "
            f"Consumed: {', '.join([f'{m}: {a:.4f}' for m, a in self.substrates.items()])}. "
            f"Produced: {', '.join([f'{m}: {a:.4f}' for m, a in self.products.items()])}"
        )

        return 1.0  # Return 1.0 to indicate the reaction occurred once


def perform_reaction(metabolites: Dict[str, float], reaction: Reaction) -> bool:
    """
    Performs a specified reaction if possible.

    Args:
        metabolites (dict): Dictionary of metabolite concentrations.
        reaction (Reaction): The reaction to perform.

    Returns:
        bool: Result of the reaction execution.
    """
    return reaction.execute(metabolites)
