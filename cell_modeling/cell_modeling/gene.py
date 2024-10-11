"""
Class representing a gene.
"""


class Gene:
    """
    Represents a gene with a name, sequence, expression level, and regulators.

    Parameters
    ----------
    name : str
        The name of the gene.
    sequence : str
        The sequence of the gene.
    expression_level : float, optional
        The basal expression level of the gene (default is 1.0).
    regulators : list["TranscriptionFactor"], optional
        The regulators of the gene (default is an empty list).

    Methods
    -------
    add_regulator : function
        Adds a regulator to the gene.
    get_expression_level : function
        Gets the expression level of the gene.
    """

    def __init__(self, name: str, sequence: str, expression_level: float = 1.0) -> None:
        self.name: str = name
        self.sequence: str = sequence
        self.expression_level: float = expression_level  # Basal expression level
        self.regulators: list["TranscriptionFactor"] = []  # List of regulatory proteins

    def add_regulator(self, regulator: "TranscriptionFactor") -> None:
        self.regulators.append(regulator)

    def get_expression_level(self) -> float:
        # Modify expression level based on regulators
        level = self.expression_level
        for regulator in self.regulators:
            level *= regulator.effect
        return level
