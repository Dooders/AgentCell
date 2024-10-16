import logging
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from .enzymes import Enzyme


logger = logging.getLogger(__name__)


class Reaction:
    def __init__(
        self,
        name: str,
        enzyme: "Enzyme",
        consume: Dict[str, float],
        produce: Dict[str, float],
    ):
        self.name = name
        self.enzyme = enzyme
        self.consume = consume
        self.produce = produce

    def execute(self, organelle, time_step: float = 1.0) -> float:
        substrate = list(self.consume.keys())[0]
        substrate_conc = organelle.get_metabolite_quantity(substrate)
        # Calculate reaction rate using the updated Enzyme.calculate_rate method
        reaction_rate = (
            self.enzyme.calculate_rate(substrate_conc, organelle.metabolites)
            * time_step
        )

        # Log intermediate values
        logger.debug(
            f"Reaction '{self.name}': Initial reaction rate: {reaction_rate:.6f}"
        )

        # Calculate potential limiting factors
        limiting_factors = {
            "reaction_rate": reaction_rate,
            "substrate_conc": substrate_conc,
        }
        for met, amount in self.consume.items():
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
        for metabolite, amount in self.consume.items():
            organelle.change_metabolite_quantity(metabolite, -amount * actual_rate)

        # Produce metabolites
        for metabolite, amount in self.produce.items():
            organelle.change_metabolite_quantity(metabolite, amount * actual_rate)

        # Add log entry
        logger.info(
            f"Executed reaction '{self.name}' with rate {actual_rate:.4f}. "
            f"Consumed: {', '.join([f'{m}: {a * actual_rate:.4f}' for m, a in self.consume.items()])}. "
            f"Produced: {', '.join([f'{m}: {a * actual_rate:.4f}' for m, a in self.produce.items()])}"
        )

        return actual_rate
