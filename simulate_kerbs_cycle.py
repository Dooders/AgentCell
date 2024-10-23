import logging

from pyology.cell import Cell
from pyology.krebs_cycle import KrebsCycle
from pyology.reporter import Reporter
from utils.command_data import CommandData
from utils.tracking import execute_command


class KrebsCycleSimulation:
    def __init__(self, cell: "Cell", debug=True):
        self.cell = cell
        self.debug = debug

    def run(self, acetyl_coa_units: float, logger: logging.Logger):
        logger.info("Starting Krebs Cycle simulation")
        self.cell.set_metabolite_quantity("Acetyl_CoA", acetyl_coa_units)

        krebs_cycle_command = CommandData(
            obj=KrebsCycle(),
            command=KrebsCycle.run,
            tracked_attributes=[
                "ATP",
                "ADP",
                "AMP",
                "Acetyl_CoA",
                "NAD",
                "NADH",
                "FAD",
                "FADH2",
                "CO2",
            ],
            args=(self.cell, acetyl_coa_units, logger),
            kwargs={},
        )

        execute_command(self.cell, krebs_cycle_command, logger=logger)


reporter = Reporter()
reporter.logger.setLevel(logging.DEBUG)
cell = Cell(logger=reporter)
sim_controller = KrebsCycleSimulation(cell, debug=True)
sim_controller.run(4, logger=reporter)
