from .glycolysis import GlycolysisPathway
from .organelle import Organelle


class Cytoplasm(Organelle):
    """
    The cytoplasm is the fluid-filled space inside the cell that contains the
    cell's organelles and performs many of the cell's metabolic functions.

    Attributes
    ----------
    glycolysis_rate (float): The rate at which glucose is processed during glycolysis.

    Methods
    -------
    glycolysis(self, glucose_consumed: float) -> float:
        Perform glycolysis on the specified amount of glucose.
    reset(self) -> None:
        Reset the cytoplasm to its initial state.
    """

    name = "Cytoplasm"

    def __init__(self):
        super().__init__()

    def glycolysis(self, glucose_consumed: float) -> float:
        """
        Perform glycolysis on the specified amount of glucose.

        Parameters
        ----------
        glucose_consumed : float
            The amount of glucose to consume.

        Returns
        -------
        float
            The amount of pyruvate produced.
        """
        return GlycolysisPathway.perform(self, glucose_consumed)

    def reset(self) -> None:
        self.__init__()
