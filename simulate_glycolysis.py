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
        logger.info(f"Initial State: {self.cell.metabolites.state}")
        self.cell.set_metabolite_quantity("glucose", glucose_units)

        glycolysis = Glycolysis()
        result = glycolysis.run(self.cell, glucose_units, logger)
        logger.info(f"Final State: {self.cell.metabolites.state}")
        logger.info(f"Glycolysis simulation completed, result: {result}")

reporter = Reporter()
reporter.logger.setLevel(logging.DEBUG)  # Add this line
cell = Cell(logger=reporter)
sim_controller = GlycolysisSimulation(cell, debug=True)
sim_controller.run(4, logger=reporter)
