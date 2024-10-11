"""
Class representing a cell.
"""

from cell_membrane import CellMembrane
from cytoplasm import Cytoplasm
from cytoskeleton import Cytoskeleton
from endoplasmic_reticulum import EndoplasmicReticulum
from golgi_apparatus import GolgiApparatus
from lysosome import Lysosome
from mitochondrion import Mitochondrion
from nucleus import Nucleus
from ribosome import Ribosome

# Import other necessary classes


class Cell:
    """
    Represents a cell.

    Methods
    -------
    metabolize_glucose : function
        Simulates the metabolism of glucose.
    synthesize_protein : function
        Simulates the synthesis of a protein.
    perform_functions : function
        Simulates additional cell functions.
    """

    def __init__(self) -> None:
        # Initialize organelles
        self.nucleus: Nucleus = Nucleus(genes=[])
        self.mitochondria: list[Mitochondrion] = [Mitochondrion() for _ in range(10)]
        self.ribosomes: list[Ribosome] = [Ribosome() for _ in range(1000)]
        self.endoplasmic_reticulum: EndoplasmicReticulum = EndoplasmicReticulum()
        self.golgi_apparatus: GolgiApparatus = GolgiApparatus()
        self.lysosomes: list[Lysosome] = [Lysosome() for _ in range(5)]
        self.cytoskeleton: Cytoskeleton = Cytoskeleton()
        self.cytoplasm: Cytoplasm = Cytoplasm()
        self.cell_membrane: CellMembrane = CellMembrane()
        self.energy: int = 0  # ATP

    def metabolize_glucose(self, glucose_amount: int) -> None:
        """
        Simulates the metabolism of glucose.
        """
        print(f"Cell is metabolizing {glucose_amount} units of glucose")
        glucose_per_mitochondrion: int = glucose_amount / len(self.mitochondria)
        for mitochondrion in self.mitochondria:
            atp: int = mitochondrion.produce_atp(glucose_per_mitochondrion)
            self.energy += atp
        print(f"Total energy (ATP): {self.energy}")

    def synthesize_protein(self, gene_name: str) -> None:
        """
        Simulates the synthesis of a protein from a given gene.
        """
        print(f"Cell is synthesizing protein from gene: {gene_name}")
        mrna: str | None = self.nucleus.transcribe_dna(gene_name)
        if mrna:
            protein = self.ribosomes[0].translate_mrna(mrna)
            # Process protein in ER and Golgi
            protein_er: str = self.endoplasmic_reticulum.synthesize_protein(protein)
            self.golgi_apparatus.receive_protein(protein_er)
            sorted_cargo: dict[str, list[str]] = self.golgi_apparatus.modify_and_sort()
            # Update cytoplasm or export proteins
            for destination, proteins in sorted_cargo.items():
                if destination == "Cytoplasm":
                    for protein in proteins:
                        self.cytoplasm.add_molecule(protein)
                elif destination == "Plasma Membrane":
                    for protein in proteins:
                        self.cell_membrane.add_receptor(protein)
            print(f"Protein {protein} synthesized and sorted")

    def perform_functions(self) -> None:
        # Define additional cell functions
        pass
