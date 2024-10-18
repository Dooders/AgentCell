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
            initial_atp = organelle.get_metabolite_quantity("ATP")

            if glucose_available < glucose_units or initial_atp < glucose_units:
                logger.error(
                    f"Insufficient metabolites for glycolysis. Glucose: {glucose_available}, ATP: {initial_atp}"
                )
                raise MetaboliteError(
                    f"Insufficient metabolites for glycolysis. Required: {glucose_units} glucose and ATP, Available: {glucose_available} glucose, {initial_atp} ATP"
                )

            # Investment phase
            cls.investment_phase(organelle, glucose_units)

            atp_after_investment = organelle.get_metabolite_quantity("ATP")
            logger.info(f"ATP after investment phase: {atp_after_investment}")
            logger.info(
                f"ATP consumed in investment phase: {initial_atp - atp_after_investment}"
            )

            # Yield phase
            cls.yield_phase(organelle, glucose_units * 2)  # 2 G3P per glucose

            final_atp = organelle.get_metabolite_quantity("ATP")
            logger.info(f"Final ATP: {final_atp}")
            logger.info(f"Net ATP produced: {final_atp - initial_atp}")

            # Calculate pyruvate produced (2 pyruvate per glucose)
            pyruvate_produced = 2 * glucose_units

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
        initial_atp = organelle.get_metabolite_quantity("ATP")

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
        final_atp = organelle.get_metabolite_quantity("ATP")
        logger.info(f"ATP consumed in investment phase: {initial_atp - final_atp}")

    @classmethod
    def yield_phase(cls, organelle, g3p_units):
        """
        Perform the yield phase of glycolysis (steps 6-10) for multiple G3P units.
        """
        logger.info(f"Starting yield phase with {g3p_units} G3P units")
        initial_atp = organelle.get_metabolite_quantity("ATP")

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
        final_atp = organelle.get_metabolite_quantity("ATP")
        logger.info(f"ATP produced in yield phase: {final_atp - initial_atp}")

    @classmethod
    def enolase_reaction(cls, organelle: "Organelle"):
        initial_atp = organelle.get_metabolite_quantity("ATP")
        enolase = GlycolysisReactions.enolase
        phosphoglycerate_2 = organelle.get_metabolite_quantity("phosphoglycerate_2")

        while phosphoglycerate_2 > 0:
            reaction_result = enolase.execute(organelle)
            if reaction_result == 0:
                break
            phosphoglycerate_2 = organelle.get_metabolite_quantity("phosphoglycerate_2")

        final_atp = organelle.get_metabolite_quantity("ATP")
        logger.info(f"ATP change in enolase reaction: {final_atp - initial_atp}")
        logger.info(
            f"Enolase reaction completed. Remaining 2-phosphoglycerate: {phosphoglycerate_2}"
        )

    @classmethod
    def phosphoglycerate_kinase(cls, organelle):
        """1,3-Bisphosphoglycerate to 3-Phosphoglycerate"""
        reaction = cls.reactions.phosphoglycerate_kinase
        reaction.execute(organelle)

    @classmethod
    def pyruvate_kinase(cls, organelle):
        """Phosphoenolpyruvate to Pyruvate"""
        reaction = cls.reactions.pyruvate_kinase
        reaction.execute(organelle)
