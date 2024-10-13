import logging

from .constants import SIMULATION_DURATION, TIME_STEP
from .cytoplasm import Cytoplasm
from .data import Metabolite
from .mitochondrion import KrebsCycle, Mitochondrion
from .organelle import Organelle

logger = logging.getLogger(__name__)


class Cell(Organelle):
    name = "Cell"
    def __init__(self):
        self.cytoplasm = Cytoplasm()
        # The Cytoplasm now initializes with some glucose, ATP, and ADP
        self.cytoplasm.add_metabolite("glucose", 10, 1000)  # Increase initial glucose
        self.mitochondrion = Mitochondrion()
        self.krebs_cycle = KrebsCycle()
        self.simulation_time = 0
        self.time_step = TIME_STEP
        self.cytoplasmic_calcium = Metabolite("Ca2+", 100, 1000)

    def produce_atp(self, glucose, simulation_duration=SIMULATION_DURATION):
        """Simulates ATP production in the entire cell over a specified duration."""
        initial_atp = (
            self.cytoplasm.metabolites["atp"].quantity
            + self.mitochondrion.metabolites["atp"].quantity
        )
        self.simulation_time = 0
        total_atp_produced = 0
        glucose_processed = 0

        while (
            glucose_processed < glucose and self.simulation_time < simulation_duration
        ):
            if self.mitochondrion.metabolites["oxygen"].quantity <= 0:
                logger.warning("Oxygen depleted. Stopping simulation.")
                break

            # Check ADP availability
            if (
                self.mitochondrion.metabolites["adp"].quantity < 10
            ):  # Arbitrary threshold
                logger.warning(
                    "Low ADP levels in mitochondrion. Transferring ADP from cytoplasm."
                )
                adp_transfer = min(
                    50, self.cytoplasm.metabolites["adp"].quantity
                )  # Transfer up to 50 ADP
                self.mitochondrion.metabolites["adp"].quantity += adp_transfer
                self.cytoplasm.metabolites["adp"].quantity -= adp_transfer

            # Implement feedback activation
            adp_activation_factor = (
                1 + self.cytoplasm.metabolites["adp"].quantity / 500
            )  # Example threshold
            self.cytoplasm.glycolysis_rate *= adp_activation_factor

            # Glycolysis with updated rate
            pyruvate = self.cytoplasm.glycolysis(1 * self.cytoplasm.glycolysis_rate)
            self.mitochondrion.add_metabolite("pyruvate", pyruvate)
            logger.info(f"Transferred {pyruvate} pyruvate to mitochondrion")
            glucose_processed += 1 * self.cytoplasm.glycolysis_rate

            # Calculate ATP produced in glycolysis
            glycolysis_atp = (
                self.cytoplasm.metabolites["atp"].quantity
                - initial_atp
                + self.mitochondrion.metabolites["atp"].quantity
            )
            total_atp_produced += glycolysis_atp

            cytoplasmic_nadh = self.cytoplasm.metabolites["nadh"].quantity

            # NADH shuttle
            mitochondrial_nadh = self.mitochondrion.transfer_cytoplasmic_nadh(
                cytoplasmic_nadh
            )

            # Cellular respiration in mitochondrion
            mitochondrial_atp = self.mitochondrion.cellular_respiration(pyruvate)
            total_atp_produced += mitochondrial_atp

            # Transfer excess ATP from mitochondrion to cytoplasm
            atp_transfer = max(
                0, self.mitochondrion.metabolites["atp"].quantity - 100
            )  # Keep 100 ATP in mitochondrion
            self.cytoplasm.metabolites["atp"].quantity += atp_transfer
            self.mitochondrion.metabolites["atp"].quantity -= atp_transfer

            self.simulation_time += self.time_step

        atp_per_glucose = (
            total_atp_produced / glucose_processed if glucose_processed > 0 else 0
        )

        logger.info(
            f"Simulation completed. Time elapsed: {self.simulation_time:.2f} seconds"
        )
        logger.info(f"Glucose units processed: {glucose_processed}")
        logger.info(f"Total ATP produced: {total_atp_produced}")
        logger.info(f"ATP yield per glucose molecule: {atp_per_glucose:.2f}")
        logger.info(
            f"Remaining oxygen: {self.mitochondrion.metabolites['oxygen'].quantity}"
        )

        return total_atp_produced

    def produce_atp_generator(self, glucose, simulation_duration=SIMULATION_DURATION):
        """Generator that yields the cell's state after each time step."""
        initial_atp = (
            self.cytoplasm.metabolites["atp"].quantity
            + self.mitochondrion.metabolites["atp"].quantity
        )
        self.simulation_time = 0
        total_atp_produced = 0
        glucose_processed = 0

        while (
            glucose_processed < glucose and self.simulation_time < simulation_duration
        ):
            if self.mitochondrion.metabolites["oxygen"].quantity <= 0:
                logger.warning("Oxygen depleted. Stopping simulation.")
                break

            # Check ADP availability
            if self.mitochondrion.metabolites["adp"].quantity < 10:
                logger.warning(
                    "Low ADP levels in mitochondrion. Transferring ADP from cytoplasm."
                )
                adp_transfer = min(50, self.cytoplasm.metabolites["adp"].quantity)
                self.mitochondrion.metabolites["adp"].quantity += adp_transfer
                self.cytoplasm.metabolites["adp"].quantity -= adp_transfer

            # Implement feedback activation
            adp_activation_factor = 1 + self.cytoplasm.metabolites["adp"].quantity / 500
            self.cytoplasm.glycolysis_rate *= adp_activation_factor

            # Glycolysis with updated rate
            pyruvate = self.cytoplasm.glycolysis(1 * self.cytoplasm.glycolysis_rate)
            glucose_processed += 1 * self.cytoplasm.glycolysis_rate

            # Calculate ATP produced in glycolysis
            glycolysis_atp = (
                self.cytoplasm.metabolites["atp"].quantity
                - initial_atp
                + self.mitochondrion.metabolites["atp"].quantity
            )
            total_atp_produced += glycolysis_atp

            cytoplasmic_nadh = self.cytoplasm.metabolites["nadh"].quantity

            # NADH shuttle
            mitochondrial_nadh = self.mitochondrion.transfer_cytoplasmic_nadh(
                cytoplasmic_nadh
            )

            # Cellular respiration in mitochondrion
            mitochondrial_atp = self.mitochondrion.cellular_respiration(pyruvate)
            total_atp_produced += mitochondrial_atp

            # Transfer excess ATP from mitochondrion to cytoplasm
            atp_transfer = max(0, self.mitochondrion.metabolites["atp"].quantity - 100)
            self.cytoplasm.metabolites["atp"].quantity += atp_transfer
            self.mitochondrion.metabolites["atp"].quantity -= atp_transfer

            # Yield the current state of the cell
            yield {
                "simulation_time": self.simulation_time,
                "glucose_processed": glucose_processed,
                "total_atp_produced": total_atp_produced,
                "cytoplasm_atp": self.cytoplasm.metabolites["atp"].quantity,
                "mitochondrion_atp": self.mitochondrion.metabolites["atp"].quantity,
                "cytoplasm_nadh": self.cytoplasm.metabolites["nadh"].quantity,
                "mitochondrion_nadh": self.mitochondrion.metabolites["nadh"].quantity,
                "mitochondrion_fadh2": self.mitochondrion.metabolites["fadh2"].quantity,
                "mitochondrial_calcium": self.mitochondrion.metabolites[
                    "calcium"
                ].quantity,
                "cytoplasmic_calcium": self.cytoplasmic_calcium.quantity,
                "proton_gradient": self.mitochondrion.proton_gradient,
                "oxygen_remaining": self.mitochondrion.metabolites["oxygen"].quantity,
            }

            self.simulation_time += self.time_step

        # Final yield after the simulation completes
        yield {
            "simulation_time": self.simulation_time,
            "glucose_processed": glucose_processed,
            "total_atp_produced": total_atp_produced,
            "cytoplasm_atp": self.cytoplasm.metabolites["atp"].quantity,
            "mitochondrion_atp": self.mitochondrion.metabolites["atp"].quantity,
            "cytoplasm_nadh": self.cytoplasm.metabolites["nadh"].quantity,
            "mitochondrion_nadh": self.mitochondrion.metabolites["nadh"].quantity,
            "mitochondrion_fadh2": self.mitochondrion.metabolites["fadh2"].quantity,
            "mitochondrial_calcium": self.mitochondrion.metabolites["calcium"].quantity,
            "cytoplasmic_calcium": self.cytoplasmic_calcium.quantity,
            "proton_gradient": self.mitochondrion.proton_gradient,
            "oxygen_remaining": self.mitochondrion.metabolites["oxygen"].quantity,
        }

    def reset(self):
        """Reset the entire cell state."""
        self.cytoplasm.reset()
        self.mitochondrion.reset()
        self.simulation_time = 0
        self.cytoplasmic_calcium = Metabolite(
            "Ca2+", 100, 1000
        )  # Reset cytoplasmic calcium
        logger.info("Cell state reset")
