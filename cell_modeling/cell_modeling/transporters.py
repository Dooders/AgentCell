"""
A transporter is a protein that moves substances across the cell membrane.
"""


class Transporter:
    """
    Represents a transporter that moves substances across the cell membrane.

    Parameters
    ----------
    substance : str
        The substance to be transported.
    energy_required : bool, optional
        Whether the transport requires energy, by default False.

    Methods
    -------
    transport : function
        Initiates the transport of the substance across the cell membrane.
    """

    def __init__(self, substance: str, energy_required: bool = False) -> None:
        self.substance = substance
        self.energy_required = energy_required

    def transport(self) -> None:
        """
        Initiates the transport of the substance across the cell membrane.
        """
        if self.energy_required:
            print(f"Active transport of {self.substance} initiated.")
        else:
            print(f"Passive transport of {self.substance} initiated.")
