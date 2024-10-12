"""
Biological Background
Structure: 
    Double-membrane organelle with inner folds called cristae; 
    contains its own DNA.
Function:
    ATP Production: 
        Generates ATP through cellular respiration (glycolysis, Krebs cycle, 
        oxidative phosphorylation).
    Metabolic Integration: 
        Involved in apoptosis, calcium storage, and other metabolic pathways.
Modeling Considerations
    Metabolic Pathways:
        Glycolysis:
        Occurs in the cytoplasm; glucose breakdown.
        Krebs Cycle: Occurs in the mitochondrial matrix.
        Electron Transport Chain (ETC): Located in the inner mitochondrial membrane.
    ATP Yield Calculations:
        Model the stoichiometry of ATP production from substrates.
"""

import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Metabolite:
    name: str
    quantity: int
    max_quantity: int


class Cytoplasm:
    def __init__(self):
        self.glucose = 0
        self.pyruvate = 0
        self.atp = Metabolite("ATP", 0, 1000)
        self.nadh = Metabolite("NADH", 0, 1000)

    def glycolysis(self, glucose_amount: int) -> int:
        """Simulates glycolysis in the cytoplasm."""
        logger.info(f"Glycolysis of {glucose_amount} units of glucose in cytoplasm")
        atp_produced = glucose_amount * 2  # Net ATP production in glycolysis
        self.atp.quantity = min(self.atp.quantity + atp_produced, self.atp.max_quantity)
        self.nadh.quantity = min(
            self.nadh.quantity + glucose_amount * 2, self.nadh.max_quantity
        )
        self.pyruvate += glucose_amount * 2
        return self.pyruvate

    def reset(self):
        """Reset cytoplasm state."""
        self.__init__()
        logger.info("Cytoplasm state reset")


class Mitochondrion:
    def __init__(self):
        self.nadh = Metabolite("NADH", 0, 1000)
        self.fadh2 = Metabolite("FADH2", 0, 1000)
        self.atp = Metabolite("ATP", 0, 1000)
        self.oxygen = Metabolite("O2", 1_000_000, 1_000_000)
        self.proton_gradient = 0
        self.co2 = Metabolite("CO2", 0, 1000000)  # Add CO2 metabolite

    def pyruvate_to_acetyl_coa(self, pyruvate_amount: int) -> int:
        """Converts pyruvate to acetyl-CoA."""
        logger.info(f"Converting {pyruvate_amount} units of pyruvate to acetyl-CoA")
        acetyl_coa_produced = pyruvate_amount
        self.nadh.quantity = min(
            self.nadh.quantity + pyruvate_amount, self.nadh.max_quantity
        )
        self.co2.quantity = min(
            self.co2.quantity + pyruvate_amount, self.co2.max_quantity
        )  # Add CO2 production
        return acetyl_coa_produced

    def krebs_cycle(self, acetyl_coa_amount: int):
        """Simulates the Krebs cycle."""
        logger.info(f"Krebs cycle processing {acetyl_coa_amount} units of acetyl-CoA")
        for _ in range(acetyl_coa_amount):
            self.atp.quantity = min(
                self.atp.quantity + 1, self.atp.max_quantity
            )  # 1 GTP (equivalent to ATP) per acetyl-CoA
            self.nadh.quantity = min(
                self.nadh.quantity + 3, self.nadh.max_quantity
            )  # 3 NADH per acetyl-CoA
            self.fadh2.quantity = min(
                self.fadh2.quantity + 1, self.fadh2.max_quantity
            )  # 1 FADH2 per acetyl-CoA

    def oxidative_phosphorylation(self, cytoplasmic_nadh_used: int = 0):
        """Simulates oxidative phosphorylation."""
        total_oxygen_required = (
            self.nadh.quantity + self.fadh2.quantity + cytoplasmic_nadh_used
        ) * 0.5
        if self.oxygen.quantity < total_oxygen_required:
            logger.warning("Not enough oxygen for oxidative phosphorylation")
            total_nadh_used = int(self.oxygen.quantity * 2) - cytoplasmic_nadh_used
            total_fadh2_used = 0
            oxygen_consumed = self.oxygen.quantity
            self.oxygen.quantity = 0
        else:
            total_nadh_used = self.nadh.quantity
            total_fadh2_used = self.fadh2.quantity
            oxygen_consumed = total_oxygen_required
            self.oxygen.quantity -= oxygen_consumed

        mitochondrial_nadh_atp = (
            total_nadh_used * 2.5
        )  # Each mitochondrial NADH produces ~2.5 ATP
        cytoplasmic_nadh_atp = (
            cytoplasmic_nadh_used * 1.5
        )  # Each cytoplasmic NADH produces ~1.5 ATP via glycerol-phosphate shuttle
        fadh2_atp = total_fadh2_used * 1.5  # Each FADH2 produces ~1.5 ATP
        total_atp = int(mitochondrial_nadh_atp + cytoplasmic_nadh_atp + fadh2_atp)

        self.atp.quantity = min(self.atp.quantity + total_atp, self.atp.max_quantity)
        self.nadh.quantity -= total_nadh_used
        self.fadh2.quantity -= total_fadh2_used

        logger.info(f"ATP produced in oxidative phosphorylation: {total_atp}")
        logger.info(f"Oxygen consumed: {oxygen_consumed}")
        return total_atp

    def reset(self):
        """Reset mitochondrion state."""
        self.__init__()
        logger.info("Mitochondrion state reset")

    def transfer_cytoplasmic_nadh(self, cytoplasmic_nadh: int) -> int:
        """
        Transfers cytoplasmic NADH into the mitochondrion using shuttle systems.
        Returns the amount of mitochondrial NADH produced.
        """
        shuttle_efficiency = 0.67  # Efficiency of the glycerol-phosphate shuttle
        mitochondrial_nadh = int(cytoplasmic_nadh * shuttle_efficiency)
        self.nadh.quantity = min(
            self.nadh.quantity + mitochondrial_nadh, self.nadh.max_quantity
        )
        logger.info(
            f"Transferred {cytoplasmic_nadh} cytoplasmic NADH, produced {mitochondrial_nadh} mitochondrial NADH"
        )
        return mitochondrial_nadh


class Cell:
    def __init__(self):
        self.cytoplasm = Cytoplasm()
        self.mitochondrion = Mitochondrion()
        self.simulation_time = 0
        self.time_step = 0.1  # 0.1 second per time step

    def produce_atp(self, glucose_amount: int, duration: float) -> int:
        """Simulates ATP production in the entire cell over a specified duration."""
        initial_atp = self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity
        self.simulation_time = 0

        glucose_remaining = glucose_amount
        pyruvate_accumulated = 0
        cytoplasmic_nadh_accumulated = 0

        while self.simulation_time < duration:
            # Glycolysis (occurs every time step if glucose is available)
            if glucose_remaining > 0:
                glucose_processed = min(
                    glucose_remaining, 1
                )  # Process up to 1 glucose per time step
                pyruvate_produced = self.cytoplasm.glycolysis(glucose_processed)
                pyruvate_accumulated += pyruvate_produced
                cytoplasmic_nadh_accumulated += self.cytoplasm.nadh.quantity
                self.cytoplasm.nadh.quantity = 0  # Reset cytoplasmic NADH
                glucose_remaining -= glucose_processed

            # NADH shuttle and oxidative phosphorylation (occurs every time step)
            cytoplasmic_nadh_used = min(
                cytoplasmic_nadh_accumulated, 5
            )  # Process up to 5 NADH per time step
            mitochondrial_nadh_produced = self.mitochondrion.transfer_cytoplasmic_nadh(
                cytoplasmic_nadh_used
            )
            cytoplasmic_nadh_accumulated -= cytoplasmic_nadh_used
            self.mitochondrion.oxidative_phosphorylation(cytoplasmic_nadh_used)

            # Pyruvate processing and Krebs cycle (occurs every 10 time steps if pyruvate is available)
            if (
                self.simulation_time % (10 * self.time_step) < self.time_step
                and pyruvate_accumulated > 0
            ):
                pyruvate_processed = min(
                    pyruvate_accumulated, 5
                )  # Process up to 5 pyruvate per cycle
                acetyl_coa = self.mitochondrion.pyruvate_to_acetyl_coa(
                    pyruvate_processed
                )
                self.mitochondrion.krebs_cycle(acetyl_coa)
                pyruvate_accumulated -= pyruvate_processed

            self.simulation_time += self.time_step

        total_atp = (
            self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity - initial_atp
        )
        atp_per_glucose = total_atp / glucose_amount if glucose_amount > 0 else 0
        logger.info(
            f"Simulation completed. Time elapsed: {self.simulation_time:.2f} seconds"
        )
        logger.info(f"Total ATP produced: {total_atp}")
        logger.info(f"ATP yield per glucose molecule: {atp_per_glucose:.2f}")
        return total_atp

    def reset(self):
        """Reset the entire cell state."""
        self.cytoplasm.reset()
        self.mitochondrion.reset()
        self.simulation_time = 0
        logger.info("Cell state reset")


# Simulation code
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    cell = Cell()
    glucose_amounts = [1, 2, 5, 10]
    simulation_duration = (
        5  # 5 seconds should be enough for complete glucose processing
    )

    for glucose in glucose_amounts:
        logger.info(f"\nSimulating ATP production with {glucose} glucose units:")
        atp_produced = cell.produce_atp(glucose, simulation_duration)

        # Log the current state of the cell
        logger.info(f"Cytoplasm ATP: {cell.cytoplasm.atp.quantity}")
        logger.info(f"Cytoplasm NADH: {cell.cytoplasm.nadh.quantity}")
        logger.info(f"Mitochondrion ATP: {cell.mitochondrion.atp.quantity}")
        logger.info(f"Mitochondrion NADH: {cell.mitochondrion.nadh.quantity}")
        logger.info(f"Mitochondrion FADH2: {cell.mitochondrion.fadh2.quantity}")
        logger.info(f"Simulation time: {cell.simulation_time:.2f} seconds")

        # Reset the cell for the next simulation
        cell.reset()

    logger.info("Simulation complete.")
