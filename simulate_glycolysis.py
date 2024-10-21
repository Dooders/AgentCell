import logging

from pyology.cell import Cell
from pyology.glycolysis import Glycolysis
from pyology.reporter import Reporter
from utils.command_data import CommandData
from utils.tracking import execute_command


class GlycolysisSimulation:
    def __init__(self, cell: "Cell", debug=True):
        self.cell = cell
        self.debug = debug

    def run(self, glucose_units: float, logger: logging.Logger):
        logger.info("Starting glycolysis simulation")
        # Investment phase
        investment_command = CommandData(
            obj=self.cell,
            command=Glycolysis.investment_phase,
            tracked_attributes=["ATP", "ADP", "AMP", "glucose"],
            args=(glucose_units, logger),
        )

        execute_command(investment_command, logger=logger)

        # Yield phase
        yield_command = CommandData(
            obj=self.cell,
            command=Glycolysis.yield_phase,
            tracked_attributes=["ATP", "ADP", "AMP"],
            args=(glucose_units * 2, logger),
        )
        execute_command(yield_command, logger=logger)


reporter = Reporter()
reporter.logger.setLevel(logging.DEBUG)  # Add this line
cell = Cell(logger=reporter)
sim_controller = GlycolysisSimulation(cell, debug=True)
sim_controller.run(4, logger=reporter)
