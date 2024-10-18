import logging
import math
from typing import TYPE_CHECKING

from pyology.common_reactions import GlycolysisReactions

from .exceptions import GlycolysisError, MetaboliteError, ReactionError
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
        logger.info(f"Starting glycolysis with {glucose_units} glucose units")
        logger.info(f"Initial metabolite levels: {organelle.metabolites.quantities}")
        glucose_units = math.floor(glucose_units)
        if glucose_units <= 0:
            raise GlycolysisError("The number of glucose units must be positive.")

        try:
            logger.info(
                f"Metabolites before glycolysis: {organelle.metabolites.quantities}"
            )
            # Check glucose availability
            glucose_available = organelle.get_metabolite_quantity("glucose")
            atp_available = organelle.get_metabolite_quantity("ATP")

            if glucose_available < glucose_units or atp_available < glucose_units:
                logger.error(
                    f"Insufficient metabolites for glycolysis. Glucose: {glucose_available}, ATP: {atp_available}"
                )
                raise MetaboliteError(
                    f"Insufficient metabolites for glycolysis. Required: {glucose_units} glucose and ATP, Available: {glucose_available} glucose, {atp_available} ATP"
                )

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

            # Add this after the investment phase and before the pay-off phase
            cls.enolase_reaction(organelle)

            # Yield phase
            cls.yield_phase(organelle, expected_g3p_units)

            # Calculate pyruvate produced (2 pyruvate per glucose)
            pyruvate_produced = 2 * glucose_units
            actual_pyruvate = organelle.get_metabolite_quantity("pyruvate")

            # Adjust pyruvate production (accounting for any pre-existing pyruvate)
            organelle.change_metabolite_quantity(
                "pyruvate", pyruvate_produced - actual_pyruvate
            )

            if organelle.get_metabolite_quantity("pyruvate") != pyruvate_produced:
                raise GlycolysisError(
                    f"Incorrect pyruvate production. Expected: {pyruvate_produced}, Actual: {organelle.get_metabolite_quantity('pyruvate')}"
                )

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
        logger.info(f"Starting investment phase with {glucose_units} glucose units")
        logger.info(
            f"Metabolite levels before investment phase: {organelle.metabolites.quantities}"
        )

        initial_g3p = organelle.get_metabolite_quantity("glyceraldehyde_3_phosphate")

        for i in range(glucose_units):
            logger.info(
                f"🔄🔄🔄 Processing glucose unit {i+1} of {glucose_units} 🔄🔄🔄"
            )
            try:
                # Steps 1-4 occur once per glucose molecule
                cls.reactions.hexokinase.execute(organelle=organelle)
                cls.reactions.phosphoglucose_isomerase.execute(organelle=organelle)
                cls.reactions.phosphofructokinase.execute(organelle=organelle)
                cls.reactions.aldolase.execute(organelle=organelle)

                # Step 5 occurs once to convert DHAP to G3P
                cls.reactions.triose_phosphate_isomerase.execute(organelle=organelle)

            except ReactionError as e:
                logger.error(f"Investment phase failed at glucose unit {i+1}: {str(e)}")
                raise GlycolysisError(
                    f"Investment phase failed at glucose unit {i+1}: {str(e)}"
                )

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

        for i in range(g3p_units):
            logger.info(f"🍀🍀🍀 Processing G3P unit {i+1} of {g3p_units} 🍀🍀🍀")
            try:
                cls.reactions.glyceraldehyde_3_phosphate_dehydrogenase.execute(
                    organelle=organelle
                )
                cls.reactions.phosphoglycerate_kinase.execute(organelle=organelle)
                cls.reactions.phosphoglycerate_mutase.execute(organelle=organelle)
                cls.reactions.enolase.execute(organelle=organelle)
                cls.reactions.pyruvate_kinase.execute(organelle=organelle)
            except ReactionError as e:
                raise GlycolysisError(f"Yield phase failed at G3P unit {i+1}: {str(e)}")

            current_pyruvate = organelle.get_metabolite_quantity("pyruvate")
            logger.debug(f"Current pyruvate: {current_pyruvate}")

        final_pyruvate = organelle.get_metabolite_quantity("pyruvate")
        logger.info(
            f"Pyruvate produced in yield phase: {final_pyruvate - initial_pyruvate}"
        )

    @classmethod
    def enolase_reaction(cls, organelle: "Organelle"):
        enolase = GlycolysisReactions.enolase
        phosphoglycerate_2 = organelle.get_metabolite_quantity("phosphoglycerate_2")
        
        while phosphoglycerate_2 > 0:
            reaction_result = enolase.execute(organelle)
            if reaction_result == 0:
                break
            phosphoglycerate_2 = organelle.get_metabolite_quantity("phosphoglycerate_2")

        logger.info(f"Enolase reaction completed. Remaining 2-phosphoglycerate: {phosphoglycerate_2}")
