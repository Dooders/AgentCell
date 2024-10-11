"""
Biological Background
Structure: 
    Gel-like substance composed of water, salts, and organic molecules.
Function:
    Medium for Chemical Reactions: Site for many metabolic pathways.
    Supports Organelles: Provides a medium where organelles are suspended.
Modeling Considerations
    Reaction Medium:
        Simulate diffusion and interactions of molecules.
    Metabolic Pathways:
        Model pathways like glycolysis occurring in the cytoplasm.
"""


class Cytoplasm:
    """
    Represents the cytoplasm of a cell.

    Methods
    -------
    add_molecule : function
        Adds a molecule to the cytoplasm.
    remove_molecule : function
        Removes a molecule from the cytoplasm.
    simulate_reaction : function
        Simulates a chemical reaction in the cytoplasm.
    """

    def __init__(self) -> None:
        self.molecules = {}

    def add_molecule(self, molecule: str, quantity: int = 1) -> None:
        """
        Adds a molecule to the cytoplasm.
        """
        self.molecules[molecule] = self.molecules.get(molecule, 0) + quantity

    def remove_molecule(self, molecule: str, quantity: int = 1) -> None:
        """
        Removes a molecule from the cytoplasm.
        """
        if molecule in self.molecules and self.molecules[molecule] >= quantity:
            self.molecules[molecule] -= quantity
            if self.molecules[molecule] == 0:
                del self.molecules[molecule]
        else:
            print(f"Not enough {molecule} to remove.")

    def simulate_reaction(
        self, reactants: list[str], products: list[str], rate_constant: float
    ) -> None:
        """
        Simulates a chemical reaction in the cytoplasm.
        """
        print(f"Simulating reaction: {reactants} -> {products}")
        # Simplified reaction simulation
        for reactant in reactants:
            self.remove_molecule(reactant)
        for product in products:
            self.add_molecule(product)
