from typing import Dict

from .reaction import Reaction


class Pathway:
    def __init__(self, name: str):
        """
        Initializes a Pathway instance.

        Args:
            name (str): Name of the pathway.
        """
        self.name = name
        self.reactions = []

    def add_reaction(self, reaction: Reaction):
        """
        Adds a Reaction to the pathway.

        Args:
            reaction (Reaction): The reaction to add.
        """
        self.reactions.append(reaction)
        print(f"Added reaction '{reaction.name}' to pathway '{self.name}'.")

    def execute(self, metabolites: Dict[str, float]) -> None:
        """
        Executes all reactions in the pathway sequentially.

        Args:
            metabolites (dict): Dictionary of metabolite concentrations.
        """
        print(f"\nExecuting Pathway: {self.name}")
        for reaction in self.reactions:
            # Assuming forward direction for glycolysis
            reaction.execute(metabolites, direction="forward")


# # Define reactions involved in Glycolysis

# # 1. Hexokinase
# hexokinase = Reaction(
#     name="Hexokinase",
#     substrates={"Glucose": 1, "ATP": 1},
#     products={"Glucose-6-Phosphate": 1, "ADP": 1},
# )

# # 2. Phosphoglucose Isomerase
# phosphoglucose_isomerase = Reaction(
#     name="Phosphoglucose Isomerase",
#     substrates={"Glucose-6-Phosphate": 1},
#     products={"Fructose-6-Phosphate": 1},
#     reversible=True,
# )

# # 3. Phosphofructokinase-1 (PFK-1)
# phosphofructokinase = Reaction(
#     name="Phosphofructokinase-1",
#     substrates={"Fructose-6-Phosphate": 1, "ATP": 1},
#     products={"Fructose-1,6-Bisphosphate": 1, "ADP": 1},
# )

# # 4. Aldolase
# aldolase = Reaction(
#     name="Aldolase",
#     substrates={"Fructose-1,6-Bisphosphate": 1},
#     products={"Dihydroxyacetone Phosphate": 1, "Glyceraldehyde-3-Phosphate": 1},
#     reversible=True,
# )

# # 5. Triose Phosphate Isomerase
# triose_phosphate_isomerase = Reaction(
#     name="Triose Phosphate Isomerase",
#     substrates={"Dihydroxyacetone Phosphate": 1},
#     products={"Glyceraldehyde-3-Phosphate": 1},
#     reversible=True,
# )

# # 6. Glyceraldehyde-3-Phosphate Dehydrogenase
# glyceraldehyde_3_phosphate_dehydrogenase = Reaction(
#     name="Glyceraldehyde-3-Phosphate Dehydrogenase",
#     substrates={"Glyceraldehyde-3-Phosphate": 1, "NAD+": 1, "Pi": 1},
#     products={"1,3-Bisphosphoglycerate": 1, "NADH": 1, "H+": 1},
# )

# # 7. Phosphoglycerate Kinase
# phosphoglycerate_kinase = Reaction(
#     name="Phosphoglycerate Kinase",
#     substrates={"1,3-Bisphosphoglycerate": 1, "ADP": 1},
#     products={"3-Phosphoglycerate": 1, "ATP": 1},
# )

# # 8. Phosphoglycerate Mutase
# phosphoglycerate_mutase = Reaction(
#     name="Phosphoglycerate Mutase",
#     substrates={"3-Phosphoglycerate": 1},
#     products={"2-Phosphoglycerate": 1},
#     reversible=True,
# )

# # 9. Enolase
# enolase = Reaction(
#     name="Enolase",
#     substrates={"2-Phosphoglycerate": 1},
#     products={"Phosphoenolpyruvate": 1, "H2O": 1},
# )

# # 10. Pyruvate Kinase
# pyruvate_kinase = Reaction(
#     name="Pyruvate Kinase",
#     substrates={"Phosphoenolpyruvate": 1, "ADP": 1},
#     products={"Pyruvate": 1, "ATP": 1},
# )
