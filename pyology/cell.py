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
        self.base_glycolysis_rate = 1.0  # This is now in the Cell class

    def produce_atp(self, glucose, simulation_duration=SIMULATION_DURATION):
        """Simulates ATP production in the entire cell over a specified duration."""
        self.simulation_time = 0
        total_atp_produced = 0
        glucose_processed = 0

        while (
            glucose_processed < glucose and self.simulation_time < simulation_duration
        ):
            if self.mitochondrion.metabolites["oxygen"].quantity <= 0:
                logger.warning("Oxygen depleted. Stopping simulation.")
                break

            # Calculate ATP at the start of the iteration
            atp_start = (
                self.cytoplasm.metabolites["atp"].quantity
                + self.mitochondrion.metabolites["atp"].quantity
            )

            # Check ADP availability
            if self.mitochondrion.metabolites["adp"].quantity < 10:  # Arbitrary threshold
                logger.warning(
                    "Low ADP levels in mitochondrion. Transferring ADP from cytoplasm."
                )
                adp_transfer = min(
                    50, 
                    max(0, self.cytoplasm.metabolites["adp"].quantity)
                )  # Transfer up to 50 ADP, but not less than 0
                self.mitochondrion.metabolites["adp"].quantity += adp_transfer
                self.cytoplasm.metabolites["adp"].quantity -= adp_transfer

            # Implement feedback activation
            adp_activation_factor = (
                1 + self.cytoplasm.metabolites["adp"].quantity / 500
            )  # Example threshold
            current_glycolysis_rate = self.base_glycolysis_rate * adp_activation_factor

            # Glycolysis with updated rate
            glucose_consumed = min(1 * current_glycolysis_rate, self.cytoplasm.metabolites["glucose"].quantity)
            pyruvate = self.cytoplasm.glycolysis(glucose_consumed)
            self.mitochondrion.add_metabolite("pyruvate", pyruvate)
            logger.info(f"Transferred {pyruvate} pyruvate to mitochondrion")
            glucose_processed += glucose_consumed

            cytoplasmic_nadh = self.cytoplasm.metabolites["nadh"].quantity

            # NADH shuttle
            mitochondrial_nadh = self.mitochondrion.transfer_cytoplasmic_nadh(
                cytoplasmic_nadh
            )

            # Cellular respiration in mitochondrion
            mitochondrial_atp = self.mitochondrion.cellular_respiration(pyruvate)

            # Transfer excess ATP from mitochondrion to cytoplasm
            atp_transfer = max(
                0, self.mitochondrion.metabolites["atp"].quantity - 100
            )  # Keep 100 ATP in mitochondrion
            self.cytoplasm.metabolites["atp"].quantity += atp_transfer
            self.mitochondrion.metabolites["atp"].quantity -= atp_transfer

            # Calculate ATP at the end of the iteration
            atp_end = (
                self.cytoplasm.metabolites["atp"].quantity
                + self.mitochondrion.metabolites["atp"].quantity
            )

            # Calculate ATP produced in this iteration
            delta_atp = atp_end - atp_start
            total_atp_produced += delta_atp

            self.simulation_time += self.time_step

        # ... existing code for logging results ...

        return total_atp_produced

    def produce_atp_generator(self, glucose, simulation_duration=SIMULATION_DURATION):
        """Generator that yields the cell's state after each time step."""
        self.simulation_time = 0
        total_atp_produced = 0
        glucose_processed = 0

        while (
            glucose_processed < glucose and self.simulation_time < simulation_duration
        ):
            if self.mitochondrion.metabolites["oxygen"].quantity <= 0:
                logger.warning("Oxygen depleted. Stopping simulation.")
                break

            # Calculate ATP at the start of the iteration
            atp_start = (
                self.cytoplasm.metabolites["atp"].quantity
                + self.mitochondrion.metabolites["atp"].quantity
            )

            # Check ADP availability and transfer if needed
            if self.mitochondrion.metabolites["adp"].quantity < 10:
                logger.warning(
                    "Low ADP levels in mitochondrion. Transferring ADP from cytoplasm."
                )
                adp_transfer = min(
                    50, 
                    max(0, self.cytoplasm.metabolites["adp"].quantity)
                )  # Transfer up to 50 ADP, but not less than 0
                self.mitochondrion.metabolites["adp"].quantity += adp_transfer
                self.cytoplasm.metabolites["adp"].quantity -= adp_transfer

            # Implement feedback activation
            adp_activation_factor = 1 + self.cytoplasm.metabolites["adp"].quantity / 500
            current_glycolysis_rate = self.base_glycolysis_rate * adp_activation_factor

            # Glycolysis with updated rate
            glucose_consumed = min(1 * current_glycolysis_rate, self.cytoplasm.metabolites["glucose"].quantity)
            pyruvate = self.cytoplasm.glycolysis(glucose_consumed)
            glucose_processed += glucose_consumed

            cytoplasmic_nadh = self.cytoplasm.metabolites["nadh"].quantity

            # NADH shuttle
            mitochondrial_nadh = self.mitochondrion.transfer_cytoplasmic_nadh(
                cytoplasmic_nadh
            )

            # Cellular respiration in mitochondrion
            mitochondrial_atp = self.mitochondrion.cellular_respiration(pyruvate)

            # Transfer excess ATP from mitochondrion to cytoplasm
            atp_transfer = max(0, self.mitochondrion.metabolites["atp"].quantity - 100)
            self.cytoplasm.metabolites["atp"].quantity += atp_transfer
            self.mitochondrion.metabolites["atp"].quantity -= atp_transfer

            # Calculate ATP at the end of the iteration
            atp_end = (
                self.cytoplasm.metabolites["atp"].quantity
                + self.mitochondrion.metabolites["atp"].quantity
            )

            # Calculate ATP produced in this iteration
            delta_atp = atp_end - atp_start
            total_atp_produced += delta_atp

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
