from .organelle import Organelle
from .pathways import GlycolysisPathway


class Cytoplasm(Organelle):
    """
    The cytoplasm is the fluid-filled space inside the cell that contains the
    cell's organelles and performs many of the cell's metabolic functions.

    Attributes:
        glycolysis_rate (float): The rate at which glucose is processed during glycolysis.
    """

    name = "Cytoplasm"

    def __init__(self, glycolysis_rate: float = 1.0):
        super().__init__()
        self.add_metabolite("glucose", 100, 1000)
        self.add_metabolite("atp", 100, 1000)
        self.add_metabolite("adp", 100, 1000)
        self.add_metabolite("amp", 10, 1000)  # Added AMP
        self.add_metabolite("nad", 100, 1000)
        self.add_metabolite("nadh", 0, 1000)
        self.add_metabolite("glucose_6_phosphate", 0, 1000)
        self.add_metabolite("fructose_6_phosphate", 0, 1000)
        self.add_metabolite("fructose_1_6_bisphosphate", 0, 1000)
        self.add_metabolite("glyceraldehyde_3_phosphate", 0, 1000)
        self.add_metabolite("dihydroxyacetone_phosphate", 0, 1000)
        self.add_metabolite("bisphosphoglycerate_1_3", 0, 1000)
        self.add_metabolite("phosphoglycerate_3", 0, 1000)
        self.add_metabolite("phosphoglycerate_2", 0, 1000)
        self.add_metabolite("phosphoenolpyruvate", 0, 1000)
        self.add_metabolite("pyruvate", 0, 1000)
        self.add_metabolite("pi", 1000, 10000)
        self.add_metabolite("h_plus", 0, 1000)  # Add H+ (proton) metabolite
        self.add_metabolite("h2o", 1000, 10000)  # Add H2O (water) metabolite
        self.glycolysis_rate = glycolysis_rate
        self.glycolysis_pathway = GlycolysisPathway(self)

    def glycolysis(self, glucose_units: float) -> float:
        """
        Perform glycolysis on the given number of glucose units.

        Parameters
        ----------
        glucose_units : float
            The number of glucose units to process.

        Returns
        -------
        float
            The amount of pyruvate produced.
        """
        return self.glycolysis_pathway.glycolysis(glucose_units)

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
