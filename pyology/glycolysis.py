import logging
import math
from enum import Enum
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
            If glycolysis fails at any step.
        """
        logger.info(f"Performing glycolysis with {glucose_units} glucose units.")
        glucose_units = math.floor(glucose_units)
        if glucose_units <= 0:
            raise GlycolysisError("The number of glucose units must be positive.")

        try:
            # Check and consume glucose
            if not organelle.is_metabolite_available("glucose", glucose_units):
                raise MetaboliteError(
                    f"Insufficient glucose. Required: {glucose_units}, Available: {organelle.get_metabolite_quantity('glucose')}"
                )
            organelle.consume_metabolites(glucose=glucose_units)

            # Investment phase
            cls.investment_phase(organelle, glucose_units)

            # Yield phase (2 G3P molecules per glucose)
            g3p_units = 2 * glucose_units
            cls.yield_phase(organelle, g3p_units)

            # Adjust net ATP gain
            organelle.produce_metabolites(atp=2 * glucose_units)

            pyruvate_produced = organelle.get_metabolite_quantity("pyruvate")
            logger.info(f"Glycolysis completed. Produced {pyruvate_produced} pyruvate.")
            return pyruvate_produced
        except MetaboliteError as e:
            raise GlycolysisError(f"Glycolysis failed: {str(e)}")

    @classmethod
    def investment_phase(cls, organelle, glucose_units):
        """
        Perform the investment phase of glycolysis (steps 1-5) for multiple glucose units.
        """
        logger.info(f"Performing investment phase for {glucose_units} glucose units.")
        # Steps 1-4 occur once per glucose molecule
        cls.reactions.hexokinase.execute(organelle=organelle)
        cls.reactions.phosphoglucose_isomerase.execute(organelle=organelle)
        cls.reactions.phosphofructokinase.execute(organelle=organelle)
        cls.reactions.aldolase.execute(organelle=organelle)

        # Step 5 occurs once to convert DHAP to G3P
        cls.reactions.triose_phosphate_isomerase.execute(organelle=organelle)

    @classmethod
    def yield_phase(cls, organelle, g3p_units):
        """
        Perform the yield phase of glycolysis (steps 6-10) for multiple G3P units.
        """
        logger.info(f"Performing yield phase for {g3p_units} G3P units.")
        cls.reactions.glyceraldehyde_3_phosphate_dehydrogenase.execute(
            organelle=organelle
        )
        cls.reactions.phosphoglycerate_kinase.execute(organelle=organelle)
        cls.reactions.phosphoglycerate_mutase.execute(organelle=organelle)
        cls.reactions.enolase.execute(organelle=organelle)
        cls.reactions.pyruvate_kinase.execute(organelle=organelle)
