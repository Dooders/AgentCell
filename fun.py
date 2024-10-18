import logging

from pyology.cell import Cell
from pyology.simulation import Reporter, SimulationController

logging.basicConfig(
    level=logging.DEBUG,  # Change this to DEBUG to see all log messages
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

cell = Cell()
reporter = Reporter()
sim_controller = SimulationController(cell, reporter)
glucose_amounts = [4]

for glucose in glucose_amounts:
    cell.cytoplasm.metabolites["glucose"].quantity = glucose
    reporter.log_event(f"\nSimulating ATP production with {glucose} glucose units:")
    initial_glucose = cell.metabolites["glucose"].quantity
    initial_atp = cell.metabolites["ATP"].quantity
    initial_adp = cell.metabolites["ADP"].quantity
    initial_amp = cell.metabolites["AMP"].quantity

    results = sim_controller.run_simulation(glucose)

    final_glucose = cell.metabolites["glucose"].quantity
    glucose_consumed = initial_glucose - final_glucose
    reporter.log_event(f"Glucose consumed: {glucose_consumed}")
    reporter.log_event(f"Pyruvate produced: {cell.metabolites['pyruvate'].quantity}")
    reporter.log_event(
        f"2-Phosphoglycerate remaining: {cell.metabolites['phosphoglycerate_2'].quantity}"
    )
    reporter.log_event(
        f"Phosphoenolpyruvate produced: {cell.metabolites['phosphoenolpyruvate'].quantity}"
    )

    reporter.log_event("\nAdenine Nucleotide Balance:")
    reporter.log_event(
        f"Initial: ATP: {initial_atp}, ADP: {initial_adp}, AMP: {initial_amp}"
    )
    reporter.log_event(
        f"Final: ATP: {cell.metabolites['ATP'].quantity}, "
        f"ADP: {cell.metabolites['ADP'].quantity}, "
        f"AMP: {cell.metabolites['AMP'].quantity}"
    )

    sim_controller.reset()

reporter.log_event("Simulation complete.")
