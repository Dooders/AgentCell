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
        self.add_metabolite("glucose", 100, 1000)
        self.add_metabolite("atp", 100, 1000)
        self.add_metabolite("adp", 100, 1000)
        self.add_metabolite("amp", 100, 1000)
        self.add_metabolite("nad", 100, 1000)
        self.add_metabolite("nadh", 100, 1000)
        self.add_metabolite("glucose_6_phosphate", 100, 1000)
        self.add_metabolite("fructose_6_phosphate", 100, 1000)
        self.add_metabolite("fructose_1_6_bisphosphate", 100, 1000)
        self.add_metabolite("glyceraldehyde_3_phosphate", 100, 1000)
        self.add_metabolite("dihydroxyacetone_phosphate", 100, 1000)
        self.add_metabolite("bisphosphoglycerate_1_3", 100, 1000)
        self.add_metabolite("phosphoglycerate_3", 100, 1000)
        self.add_metabolite("phosphoglycerate_2", 100, 1000)
        self.add_metabolite("phosphoenolpyruvate", 100, 1000)
        self.add_metabolite("pyruvate", 100, 1000)
        self.add_metabolite("pi", 1000, 10000)
        self.add_metabolite("h_plus", 100, 1000)  # Add H+ (proton) metabolite
        self.add_metabolite("h2o", 1000, 10000)  # Add H2O (water) metabolite

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
