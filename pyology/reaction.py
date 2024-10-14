import logging
from typing import Dict

from .enzymes import Enzyme

logger = logging.getLogger(__name__)


class Reaction:
    def __init__(
        self,
        name: str,
        enzyme: Enzyme,
        consume: Dict[str, float],
        produce: Dict[str, float],
    ):
        self.name = name
        self.enzyme = enzyme
        self.consume = consume
        self.produce = produce

    def execute(self, organelle, time_step: float = 1.0, factor: float = 1.0) -> float:
        substrate = list(self.consume.keys())[0]
        substrate_conc = organelle.get_metabolite_quantity(substrate)

        # Calculate reaction rate using the updated Enzyme.calculate_rate method
        reaction_rate = (
            self.enzyme.calculate_rate(substrate_conc, organelle.metabolites)
            * time_step
            * factor
        )

        # Log intermediate values
        logger.debug(
            f"Reaction '{self.name}': Initial reaction rate: {reaction_rate:.6f}"
        )

        # Determine actual rate based on available metabolites
        actual_rate = min(
            reaction_rate,
            substrate_conc / factor,
            *[
                organelle.get_metabolite_quantity(met) / (amount * factor)
                for met, amount in self.consume.items()
            ],
        )

        # Log limiting factors
        if actual_rate < reaction_rate:
            limiting_factor = (
                "substrate concentration"
                if actual_rate == substrate_conc / factor
                else "other metabolite"
            )
            logger.debug(
                f"Reaction '{self.name}': Rate limited by {limiting_factor}. Actual rate: {actual_rate:.6f}"
            )

        # Consume metabolites
        for metabolite, amount in self.consume.items():
            organelle.change_metabolite_quantity(
                metabolite, -amount * actual_rate * factor
            )

        # Produce metabolites
        for metabolite, amount in self.produce.items():
            organelle.change_metabolite_quantity(
                metabolite, amount * actual_rate * factor
            )

        # Add log entry
        logger.info(
            f"Executed reaction '{self.name}' with rate {actual_rate:.4f} and factor {factor:.4f}. "
            f"Consumed: {', '.join([f'{m}: {a * actual_rate * factor:.4f}' for m, a in self.consume.items()])}. "
            f"Produced: {', '.join([f'{m}: {a * actual_rate * factor:.4f}' for m, a in self.produce.items()])}"
        )

        return actual_rate
