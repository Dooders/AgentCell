import logging

from .constants import (
    SIMULATION_DURATION,
    TIME_STEP,
)
from .exceptions import (
    InsufficientMetaboliteError,
    QuantityError,
    UnknownMetaboliteError,
)


class Reporter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def log_event(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

    def report_simulation_results(self, results):
        self.log_event(
            f"Simulation completed in {results['simulation_time']:.2f} seconds"
        )
        self.log_event(f"Total ATP produced: {results['total_atp_produced']:.2f}")
        self.log_event(f"Glucose processed: {results['glucose_processed']:.2f}")
        self.log_event(f"Oxygen remaining: {results['oxygen_remaining']:.2f}")
        self.log_event(f"Final cytoplasm ATP: {results['final_cytoplasm_atp']:.2f}")
        self.log_event(
            f"Final mitochondrion ATP: {results['final_mitochondrion_atp']:.2f}"
        )


class SimulationController:
    def __init__(self, cell, reporter, simulation_duration=SIMULATION_DURATION):
        self.cell = cell
        self.reporter = reporter
        self.simulation_duration = simulation_duration
        self.simulation_time = 0
        self.time_step = TIME_STEP

    def run_simulation(self, glucose_amount):
        self.reporter.log_event(
            f"Starting simulation with {glucose_amount} glucose units"
        )
        try:
            glucose_processed = 0
            total_atp_produced = 0
            initial_atp = (
                self.cell.cytoplasm.metabolites["atp"].quantity
                + self.cell.mitochondrion.metabolites["atp"].quantity
            )

            while (
                glucose_processed < glucose_amount
                and self.simulation_time < self.simulation_duration
            ):
                try:
                    if self.cell.mitochondrion.metabolites["oxygen"].quantity <= 0:
                        self.reporter.log_warning(
                            "Oxygen depleted. Stopping simulation."
                        )
                        break

                    # Check and handle ADP availability
                    self._handle_adp_availability()

                    # Implement feedback activation
                    self._apply_feedback_activation()

                    # Perform glycolysis
                    pyruvate = self.cell.cytoplasm.glycolysis(
                        int(1 * self.cell.cytoplasm.glycolysis_rate)
                    )
                    glucose_processed += round(
                        1 * self.cell.cytoplasm.glycolysis_rate, 2
                    )

                    # Calculate ATP produced in glycolysis
                    glycolysis_atp = (
                        self.cell.cytoplasm.metabolites["atp"].quantity
                        - initial_atp
                        + self.cell.mitochondrion.metabolites["atp"].quantity
                    )
                    total_atp_produced += glycolysis_atp

                    # Handle NADH shuttle
                    self._handle_nadh_shuttle()

                    # Perform cellular respiration
                    mitochondrial_atp = self.cell.mitochondrion.cellular_respiration(
                        pyruvate
                    )
                    total_atp_produced += mitochondrial_atp

                    # Transfer excess ATP from mitochondrion to cytoplasm
                    self._transfer_excess_atp()

                    self.simulation_time += self.time_step

                    if self.simulation_time % 10 == 0:
                        self._log_intermediate_state()

                except UnknownMetaboliteError as e:
                    self.reporter.log_error(f"Unknown metabolite error: {str(e)}")
                    self.reporter.log_warning("Skipping current simulation step.")
                    continue
                except InsufficientMetaboliteError as e:
                    self.reporter.log_error(f"Insufficient metabolite error: {str(e)}")
                    self.reporter.log_warning(
                        "Attempting to continue simulation with available metabolites."
                    )
                    continue
                except QuantityError as e:
                    self.reporter.log_error(f"Quantity error: {str(e)}")
                    self.reporter.log_warning(
                        "Adjusting quantities and continuing simulation."
                    )
                    continue

            # Return simulation results
            results = {
                "total_atp_produced": total_atp_produced,
                "glucose_processed": glucose_processed,
                "simulation_time": self.simulation_time,
                "oxygen_remaining": self.cell.mitochondrion.metabolites[
                    "oxygen"
                ].quantity,
                "final_cytoplasm_atp": self.cell.cytoplasm.metabolites["atp"].quantity,
                "final_mitochondrion_atp": self.cell.mitochondrion.metabolites[
                    "atp"
                ].quantity,
            }
            self.reporter.report_simulation_results(results)
            return results

        except Exception as e:
            self.reporter.log_error(f"Unhandled simulation error: {str(e)}")
            raise

    def _handle_adp_availability(self):
        if self.cell.mitochondrion.metabolites["adp"].quantity < 10:
            self.reporter.log_warning(
                "Low ADP levels in mitochondrion. Transferring ADP from cytoplasm."
            )
            adp_transfer = min(50, self.cell.cytoplasm.metabolites["adp"].quantity)
            self.cell.mitochondrion.metabolites["adp"].quantity += adp_transfer
            self.cell.cytoplasm.metabolites["adp"].quantity -= adp_transfer

    def _apply_feedback_activation(self):
        adp_activation_factor = (
            1 + self.cell.cytoplasm.metabolites["adp"].quantity / 500
        )
        self.cell.cytoplasm.glycolysis_rate *= adp_activation_factor

    def _handle_nadh_shuttle(self):
        cytoplasmic_nadh = self.cell.cytoplasm.metabolites["nadh"].quantity
        self.cell.mitochondrion.transfer_cytoplasmic_nadh(cytoplasmic_nadh)

    def _transfer_excess_atp(self):
        atp_transfer = max(0, self.cell.mitochondrion.metabolites["atp"].quantity - 100)
        self.cell.cytoplasm.metabolites["atp"].quantity += atp_transfer
        self.cell.mitochondrion.metabolites["atp"].quantity -= atp_transfer

    def _log_intermediate_state(self):
        state = self.get_current_state()
        self.reporter.log_event(f"Time: {state['simulation_time']:.2f} s")
        self.reporter.log_event(f"Glucose Processed: {state['glucose_processed']:.2f}")
        self.reporter.log_event(
            f"Total ATP Produced: {state['total_atp_produced']:.2f}"
        )
        self.reporter.log_event(f"Cytoplasm ATP: {state['cytoplasm_atp']:.2f}")
        self.reporter.log_event(f"Mitochondrion ATP: {state['mitochondrion_atp']:.2f}")
        self.reporter.log_event(f"Proton Gradient: {state['proton_gradient']:.2f}")
        self.reporter.log_event(f"Oxygen Remaining: {state['oxygen_remaining']:.2f}")

    def get_current_state(self):
        return {
            "simulation_time": self.simulation_time,
            "cytoplasm_atp": self.cell.cytoplasm.metabolites["atp"].quantity,
            "mitochondrion_atp": self.cell.mitochondrion.metabolites["atp"].quantity,
            "cytoplasm_nadh": self.cell.cytoplasm.metabolites["nadh"].quantity,
            "mitochondrion_nadh": self.cell.mitochondrion.metabolites["nadh"].quantity,
            "mitochondrion_fadh2": self.cell.mitochondrion.metabolites[
                "fadh2"
            ].quantity,
            "mitochondrial_calcium": self.cell.mitochondrion.metabolites[
                "calcium"
            ].quantity,
            "cytoplasmic_calcium": self.cell.cytoplasmic_calcium.quantity,
            "proton_gradient": self.cell.mitochondrion.proton_gradient,
            "oxygen_remaining": self.cell.mitochondrion.metabolites["oxygen"].quantity,
        }
