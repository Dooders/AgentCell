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

    def pyruvate_to_acetyl_coa(self, pyruvate_amount: int) -> int:
        """Converts pyruvate to acetyl-CoA."""
        logger.info(f"Converting {pyruvate_amount} units of pyruvate to acetyl-CoA")
        acetyl_coa_produced = pyruvate_amount
        self.nadh.quantity = min(
            self.nadh.quantity + pyruvate_amount, self.nadh.max_quantity
        )
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

    def oxidative_phosphorylation(self):
        """Simulates oxidative phosphorylation."""
        nadh_atp = min(
            self.nadh.quantity * 2.5, self.nadh.max_quantity
        )  # Each NADH produces ~2.5 ATP
        fadh2_atp = min(
            self.fadh2.quantity * 1.5, self.fadh2.max_quantity
        )  # Each FADH2 produces ~1.5 ATP
        total_atp = int(nadh_atp + fadh2_atp)

        self.atp.quantity = min(self.atp.quantity + total_atp, self.atp.max_quantity)
        self.nadh.quantity = 0
        self.fadh2.quantity = 0

        logger.info(f"ATP produced in oxidative phosphorylation: {total_atp}")

    def reset(self):
        """Reset mitochondrion state."""
        self.__init__()
        logger.info("Mitochondrion state reset")


class Cell:
    def __init__(self):
        self.cytoplasm = Cytoplasm()
        self.mitochondrion = Mitochondrion()
        self.simulation_time = 0
        self.time_step = 0.1

    def produce_atp(self, glucose_amount: int, duration: float) -> int:
        """Simulates ATP production in the entire cell."""
        initial_atp = self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity
        self.simulation_time = 0

        # Glycolysis in cytoplasm
        pyruvate = self.cytoplasm.glycolysis(glucose_amount)
        self.simulation_time += 1

        # Pyruvate processing and Krebs cycle in mitochondrion
        acetyl_coa = self.mitochondrion.pyruvate_to_acetyl_coa(pyruvate)
        self.mitochondrion.krebs_cycle(acetyl_coa)
        self.simulation_time += 2

        # Oxidative phosphorylation
        self.mitochondrion.oxidative_phosphorylation()
        self.simulation_time += 1

        total_atp = (
            self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity - initial_atp
        )
        atp_per_glucose = total_atp / glucose_amount
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
