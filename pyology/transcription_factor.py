"""
Class representing a transcription factor.
"""


class TranscriptionFactor:
    """
    Represents a transcription factor.

    Parameters
    ----------
    name : str
        The name of the transcription factor.
    effect : float
        The effect of the transcription factor on gene expression.
    """

    def __init__(self, name: str, effect: float) -> None:
        self.name = name
        self.effect = effect  # Multiplier on gene expression (e.g., 0.5 for repression, 2.0 for activation)
