import logging

from pyology.cell import Cell
from pyology.simulation import SimulationController, Reporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

cell = Cell()
reporter = Reporter()
sim_controller = SimulationController(cell, reporter)
glucose_amounts = [4]

for glucose in glucose_amounts:
    reporter.log_event(f"\nSimulating ATP production with {glucose} glucose units:")
    results = sim_controller.run_simulation(glucose)
    sim_controller.reset()

reporter.log_event("Simulation complete.")
