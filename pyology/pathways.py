import math
from typing import Dict

from .enzymes import Enzyme
from .exceptions import GlycolysisError, MetaboliteError
from .mitochondrion import GlycolysisSteps
from .reaction import Reaction


class GlycolysisPathway:
    """
    Class representing the glycolysis pathway.
    """

    def __init__(self, organelle):
        self.organelle = organelle
        self.define_enzymes()
        self.define_reactions()
        self.time_step = 0.1  # Default time step in seconds

    def define_enzymes(self):
        """Define enzymes for each step of glycolysis."""
        self.enzymes = {
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
            "phosphoglycerate_kinase": Enzyme(
                "Phosphoglycerate Kinase", vmax=9.0, km=0.2
            ),
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

    def define_reactions(self):
        """Define reactions for each step of glycolysis."""
        self.reactions = {
            "hexokinase": Reaction(
                "Hexokinase",
                self.enzymes["hexokinase"],
                consume={"glucose": 1, "atp": 1},
                produce={"glucose_6_phosphate": 1, "adp": 1},
            ),
            "phosphoglucose_isomerase": Reaction(
                "Phosphoglucose Isomerase",
                self.enzymes["phosphoglucose_isomerase"],
                consume={"glucose_6_phosphate": 1},
                produce={"fructose_6_phosphate": 1},
            ),
            "phosphofructokinase": Reaction(
                "Phosphofructokinase",
                self.enzymes["phosphofructokinase"],
                consume={"fructose_6_phosphate": 1, "atp": 1},
                produce={"fructose_1_6_bisphosphate": 1, "adp": 1},
            ),
            "aldolase": Reaction(
                "Aldolase",
                self.enzymes["aldolase"],
                consume={"fructose_1_6_bisphosphate": 1},
                produce={
                    "glyceraldehyde_3_phosphate": 1,
                    "dihydroxyacetone_phosphate": 1,
                },
            ),
            "triose_phosphate_isomerase": Reaction(
                "Triose Phosphate Isomerase",
                self.enzymes["triose_phosphate_isomerase"],
                consume={"dihydroxyacetone_phosphate": 1},
                produce={"glyceraldehyde_3_phosphate": 1},
            ),
            "glyceraldehyde_3_phosphate_dehydrogenase": Reaction(
                "Glyceraldehyde 3-Phosphate Dehydrogenase",
                self.enzymes["glyceraldehyde_3_phosphate_dehydrogenase"],
                consume={"glyceraldehyde_3_phosphate": 1, "nad": 1, "pi": 1},
                produce={"bisphosphoglycerate_1_3": 1, "nadh": 1, "h_plus": 1},
            ),
            "phosphoglycerate_kinase": Reaction(
                "Phosphoglycerate Kinase",
                self.enzymes["phosphoglycerate_kinase"],
                consume={"bisphosphoglycerate_1_3": 1, "adp": 1},
                produce={"phosphoglycerate_3": 1, "atp": 1},
            ),
            "phosphoglycerate_mutase": Reaction(
                "Phosphoglycerate Mutase",
                self.enzymes["phosphoglycerate_mutase"],
                consume={"phosphoglycerate_3": 1},
                produce={"phosphoglycerate_2": 1},
            ),
            "enolase": Reaction(
                "Enolase",
                self.enzymes["enolase"],
                consume={"phosphoglycerate_2": 1},
                produce={"phosphoenolpyruvate": 1, "h2o": 1},
            ),
            "pyruvate_kinase": Reaction(
                "Pyruvate Kinase",
                self.enzymes["pyruvate_kinase"],
                consume={"phosphoenolpyruvate": 1, "adp": 1},
                produce={"pyruvate": 1, "atp": 1},
            ),
        }

    def glycolysis(self, glucose_units: float) -> float:
        """
        Perform glycolysis on the given number of glucose units.

        Glycolysis is the process by which glucose is converted into pyruvate,
        releasing energy in the form of ATP.

        Parameters
        ----------
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
        glucose_units = math.floor(glucose_units)
        if glucose_units < 0:
            raise GlycolysisError("The number of glucose units cannot be negative.")
        if glucose_units == 0:
            return 0

        try:
            # Check if there's enough glucose before starting the process
            if not self.organelle.is_metabolite_available("glucose", glucose_units):
                raise MetaboliteError(
                    f"Insufficient glucose. Required: {glucose_units}, Available: {self.organelle.get_metabolite_quantity('glucose')}"
                )

            # Now consume the glucose
            self.organelle.consume_metabolites(glucose=glucose_units)

            for _ in range(glucose_units):
                # Steps 1-4 occur once per glucose molecule
                for step in list(GlycolysisSteps)[:4]:
                    self.reactions[step.value].execute(self.organelle, self.time_step)

                # Step 5 occurs once to convert DHAP to G3P
                self.reactions[
                    GlycolysisSteps.TRIOSE_PHOSPHATE_ISOMERASE.value
                ].execute(self.organelle, self.time_step)

                # Steps 6-10 occur twice per glucose molecule
                for _ in range(2):
                    for step in list(GlycolysisSteps)[5:]:
                        self.reactions[step.value].execute(
                            self.organelle, self.time_step
                        )

                # Adjust net ATP gain
                self.organelle.produce_metabolites(atp=2)

            return self.organelle.get_metabolite_quantity("pyruvate")
        except MetaboliteError as e:
            raise GlycolysisError(f"Glycolysis failed: {str(e)}")
