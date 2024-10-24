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
        self.krebs_cycle = KrebsCycle(debug=debug)

    def run(self, acetyl_coa_units: float, logger: logging.Logger):
        logger.info("Starting Krebs Cycle simulation")
        self.cell.set_metabolite_quantity("Acetyl_CoA", acetyl_coa_units)

        logger.info(
            f"Initial metabolite levels: {self.cell.metabolites.quantities}"
        )

        # Add initial quantities for essential metabolites
        essential_metabolites = {
            "FAD": 10,
            "NAD+": 10,
            "CoA": 10,
            "ADP": 10,
            "Pi": 10,
            "Oxaloacetate": 10,
            "Succinate": 10,
            "α_Ketoglutarate": 10,
        }

        for metabolite, quantity in essential_metabolites.items():
            current_quantity = self.cell.get_metabolite_quantity(metabolite)
            if current_quantity < quantity:
                self.cell.set_metabolite_quantity(metabolite, quantity)
            logger.info(
                f"Initial {metabolite} quantity: {self.cell.get_metabolite_quantity(metabolite)}"
            )

        try:
            results = self.krebs_cycle.run(self.cell, acetyl_coa_units, logger)
            logger.info(f"Krebs Cycle results: {results}")
        except Exception as e:
            logger.error(f"Error during Krebs Cycle simulation: {str(e)}")
            raise


reporter = Reporter()
reporter.logger.setLevel(logging.DEBUG)
cell = Cell(logger=reporter)
sim_controller = KrebsCycleSimulation(cell, debug=True)
sim_controller.run(4, logger=reporter)
