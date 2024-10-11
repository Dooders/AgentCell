"""
Nucleus
Biological Background   
Structure: 
    Enclosed by a nuclear envelope with pores; 
    contains chromatin (DNA + proteins).
Function:
    Genetic Information Storage: Houses DNA organized into chromosomes.
    Transcription: DNA is transcribed into mRNA.
    DNA Replication: DNA duplicates during the cell cycle.
Modeling Considerations
    DNA Representation:
        Model DNA sequences, genes, promoters, enhancers.
    Gene Regulation:
        Include transcription factors, repressors, and activators.
    Transcription Process:
        Simulate RNA polymerase activity, mRNA synthesis.
"""

from organelle import Organelle


class Nucleus(Organelle):
    """
    Represents the nucleus, which houses DNA organized into chromosomes.

    Parameters
    ----------
    genes : list["Gene"]
        The genes in the nucleus.

    Methods
    -------
    replicate_dna : function
        Simulates the DNA replication process.
    transcribe_dna : function
        Simulates the transcription of DNA into mRNA.
    """

    def __init__(self, genes: list["Gene"]) -> None:
        super().__init__("Nucleus")
        self.genes: dict[str, "Gene"] = {gene.name: gene for gene in genes}

    def replicate_dna(self) -> None:
        """
        Simulates the DNA replication process.
        """
        print("DNA replication in progress...")
        # Logic for DNA replication (e.g., copying gene sequences)

    def transcribe_dna(self, gene_name: str) -> str | None:
        """
        Simulates the transcription of DNA into mRNA.
        """
        gene: Gene | None = self.genes.get(gene_name)
        if gene:
            expression_level: float = gene.get_expression_level()
            print(f"Transcribing {gene_name} at expression level: {expression_level}")
            # Simulate mRNA synthesis proportional to expression level
            mrna: str = f"mRNA of {gene_name}"
            return mrna
        else:
            print(f"Gene {gene_name} not found.")
            return None
