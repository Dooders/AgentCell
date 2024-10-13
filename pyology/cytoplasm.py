import logging

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

    def glycolysis(self, glucose_consumed):
        """
        Perform glycolysis on the specified amount of glucose.
        Returns the amount of pyruvate produced.
        """
        # Ensure we don't consume more glucose than available
        glucose_consumed = min(glucose_consumed, self.metabolites["glucose"].quantity)

        # Glycolysis stoichiometry
        # 1 Glucose -> 2 Pyruvate + 2 ATP + 2 NADH
        pyruvate_produced = 2 * glucose_consumed
        atp_produced = 2 * glucose_consumed
        nadh_produced = 2 * glucose_consumed

        # Update metabolite quantities
        self.metabolites["glucose"].quantity -= glucose_consumed
        self.metabolites["pyruvate"].quantity += pyruvate_produced
        self.metabolites["atp"].quantity += atp_produced
        self.metabolites["nadh"].quantity += nadh_produced

        # ADP is consumed to produce ATP
        adp_consumed = atp_produced
        self.metabolites["adp"].quantity = max(
            0, self.metabolites["adp"].quantity - adp_consumed
        )

        logger.info(
            f"Glycolysis: {glucose_consumed} glucose -> {pyruvate_produced} pyruvate, {atp_produced} ATP, {nadh_produced} NADH"
        )

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
