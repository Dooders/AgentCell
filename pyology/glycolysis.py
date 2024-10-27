import logging
from typing import TYPE_CHECKING, Tuple

from utils.command_data import CommandData
from utils.tracking import execute_command

from .common_reactions import GlycolysisReactions
from .energy_calculations import (
    calculate_energy_state,
    calculate_total_adenine_nucleotides,
)
from .exceptions import GlycolysisError, ReactionError
from .pathway import Pathway

if TYPE_CHECKING:
    from .organelle import Organelle


class Glycolysis(Pathway):
    """
    Class representing the glycolysis pathway.

    Glycolysis is the first step in cellular respiration, where glucose is
    broken down into pyruvate.

    It occurs over two phases: investment and yield.

    During the investment phase, glucose is converted into 3-phosphoglycerate,
    which is then converted into 2-phosphoglycerate. This is followed by a series
    of reactions that convert 2-phosphoglycerate into phosphoenolpyruvate, which
    is then converted into pyruvate.

    During the yield phase, pyruvate is converted into lactate. Which is used
    in the next step of cellular respiration.
    Methods
    -------
    run:
        Executes the glycolysis pathway for a given number of glucose units.
    investment_phase:
        Executes the investment phase of glycolysis.
    yield_phase:
        Executes the yield phase of glycolysis.
    """

    time_step = 1
    reactions = GlycolysisReactions

    def __init__(self, debug=False):
        self.debug = debug

    def run(
        self, organelle: "Organelle", glucose_units: float, logger: logging.Logger
    ) -> Tuple[float, float, float]:
        """
        Executes the glycolysis pathway for a given number of glucose units.

        Parameters
        ----------
        organelle: Organelle
            The organelle to run the glycolysis pathway on.
        glucose_units: float
            The number of glucose units to process.
        logger: logging.Logger
            The logger to use for logging messages.

        Returns
        -------
        Tuple[float, float, float]:
            A tuple containing the final energy state, final adenine nucleotides,
            and the number of pyruvate produced.

        Raises
        ------
        GlycolysisError:
            If the glycolysis pathway fails to complete.
        """
        try:
            if glucose_units <= 0:
                raise GlycolysisError("The number of glucose units must be positive.")

            initial_energy = organelle.metabolites.total_energy
            initial_adenine = calculate_total_adenine_nucleotides(organelle)
            logger.info(
                f"Initial energy: {initial_energy:.2f} kJ/mol, Initial adenine nucleotides: {initial_adenine:.2f} mol"
            )

            # Investment phase
            investment_results = execute_command(
                organelle,
                CommandData(
                    obj=self.__class__,  # Pass the class, not the instance
                    command=self.__class__.investment_phase,
                    tracked_attributes=["ATP", "ADP", "AMP", "glucose"],
                    args=(organelle, glucose_units, logger),
                ),
                logger=logger,
            )

            # Yield phase
            yield_results = execute_command(
                organelle,
                CommandData(
                    obj=self.__class__,
                    command=self.__class__.yield_phase,
                    tracked_attributes=["ATP", "ADP", "AMP"],
                    args=(organelle, glucose_units * 2, logger),  # Add logger here
                ),
                logger=logger,
            )

            pyruvate_produced = yield_results.result

            logger.info(f"Glycolysis completed. Produced {pyruvate_produced} pyruvate.")

            final_energy = organelle.metabolites.total_energy
            final_adenine = calculate_total_adenine_nucleotides(organelle)

            logger.info(
                f"Final energy: {final_energy:.2f} kJ/mol, Final adenine nucleotides: {final_adenine:.2f} mol"
            )

            #! Add these to checks and have as part of validation for commands
            # Check energy conservation
            energy_difference = final_energy - initial_energy
            if abs(energy_difference) > 1e-6:
                logger.warning(
                    f"Energy not conserved in glycolysis. Difference: {energy_difference}"
                )
            #! Add these to checks and have as part of validation for commands
            # Check adenine nucleotide conservation
            adenine_difference = final_adenine - initial_adenine
            if abs(adenine_difference) > 1e-6:
                logger.warning(
                    f"Adenine nucleotides not conserved in glycolysis. Difference: {adenine_difference}"
                )

            return final_energy, final_adenine, pyruvate_produced

        except Exception as e:
            logger.error(f"Error during glycolysis: {str(e)}")
            raise GlycolysisError(f"Glycolysis failed: {str(e)}")

    @classmethod
    def investment_phase(
        cls, organelle: "Organelle", glucose_units: float, logger: logging.Logger
    ) -> None:
        """
        Perform the investment phase of glycolysis (steps 1-5) for multiple glucose units.

        Parameters
        ----------
        organelle: Organelle
            The organelle to run the glycolysis pathway on.
        glucose_units: float
            The number of glucose units to process.
        logger: logging.Logger
            The logger to use for logging messages.

        Raises
        ------
        GlycolysisError:
            If the investment phase fails to complete.
        """
        logger.info(f"Starting investment phase with {glucose_units} glucose units")
        initial_atp = organelle.get_metabolite_quantity("ATP")

        for i in range(glucose_units):
            logger.info(
                f"🔄🔄🔄 Processing glucose unit {i+1} of {glucose_units} 🔄🔄🔄"
            )
            try:
                # Steps 1-4 occur once per glucose molecule
                cls.reactions.hexokinase.transform(organelle=organelle)
                cls.reactions.phosphoglucose_isomerase.transform(organelle=organelle)
                cls.reactions.phosphofructokinase.transform(organelle=organelle)
                cls.reactions.aldolase.transform(organelle=organelle)

                # Step 5 occurs once to convert DHAP to G3P
                cls.reactions.triose_phosphate_isomerase.transform(organelle=organelle)

            except ReactionError as e:
                logger.error(f"Investment phase failed at glucose unit {i+1}: {str(e)}")
                raise GlycolysisError(f"Investment phase failed: {str(e)}")

        final_atp = organelle.get_metabolite_quantity("ATP")
        logger.info(f"ATP consumed in investment phase: {initial_atp - final_atp}")

    @classmethod
    def yield_phase(
        cls, organelle: "Organelle", g3p_units: float, logger: logging.Logger
    ) -> None:
        """
        Perform the yield phase of glycolysis (steps 6-10) for multiple G3P units.

        Parameters
        ----------
        organelle: Organelle
            The organelle to run the glycolysis pathway on.
        g3p_units: float
            The number of G3P units to process.
        logger: logging.Logger
            The logger to use for logging messages.

        Raises
        ------
        GlycolysisError:
            If the yield phase fails to complete.
        """
        logger.info(f"Starting yield phase with {g3p_units} G3P units")
        initial_atp = organelle.get_metabolite_quantity("ATP")

        for i in range(g3p_units):
            logger.info(f"🍀🍀🍀 Processing G3P unit {i+1} of {g3p_units} 🍀🍀🍀")
            try:
                cls.reactions.glyceraldehyde_3_phosphate_dehydrogenase.transform(
                    organelle=organelle
                )
                cls.reactions.phosphoglycerate_kinase.transform(organelle=organelle)
                cls.reactions.phosphoglycerate_mutate.transform(organelle=organelle)
                cls.reactions.enolase.transform(organelle=organelle)
                cls.reactions.pyruvate_kinase.transform(organelle=organelle)

            except ReactionError as e:
                raise GlycolysisError(f"Yield phase failed at G3P unit {i+1}: {str(e)}")

        final_atp = organelle.get_metabolite_quantity("ATP")
        logger.info(f"ATP produced in yield phase: {final_atp - initial_atp}")


def energy_in_balance(initial_energy: float, final_energy: float) -> bool:
    """
    Check the energy balance of the glycolysis pathway by comparing the initial
    and final energy states.

    Returns
    -------
    bool:
        True if the energy balance is within the acceptable range, False otherwise.
    """
    return abs(initial_energy - final_energy) < 1e-6
