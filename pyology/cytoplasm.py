import logging

from .glycolysis import GlycolysisPathway
from .organelle import Organelle

logger = logging.getLogger(__name__)


class Cytoplasm(Organelle):
    """
    The cytoplasm is the fluid-filled space inside the cell that contains the
    cell's organelles and performs many of the cell's metabolic functions.

    Attributes:
        glycolysis_rate (float): The rate at which glucose is processed during glycolysis.
    """

    name = "Cytoplasm"

    def __init__(self):
        super().__init__()

    def glycolysis(self, glucose_consumed):
        """
        Perform glycolysis on the specified amount of glucose.

        Returns
        -------
        float
            The amount of pyruvate produced.
        """
        return GlycolysisPathway.perform(self, glucose_consumed)

    def reset(self) -> None:
        self.__init__()

    def get_metabolite_quantity(self, metabolite_name: str) -> int:
        """
        Get the quantity of a specific metabolite.
        """
        if metabolite_name in self.metabolites:
            return self.metabolites[metabolite_name].quantity
        else:
            raise ValueError(f"Unknown metabolite: {metabolite_name}")
