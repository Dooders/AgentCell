import logging
from typing import TYPE_CHECKING, Tuple

from .common_reactions import KrebsCycleReactions
from .energy_calculations import (
    calculate_energy_state,
    calculate_total_adenine_nucleotides,
)
from .exceptions import KrebsCycleError, ReactionError
from .pathway import Pathway

if TYPE_CHECKING:
    from .organelle import Organelle


class KrebsCycle(Pathway):
    """
    Class representing the Krebs Cycle (Citric Acid Cycle) pathway.

    The Krebs Cycle is a series of chemical reactions used by all aerobic organisms
    to release stored energy through the oxidation of acetyl-CoA derived from carbohydrates,
    fats, and proteins.

    Methods
    -------
    run:
        Executes the Krebs Cycle pathway for a given number of acetyl-CoA units.
    cycle:
        Executes one complete cycle of the Krebs Cycle.
    """

    time_step = 1
    reactions = KrebsCycleReactions

    def __init__(self, debug=True):
        self.debug = debug
        self.reactions = KrebsCycleReactions()

    def run(
        self, organelle: "Organelle", acetyl_coa_units: float, logger: logging.Logger
    ) -> Tuple[float, float, float]:
        """
        Executes the Krebs Cycle pathway for a given number of acetyl-CoA units.

        Parameters
        ----------
        organelle: Organelle
            The organelle to run the Krebs Cycle pathway on.
        acetyl_coa_units: float
            The number of acetyl-CoA units to process.
        logger: logging.Logger
            The logger to use for logging messages.

        Returns
        -------
        Tuple[float, float, float]:
            A tuple containing the final energy state, final adenine nucleotides,
            and the number of CO2 produced.

        Raises
        ------
        KrebsCycleError:
            If the Krebs Cycle pathway fails to complete.
        """
        try:
            if acetyl_coa_units <= 0:
                raise KrebsCycleError(
                    "The number of acetyl-CoA units must be positive."
                )

            initial_energy = calculate_energy_state(organelle, logger)
            initial_adenine = calculate_total_adenine_nucleotides(organelle)

            co2_produced = 0
            total_energy_produced = 0
            for i in range(int(acetyl_coa_units)):
                cycle_results, cycle_energy = self.cycle(organelle, logger)
                co2_produced += cycle_results
                total_energy_produced += cycle_energy

            logger.info(f"Krebs Cycle completed. Produced {co2_produced} CO2.")
            logger.info(f"Total energy produced: {total_energy_produced} kJ/mol")

            final_energy = calculate_energy_state(organelle, logger)
            final_adenine = calculate_total_adenine_nucleotides(organelle)

            # Check energy conservation
            energy_difference = final_energy - initial_energy - total_energy_produced
            if abs(energy_difference) > 1e-6:
                logger.warning(
                    f"Energy not conserved in Krebs Cycle. Difference: {energy_difference}"
                )

            # Check adenine nucleotide conservation
            adenine_difference = final_adenine - initial_adenine
            if abs(adenine_difference) > 1e-6:
                logger.warning(
                    f"Adenine nucleotides not conserved in Krebs Cycle. Difference: {adenine_difference}"
                )

            return final_energy, final_adenine, co2_produced

        except Exception as e:
            logger.error(f"Error during Krebs Cycle: {str(e)}")
            raise KrebsCycleError(f"Krebs Cycle failed: {str(e)}")

    def cycle(self, organelle: "Organelle", logger: logging.Logger) -> Tuple[int, float]:
        logger.info("Starting Krebs Cycle")
        co2_produced = 0
        energy_produced = 0

        try:

            for reaction in [
                self.reactions.citrate_synthase,
                self.reactions.aconitase,
                self.reactions.isocitrate_dehydrogenase,
                self.reactions.alpha_ketoglutarate_dehydrogenase,
                self.reactions.succinyl_coa_synthetase,
                self.reactions.succinate_dehydrogenase,
                self.reactions.fumarase,
                self.reactions.malate_dehydrogenase,
            ]:
                logger.info(f"Executing reaction: {reaction.name}")
                logger.info(f"Substrates before reaction: {reaction.substrates}")
                
                # Execute reaction and track energy changes
                reaction_energy = reaction.transform(organelle=organelle)
                energy_produced += reaction_energy
                
                if reaction.name in ["Isocitrate Dehydrogenase", "α_Ketoglutarate Dehydrogenase"]:
                    co2_produced += 1
                logger.info(f"Energy produced in {reaction.name}: {reaction_energy} kJ/mol")

            # Calculate total NADH, FADH2, and GTP produced
            nadh_produced = organelle.get_metabolite_quantity("NADH") - organelle.get_metabolite_quantity("NAD+")
            fadh2_produced = organelle.get_metabolite_quantity("FADH2") - organelle.get_metabolite_quantity("FAD")
            gtp_produced = organelle.get_metabolite_quantity("GTP") - organelle.get_metabolite_quantity("GDP")
            
            # Calculate energy from electron transport chain (more accurate values)
            etc_energy = nadh_produced * 2.5 + fadh2_produced * 1.5 + gtp_produced  # ATP equivalents
            atp_energy = 30.5  # kJ/mol of ATP
            energy_produced += etc_energy * atp_energy

            logger.info(f"Krebs Cycle completed. CO2 produced: {co2_produced}")
            logger.info(f"Total energy produced: {energy_produced:.2f} kJ/mol")
            logger.info(f"NADH produced: {nadh_produced}, FADH2 produced: {fadh2_produced}, GTP produced: {gtp_produced}")

        except ReactionError as e:
            logger.error(f"Krebs Cycle failed: {str(e)}")
            raise KrebsCycleError(f"Krebs Cycle failed: {str(e)}")

        return co2_produced, energy_produced
