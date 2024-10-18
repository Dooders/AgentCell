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
    cell.cytoplasm.metabolites["glucose"].initial_quantity = glucose
    reporter.log_event(f"\nSimulating ATP production with {glucose} glucose units:")
    initial_glucose = cell.metabolites["glucose"].quantity
    initial_atp = cell.cytoplasm.metabolites["ATP"].quantity
    initial_adp = cell.metabolites["ADP"].quantity
    initial_amp = cell.metabolites["AMP"].quantity

    reporter.log_event("Initial Metabolite Levels:")
    reporter.log_event(f"ATP: {initial_atp:.2f}")
    reporter.log_event(f"ADP: {initial_adp:.2f}")
    reporter.log_event(f"AMP: {initial_amp:.2f}")

    results = sim_controller.run_simulation(glucose)

    reporter.log_event("\nAdenine Nucleotide Balance:")
    reporter.log_event(
        f"Initial: ATP: {initial_atp}, ADP: {initial_adp}, AMP: {initial_amp}"
    )
    reporter.log_event(
        f"Final: ATP: {results['final_cytoplasm_atp'] + results['final_mitochondrion_atp']:.2f}, "
        f"ADP: {cell.metabolites['ADP'].quantity:.2f}, "
        f"AMP: {cell.metabolites['AMP'].quantity:.2f}"
    )

    total_initial = initial_atp + initial_adp + initial_amp
    total_final = (
        results["final_cytoplasm_atp"]
        + results["final_mitochondrion_atp"]
        + cell.metabolites["ADP"].quantity
        + cell.metabolites["AMP"].quantity
    )

    reporter.log_event(f"Total Initial Adenine Nucleotides: {total_initial:.2f}")
    reporter.log_event(f"Total Final Adenine Nucleotides: {total_final:.2f}")
    reporter.log_event(f"Difference: {total_final - total_initial:.2f}")

    sim_controller.reset()

reporter.log_event("Simulation complete.")
