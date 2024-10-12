import logging

from cell_modeling.organelles.cell import Cell
from cell_modeling.organelles.simulation import (
    Reporter,
    SimulationController,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

cell = Cell()
reporter = Reporter()
sim_controller = SimulationController(cell, reporter)
glucose_amounts = [1, 2, 5, 10]

for glucose in glucose_amounts:
    reporter.log_event(f"\nSimulating ATP production with {glucose} glucose units:")
    results = sim_controller.run_simulation(glucose)

    # Reset the cell for the next simulation
    cell.reset()

reporter.log_event("Simulation complete.")
