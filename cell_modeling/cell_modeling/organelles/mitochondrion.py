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
        self.oxygen = Metabolite("O2", 1000, 1000)  # Limited oxygen supply
        self.proton_gradient = 0
        self.co2 = Metabolite("CO2", 0, 1000000)  # Add CO2 metabolite
        self.atp_per_nadh = 2.5  # Fixed ATP yield per NADH oxidized
        self.atp_per_fadh2 = 1.5  # Fixed ATP yield per FADH2 oxidized
        self.atp_per_substrate_phosphorylation = (
            1  # ATP from substrate-level phosphorylation in Krebs cycle
        )
        self.oxygen_per_nadh = 0.5  # Oxygen consumed per NADH oxidized
        self.oxygen_per_fadh2 = 0.5  # Oxygen consumed per FADH2 oxidized

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
                self.atp.quantity + self.atp_per_substrate_phosphorylation,
                self.atp.max_quantity,
            )
            self.nadh.quantity = min(self.nadh.quantity + 3, self.nadh.max_quantity)
            self.fadh2.quantity = min(self.fadh2.quantity + 1, self.fadh2.max_quantity)
        return acetyl_coa_amount * self.atp_per_substrate_phosphorylation

    def oxidative_phosphorylation(self, cytoplasmic_nadh_used: int = 0):
        """Simulates oxidative phosphorylation with oxygen as a limiting factor."""
        total_oxygen_required = (
            (self.nadh.quantity + cytoplasmic_nadh_used) * self.oxygen_per_nadh +
            self.fadh2.quantity * self.oxygen_per_fadh2
        )
        available_oxygen = min(self.oxygen.quantity, total_oxygen_required)

        if available_oxygen < total_oxygen_required:
            logger.warning("Not enough oxygen for complete oxidative phosphorylation")

        oxygen_consumed = available_oxygen
        self.oxygen.quantity -= oxygen_consumed

        # Calculate oxidation based on available oxygen
        nadh_oxidized = min(self.nadh.quantity, int(available_oxygen / self.oxygen_per_nadh))
        available_oxygen -= nadh_oxidized * self.oxygen_per_nadh

        cytoplasmic_nadh_oxidized = min(cytoplasmic_nadh_used, int(available_oxygen / self.oxygen_per_nadh))
        available_oxygen -= cytoplasmic_nadh_oxidized * self.oxygen_per_nadh

        fadh2_oxidized = min(self.fadh2.quantity, int(available_oxygen / self.oxygen_per_fadh2))

        mitochondrial_nadh_atp = nadh_oxidized * self.atp_per_nadh
        cytoplasmic_nadh_atp = cytoplasmic_nadh_oxidized * (self.atp_per_nadh - 1)  # Accounting for transport cost
        fadh2_atp = fadh2_oxidized * self.atp_per_fadh2
        total_atp = int(mitochondrial_nadh_atp + cytoplasmic_nadh_atp + fadh2_atp)

        self.atp.quantity = min(self.atp.quantity + total_atp, self.atp.max_quantity)
        self.nadh.quantity -= nadh_oxidized
        self.fadh2.quantity -= fadh2_oxidized

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
        self.atp_from_glycolysis = 2  # Net ATP production in glycolysis
        self.expected_atp_yield = 32  # Expected ATP yield per glucose molecule

    def produce_atp(self, glucose_amount: int, duration: float) -> int:
        """Simulates ATP production in the entire cell over a specified duration."""
        initial_atp = self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity
        self.simulation_time = 0
        total_atp_produced = 0
        glucose_processed = 0

        while glucose_processed < glucose_amount and self.simulation_time < duration:
            if self.mitochondrion.oxygen.quantity <= 0:
                logger.warning("Oxygen depleted. Stopping simulation.")
                break

            # Glycolysis
            pyruvate = self.cytoplasm.glycolysis(1)
            total_atp_produced += self.atp_from_glycolysis
            cytoplasmic_nadh = self.cytoplasm.nadh.quantity
            self.cytoplasm.nadh.quantity = 0  # Reset cytoplasmic NADH

            # NADH shuttle
            mitochondrial_nadh = self.mitochondrion.transfer_cytoplasmic_nadh(cytoplasmic_nadh)

            # Pyruvate to Acetyl-CoA
            acetyl_coa = self.mitochondrion.pyruvate_to_acetyl_coa(pyruvate)

            # Krebs cycle
            total_atp_produced += self.mitochondrion.krebs_cycle(acetyl_coa)

            # Oxidative phosphorylation
            total_atp_produced += self.mitochondrion.oxidative_phosphorylation(cytoplasmic_nadh)

            self.simulation_time += self.time_step
            glucose_processed += 1

        atp_per_glucose = total_atp_produced / glucose_processed if glucose_processed > 0 else 0

        logger.info(f"Simulation completed. Time elapsed: {self.simulation_time:.2f} seconds")
        logger.info(f"Glucose units processed: {glucose_processed}")
        logger.info(f"Total ATP produced: {total_atp_produced}")
        logger.info(f"ATP yield per glucose molecule: {atp_per_glucose:.2f}")
        logger.info(f"Remaining oxygen: {self.mitochondrion.oxygen.quantity}")

        if abs(atp_per_glucose - self.expected_atp_yield) > 2:
            logger.warning(f"ATP yield ({atp_per_glucose:.2f}) is outside the expected range (30-34)")

        return total_atp_produced

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