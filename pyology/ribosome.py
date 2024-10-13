"""
Biological Background
Structure: 
    Composed of ribosomal RNA (rRNA) and proteins; 
    consists of large and small subunits.
Function: 
    Translates mRNA into polypeptide chains (proteins).
Modeling Considerations
    Translation Process:
        Simulate initiation, elongation, and termination phases.
    Incorporate tRNA selection, codon-anticodon pairing.
    Error Checking:
        Model fidelity mechanisms to prevent translation errors.
"""

from organelle import Organelle


class Ribosome(Organelle):
    name = "Ribosome"
    """
    Represents a ribosome, which translates mRNA into proteins.

    Methods
    -------
    translate_mrna : function
        Simulates the translation of mRNA into a protein.
    codon_to_amino_acid : function
        Simplified codon table to translate codons into amino acids.
    """

    def __init__(self) -> None:
        super().__init__("Ribosome")

    def translate_mrna(self, mrna):
        """
        Simulates the translation of mRNA into a protein.
        """
        print(f"Initiating translation of {mrna}")
        # Simplify mRNA sequence to codons
        codons: list[str] = [mrna[i : i + 3] for i in range(0, len(mrna), 3)]
        protein_sequence: str = ""
        for codon in codons:
            amino_acid: str = self.codon_to_amino_acid(codon)
            protein_sequence += amino_acid
        protein: str = f"Protein: {protein_sequence}"
        print(f"Translation completed: {protein}")
        return protein

    def codon_to_amino_acid(self, codon: str) -> str:
        """
        Simplified codon table
        """
        codon_table: dict[str, str] = {
            "AUG": "M",  # Start codon (Methionine)
            "UUU": "F",
            "UAA": "*",  # Stop codon
            # Add more codons as needed
        }
        return codon_table.get(codon, "X")  # 'X' for unknown codon
