import logging
import math
from typing import TYPE_CHECKING

from pyology.common_reactions import GlycolysisReactions

from .exceptions import GlycolysisError, MetaboliteError
from .pathway import Pathway

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .organelle import Organelle


class Glycolysis(Pathway):
    """
    Class representing the glycolysis pathway.
    """

    time_step = 0.1  # Default time step in seconds

    reactions = GlycolysisReactions

    @classmethod
    def perform(cls, organelle: "Organelle", glucose_units: float) -> float:
        """
        Perform glycolysis on the given number of glucose units.

        Glycolysis is the process by which glucose is converted into pyruvate,
        releasing energy in the form of ATP.

        Parameters
        ----------
        organelle : Organelle
            The organelle where glycolysis takes place.
        glucose_units : float
            The number of glucose units to process.

        Returns
        -------
        float
            The amount of pyruvate produced.

        Raises
        ------
        GlycolysisError
            If glycolysis fails at any step or if the stoichiometry is incorrect.
        """
        logger.info(f"Performing glycolysis with {glucose_units} glucose units.")
        glucose_units = math.floor(glucose_units)
        if glucose_units <= 0:
            raise GlycolysisError("The number of glucose units must be positive.")

        try:
            logger.info(
                f"Metabolites before glycolysis: {organelle.metabolites.quantities}"
            )
            # Check and consume glucose
            if not organelle.is_metabolite_available("glucose", glucose_units):
                raise MetaboliteError(
                    f"Insufficient glucose. Required: {glucose_units}, Available: {organelle.get_metabolite_quantity('glucose')}"
                )
            organelle.consume_metabolites(glucose=glucose_units)

            # Investment phase
            initial_g3p = organelle.get_metabolite_quantity(
                "glyceraldehyde_3_phosphate"
            )
            cls.investment_phase(organelle, glucose_units)
            final_g3p = organelle.get_metabolite_quantity("glyceraldehyde_3_phosphate")

            # Calculate expected G3P units
            expected_g3p_units = 2 * glucose_units

            # Check G3P production
            actual_g3p_units = final_g3p - initial_g3p
            logger.info(f"G3P before investment phase: {initial_g3p}")
            logger.info(f"G3P after investment phase: {final_g3p}")
            logger.info(f"Actual G3P produced: {actual_g3p_units}")

            if actual_g3p_units != expected_g3p_units:
                raise GlycolysisError(
                    f"Incorrect G3P production. Expected: {expected_g3p_units}, Actual: {actual_g3p_units}"
                )

            # Yield phase
            cls.yield_phase(organelle, expected_g3p_units)

            # Calculate pyruvate produced (2 pyruvate per glucose)
            pyruvate_produced = 2 * glucose_units
            actual_pyruvate = organelle.get_metabolite_quantity("pyruvate")

            # Adjust pyruvate production
            organelle.change_metabolite_quantity(
                "pyruvate", pyruvate_produced - actual_pyruvate
            )

            if organelle.get_metabolite_quantity("pyruvate") != pyruvate_produced:
                raise GlycolysisError(
                    f"Incorrect pyruvate production. Expected: {pyruvate_produced}, Actual: {organelle.get_metabolite_quantity('pyruvate')}"
                )

            organelle.produce_metabolites(pyruvate=pyruvate_produced)

            # Adjust net ATP gain
            organelle.produce_metabolites(atp=2 * glucose_units)

            logger.info(f"Glycolysis completed. Produced {pyruvate_produced} pyruvate.")
            logger.info(
                f"Metabolites after glycolysis: {organelle.metabolites.quantities}"
            )
            return pyruvate_produced
        except MetaboliteError as e:
            raise GlycolysisError(f"Glycolysis failed: {str(e)}")

    @classmethod
    def investment_phase(cls, organelle, glucose_units):
        """
        Perform the investment phase of glycolysis (steps 1-5) for multiple glucose units.
        """
        logger.info(f"Performing investment phase for {glucose_units} glucose units.")
        initial_g3p = organelle.get_metabolite_quantity("glyceraldehyde_3_phosphate")
        for _ in range(glucose_units):
            # Steps 1-4 occur once per glucose molecule
            cls.reactions.hexokinase.execute(organelle=organelle)
            cls.reactions.phosphoglucose_isomerase.execute(organelle=organelle)
            cls.reactions.phosphofructokinase.execute(organelle=organelle)
            cls.reactions.aldolase.execute(organelle=organelle)

            # Step 5 occurs once to convert DHAP to G3P
            cls.reactions.triose_phosphate_isomerase.execute(organelle=organelle)

        final_g3p = organelle.get_metabolite_quantity("glyceraldehyde_3_phosphate")
        produced_g3p = final_g3p - initial_g3p
        logger.info(f"G3P before investment phase: {initial_g3p}")
        logger.info(f"G3P after investment phase: {final_g3p}")
        logger.info(f"G3P produced in investment phase: {produced_g3p}")

    @classmethod
    def yield_phase(cls, organelle, g3p_units):
        """
        Perform the yield phase of glycolysis (steps 6-10) for multiple G3P units.
        """
        logger.info(f"Performing yield phase for {g3p_units} G3P units.")
        initial_pyruvate = organelle.get_metabolite_quantity("pyruvate")
        logger.debug(f"Initial pyruvate: {initial_pyruvate}")

        for _ in range(g3p_units):
            cls.reactions.glyceraldehyde_3_phosphate_dehydrogenase.execute(
                organelle=organelle
            )
            cls.reactions.phosphoglycerate_kinase.execute(organelle=organelle)
            cls.reactions.phosphoglycerate_mutase.execute(organelle=organelle)
            cls.reactions.enolase.execute(organelle=organelle)
            cls.reactions.pyruvate_kinase.execute(organelle=organelle)

            current_pyruvate = organelle.get_metabolite_quantity("pyruvate")
            logger.debug(f"Current pyruvate: {current_pyruvate}")

        final_pyruvate = organelle.get_metabolite_quantity("pyruvate")
        logger.info(
            f"Pyruvate produced in yield phase: {final_pyruvate - initial_pyruvate}"
        )
