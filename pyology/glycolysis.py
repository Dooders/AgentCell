import logging
import math
from enum import Enum
from typing import Dict

from .enzymes import Enzyme
from .exceptions import GlycolysisError, MetaboliteError
from .reaction import Reaction

logger = logging.getLogger(__name__)

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
            "Hexokinase", vmax=10.0, km=0.1, inhibitors={"glucose_6_phosphate": 0.5}
        ),
        "phosphoglucose_isomerase": Enzyme(
            "Phosphoglucose Isomerase", vmax=12.0, km=0.2
        ),
        "phosphofructokinase": Enzyme(
            "Phosphofructokinase",
            vmax=8.0,
            km=0.15,
            inhibitors={"atp": 1.0},
            activators={"adp": 0.5, "amp": 0.1},
        ),
        "aldolase": Enzyme("Aldolase", vmax=7.0, km=0.3),
        "triose_phosphate_isomerase": Enzyme(
            "Triose Phosphate Isomerase", vmax=15.0, km=0.1
        ),
        "glyceraldehyde_3_phosphate_dehydrogenase": Enzyme(
            "Glyceraldehyde 3-Phosphate Dehydrogenase",
            vmax=6.0,
            km=0.25,
            inhibitors={"nadh": 0.5},
        ),
        "phosphoglycerate_kinase": Enzyme("Phosphoglycerate Kinase", vmax=9.0, km=0.2),
        "phosphoglycerate_mutase": Enzyme(
            "Phosphoglycerate Mutase", vmax=11.0, km=0.15
        ),
        "enolase": Enzyme("Enolase", vmax=7.5, km=0.3),
        "pyruvate_kinase": Enzyme(
            "Pyruvate Kinase",
            vmax=10.0,
            km=0.2,
            inhibitors={"atp": 0.8},
            activators={"fructose_1_6_bisphosphate": 0.3},
        ),
    }

    reactions = {
        # Glucose + ATP → Glucose-6-phosphate + ADP
        "hexokinase": Reaction(
            "Hexokinase",
            enzymes["hexokinase"],
            consume={"glucose": 1, "atp": 1},
            produce={"glucose_6_phosphate": 1, "adp": 1},
        ),
        # Glucose-6-phosphate → Fructose-6-phosphate
        "phosphoglucose_isomerase": Reaction(
            "Phosphoglucose Isomerase",
            enzymes["phosphoglucose_isomerase"],
            consume={"glucose_6_phosphate": 1},
            produce={"fructose_6_phosphate": 1},
        ),
        # Fructose-6-phosphate + ATP → Fructose-1,6-bisphosphate + ADP
        "phosphofructokinase": Reaction(
            "Phosphofructokinase",
            enzymes["phosphofructokinase"],
            consume={"fructose_6_phosphate": 1, "atp": 1},
            produce={"fructose_1_6_bisphosphate": 1, "adp": 1},
        ),
        # Fructose-1,6-bisphosphate → Dihydroxyacetone phosphate + Glyceraldehyde-3-phosphate
        "aldolase": Reaction(
            "Aldolase",
            enzymes["aldolase"],
            consume={"fructose_1_6_bisphosphate": 1},
            produce={
                "glyceraldehyde_3_phosphate": 1,
                "dihydroxyacetone_phosphate": 1,
            },
        ),
        # Dihydroxyacetone phosphate → Glyceraldehyde-3-phosphate
        "triose_phosphate_isomerase": Reaction(
            "Triose Phosphate Isomerase",
            enzymes["triose_phosphate_isomerase"],
            consume={"dihydroxyacetone_phosphate": 1},
            produce={"glyceraldehyde_3_phosphate": 1},
        ),
        # Glyceraldehyde-3-phosphate + NAD+ + Pi → Bisphosphoglycerate + NADH + H+
        "glyceraldehyde_3_phosphate_dehydrogenase": Reaction(
            "Glyceraldehyde 3-Phosphate Dehydrogenase",
            enzymes["glyceraldehyde_3_phosphate_dehydrogenase"],
            consume={"glyceraldehyde_3_phosphate": 1, "nad": 1, "pi": 1},
            produce={"bisphosphoglycerate_1_3": 1, "nadh": 1, "h_plus": 1},
        ),
        # Bisphosphoglycerate → Phosphoglycerate
        "phosphoglycerate_kinase": Reaction(
            "Phosphoglycerate Kinase",
            enzymes["phosphoglycerate_kinase"],
            consume={"bisphosphoglycerate_1_3": 1, "adp": 1},
            produce={"phosphoglycerate_3": 1, "atp": 1},
        ),
        # Phosphoglycerate → Phosphoglycerate
        "phosphoglycerate_mutase": Reaction(
            "Phosphoglycerate Mutase",
            enzymes["phosphoglycerate_mutase"],
            consume={"phosphoglycerate_3": 1},
            produce={"phosphoglycerate_2": 1},
        ),
        # Phosphoglycerate → Phosphoenolpyruvate + H2O
        "enolase": Reaction(
            "Enolase",
            enzymes["enolase"],
            consume={"phosphoglycerate_2": 1},
            produce={"phosphoenolpyruvate": 1, "h2o": 1},
        ),
        # Phosphoenolpyruvate + ADP → Pyruvate + ATP
        "pyruvate_kinase": Reaction(
            "Pyruvate Kinase",
            enzymes["pyruvate_kinase"],
            consume={"phosphoenolpyruvate": 1, "adp": 1},
            produce={"pyruvate": 1, "atp": 1},
        ),
    }

    @classmethod
    def perform(cls, organelle, glucose_units: float) -> float:
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
        if glucose_units < 0:
            raise GlycolysisError("The number of glucose units cannot be negative.")
        if glucose_units == 0:
            return 0

        try:
            # Check if there's enough glucose before starting the process
            if not organelle.is_metabolite_available("glucose", glucose_units):
                raise MetaboliteError(
                    f"Insufficient glucose. Required: {glucose_units}, Available: {organelle.get_metabolite_quantity('glucose')}"
                )

            # Now consume the glucose
            organelle.consume_metabolites(glucose=glucose_units)

            for _ in range(glucose_units):
                cls.investment_phase(organelle)
                cls.yield_phase(organelle)

                # Adjust net ATP gain
                organelle.produce_metabolites(atp=2)

            logger.info(f"Glycolysis completed. Produced {organelle.get_metabolite_quantity('pyruvate')} pyruvate.")
            return organelle.get_metabolite_quantity("pyruvate")
        except MetaboliteError as e:
            raise GlycolysisError(f"Glycolysis failed: {str(e)}")

    @classmethod
    def investment_phase(cls, organelle):
        """
        Perform the investment phase of glycolysis (steps 1-5).
        """
        logger.info("Performing investment phase.")
        # Steps 1-4 occur once per glucose molecule
        for step in list(GlycolysisSteps)[:4]:
            cls.reactions[step.value].execute(organelle, cls.time_step)

        # Step 5 occurs once to convert DHAP to G3P
        cls.reactions[GlycolysisSteps.TRIOSE_PHOSPHATE_ISOMERASE.value].execute(
            organelle, cls.time_step
        )

    @classmethod
    def yield_phase(cls, organelle):
        """
        Perform the yield phase of glycolysis (steps 6-10, twice).
        """
        logger.info("Performing yield phase.")
        # Steps 6-10 occur twice per glucose molecule
        for _ in range(2):
            for step in list(GlycolysisSteps)[5:]:
                cls.reactions[step.value].execute(organelle, cls.time_step)
