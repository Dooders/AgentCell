import logging

from pyology.cell import Cell
from pyology.glycolysis import Glycolysis
from pyology.reporter import Reporter


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
        logger.info(f"Glycolysis simulation completed, result: {result}")

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
cell = Cell(logger=reporter)
sim_controller = GlycolysisSimulation(cell, debug=True)
sim_controller.run(1, logger=reporter)
