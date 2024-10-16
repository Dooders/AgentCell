import logging
import math
from enum import Enum
from typing import TYPE_CHECKING

from .enzymes import Enzyme
from .exceptions import GlycolysisError, MetaboliteError
from .reaction import Reaction

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .organelle import Organelle


class GlycolysisSteps(Enum):
    HEXOKINASE = "hexokinase"
    PHOSPHOGLUCOSE_ISOMERASE = "phosphoglucose_isomerase"
    PHOSPHOFRUCTOKINASE = "phosphofructokinase"
    ALDOLASE = "aldolase"
    TRIOSE_PHOSPHATE_ISOMERASE = "triose_phosphate_isomerase"
    GLYCERALDEHYDE_3_PHOSPHATE_DEHYDROGENASE = (
        "glyceraldehyde_3_phosphate_dehydrogenase"
    )
    PHOSPHOGLYCERATE_KINASE = "phosphoglycerate_kinase"
    PHOSPHOGLYCERATE_MUTASE = "phosphoglycerate_mutase"
    ENOLASE = "enolase"
    PYRUVATE_KINASE = "pyruvate_kinase"


class GlycolysisPathway:
    """
    Class representing the glycolysis pathway.
    """

    time_step = 0.1  # Default time step in seconds

    enzymes = {
        "hexokinase": Enzyme(
            "Hexokinase", k_cat=10.0, k_m={"glucose": 0.1, "glucose_6_phosphate": 0.5}
        ),
        "phosphoglucose_isomerase": Enzyme(
            "Phosphoglucose Isomerase", k_cat=12.0, k_m={"glucose_6_phosphate": 0.2}
        ),
        "phosphofructokinase": Enzyme(
            "Phosphofructokinase",
            k_cat=8.0,
            k_m={"atp": 1.0},
            inhibitors={"atp": 1.0},
            activators={"adp": 0.5, "amp": 0.1},
        ),
        "aldolase": Enzyme(
            "Aldolase", k_cat=7.0, k_m={"fructose_1_6_bisphosphate": 0.3}
        ),
        "triose_phosphate_isomerase": Enzyme(
            "Triose Phosphate Isomerase",
            k_cat=15.0,
            k_m={"dihydroxyacetone_phosphate": 0.1},
        ),
        "glyceraldehyde_3_phosphate_dehydrogenase": Enzyme(
            "Glyceraldehyde 3-Phosphate Dehydrogenase",
            k_cat=6.0,
            k_m={"nadh": 0.5},
        ),
        "phosphoglycerate_kinase": Enzyme(
            "Phosphoglycerate Kinase", k_cat=9.0, k_m={"bisphosphoglycerate_1_3": 0.2}
        ),
        "phosphoglycerate_mutase": Enzyme(
            "Phosphoglycerate Mutase", k_cat=11.0, k_m={"phosphoglycerate_3": 0.15}
        ),
        "enolase": Enzyme("Enolase", k_cat=7.5, k_m={"phosphoglycerate_2": 0.3}),
        "pyruvate_kinase": Enzyme(
            "Pyruvate Kinase",
            k_cat=10.0,
            k_m={"atp": 0.2},
            inhibitors={"atp": 0.8},
            activators={"fructose_1_6_bisphosphate": 0.3},
        ),
    }

    reactions = {
        # Glucose + ATP → Glucose-6-phosphate + ADP
        "hexokinase": Reaction(
            name="Hexokinase",
            enzyme=enzymes["hexokinase"],
            consume={"glucose": 1, "atp": 1},
            produce={"glucose_6_phosphate": 1, "adp": 1},
        ),
        # Glucose-6-phosphate ⇌ Fructose-6-phosphate
        "phosphoglucose_isomerase": Reaction(
            name="Phosphoglucose Isomerase",
            enzyme=enzymes["phosphoglucose_isomerase"],
            consume={"glucose_6_phosphate": 1},
            produce={"fructose_6_phosphate": 1},
        ),
        # Fructose-6-phosphate + ATP → Fructose-1,6-bisphosphate + ADP
        "phosphofructokinase": Reaction(
            name="Phosphofructokinase",
            enzyme=enzymes["phosphofructokinase"],
            consume={"fructose_6_phosphate": 1, "atp": 1},
            produce={"fructose_1_6_bisphosphate": 1, "adp": 1},
        ),
        # Fructose-1,6-bisphosphate → Dihydroxyacetone phosphate + Glyceraldehyde-3-phosphate
        "aldolase": Reaction(
            name="Aldolase",
            enzyme=enzymes["aldolase"],
            consume={"fructose_1_6_bisphosphate": 1},
            produce={
                "glyceraldehyde_3_phosphate": 1,
                "dihydroxyacetone_phosphate": 1,
            },
        ),
        # Dihydroxyacetone phosphate → Glyceraldehyde-3-phosphate
        "triose_phosphate_isomerase": Reaction(
            name="Triose Phosphate Isomerase",
            enzyme=enzymes["triose_phosphate_isomerase"],
            consume={"dihydroxyacetone_phosphate": 1},
            produce={"glyceraldehyde_3_phosphate": 1},
        ),
        # Glyceraldehyde-3-phosphate + NAD+ + Pi → 1,3-Bisphosphoglycerate + NADH + H+
        "glyceraldehyde_3_phosphate_dehydrogenase": Reaction(
            name="Glyceraldehyde 3-Phosphate Dehydrogenase",
            enzyme=enzymes["glyceraldehyde_3_phosphate_dehydrogenase"],
            consume={"glyceraldehyde_3_phosphate": 1, "nad": 1, "pi": 1},
            produce={"bisphosphoglycerate_1_3": 1, "nadh": 1, "h_plus": 1},
        ),
        # 1,3-Bisphosphoglycerate + ADP ⇌ 3-Phosphoglycerate + ATP
        "phosphoglycerate_kinase": Reaction(
            name="Phosphoglycerate Kinase",
            enzyme=enzymes["phosphoglycerate_kinase"],
            consume={"bisphosphoglycerate_1_3": 1, "adp": 1},
            produce={"phosphoglycerate_3": 1, "atp": 1},
        ),
        # 3-Phosphoglycerate ⇌ 2-Phosphoglycerate
        "phosphoglycerate_mutase": Reaction(
            name="Phosphoglycerate Mutase",
            enzyme=enzymes["phosphoglycerate_mutase"],
            consume={"phosphoglycerate_3": 1},
            produce={"phosphoglycerate_2": 1},
        ),
        # 2-Phosphoglycerate ⇌ Phosphoenolpyruvate + H2O
        "enolase": Reaction(
            name="Enolase",
            enzyme=enzymes["enolase"],
            consume={"phosphoglycerate_2": 1},
            produce={"phosphoenolpyruvate": 1, "h2o": 1},
        ),
        # Phosphoenolpyruvate + ADP → Pyruvate + ATP
        "pyruvate_kinase": Reaction(
            name="Pyruvate Kinase",
            enzyme=enzymes["pyruvate_kinase"],
            consume={"phosphoenolpyruvate": 1, "adp": 1},
            produce={"pyruvate": 1, "atp": 1},
        ),
    }

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
        for step in list(GlycolysisSteps)[:4]:
            cls.reactions[step.value].execute(organelle=organelle)

        # Step 5 occurs once to convert DHAP to G3P
        cls.reactions[GlycolysisSteps.TRIOSE_PHOSPHATE_ISOMERASE.value].execute(
            organelle=organelle
        )

    @classmethod
    def yield_phase(cls, organelle, g3p_units):
        """
        Perform the yield phase of glycolysis (steps 6-10) for multiple G3P units.
        """
        logger.info(f"Performing yield phase for {g3p_units} G3P units.")
        for step in list(GlycolysisSteps)[5:]:
            cls.reactions[step.value].execute(organelle=organelle)
