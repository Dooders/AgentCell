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

    def __init__(self):
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

    def glycolysis(self, glucose_amount):
        """
        Perform glycolysis on the given amount of glucose.
        Returns the amount of pyruvate produced.
        """
        if self.metabolites["glucose"].quantity < glucose_amount:
            glucose_amount = self.metabolites["glucose"].quantity

        self.metabolites["glucose"].quantity -= glucose_amount
        pyruvate_produced = glucose_amount * 2  # Each glucose molecule produces 2 pyruvate molecules

        # Update other metabolites involved in glycolysis
        self.metabolites["atp"].quantity += glucose_amount * 2  # Net gain of 2 ATP per glucose
        self.metabolites["nadh"].quantity += glucose_amount * 2  # 2 NADH produced per glucose
        self.metabolites["adp"].quantity -= glucose_amount * 2  # 2 ADP consumed per glucose

        return pyruvate_produced

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
