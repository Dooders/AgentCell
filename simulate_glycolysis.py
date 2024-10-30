import logging

from pyology.cell import Cell
from pyology.energy_calculations import calculate_energy_state
from pyology.glycolysis import Glycolysis
from pyology.reporter import Reporter

metabolites_list = [
    "glucose",
    "glucose-6-phosphate",
    "fructose-6-phosphate",
    "fructose-1-6-bisphosphate",
    "dihydroxyacetone-phosphate",
    "glyceraldehyde-3-phosphate",
    "1-3-bisphosphoglycerate",
    "3-phosphoglycerate",
    "2-phosphoglycerate",
    "phosphoenolpyruvate",
    "pyruvate",
    "ATP",
    "ADP",
    "AMP",
    "NADH",
    "NAD+",
    "Pi",
    "H2O",
]


class GlycolysisSimulation:
    def __init__(self, cell: "Cell", debug=True):
        self.cell = cell
        self.debug = debug

    def run(self, glucose_units: float, logger: logging.Logger):
        logger.info("Starting glycolysis simulation")
        self.cell.set_metabolite_quantity("glucose", glucose_units)
        initial_state = self.cell.metabolites.state()

        glycolysis = Glycolysis()
        result = glycolysis.run(self.cell, glucose_units, logger)
        final_state = self.cell.metabolites.state()
        logger.info(f"Glycolysis simulation completed")

        # log each metabolite that changed with the amount it changed
        # for metabolite, initial_value in initial_state.items():
        #     final_value = final_state[metabolite]
        #     if initial_value["quantity"] != final_value["quantity"]:
        #         logger.info(
        #             f"{metabolite}: {final_value['quantity'] - initial_value['quantity']}"
        #         )

        return result, initial_state, final_state


reporter = Reporter()
reporter.logger.setLevel(logging.DEBUG)  # Add this line
cell = Cell(metabolites_list, logger=reporter)
sim_controller = GlycolysisSimulation(cell, debug=True)
result, initial_state, final_state = sim_controller.run(1, logger=reporter)
reporter.info(f"----------------- Starting Analysis and Validation -----------------")


def validate_energy_balance(initial_state, final_state):
    initial_energy = calculate_energy_state(initial_state, logger=reporter)
    final_energy = calculate_energy_state(final_state, logger=reporter)
    print(f"Initial energy: {initial_energy}, Final energy: {final_energy}")
    return initial_energy == final_energy


print(validate_energy_balance(initial_state, final_state))


def validate_mass_balance(initial_state, final_state):
    pass
