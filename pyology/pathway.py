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
