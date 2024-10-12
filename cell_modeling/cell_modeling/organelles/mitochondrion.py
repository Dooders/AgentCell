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
import math
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
        self.atp = 0
        self.adp = 0
        self.nad = 10  # Starting NAD+ molecules
        self.nadh = 0
        self.pyruvate = 0
        self.logger = logging.getLogger(__name__)

    def glycolysis(self, glucose_units):
        self.glucose = glucose_units
        self.logger.info(f"Starting glycolysis with {self.glucose} units of glucose")

        self.step1_hexokinase()
        self.step2_phosphoglucose_isomerase()
        self.step3_phosphofructokinase()
        self.step4_aldolase()
        self.step5_triose_phosphate_isomerase()
        self.step6_glyceraldehyde_3_phosphate_dehydrogenase()
        self.step7_phosphoglycerate_kinase()
        self.step8_phosphoglycerate_mutase()
        self.step9_enolase()
        self.step10_pyruvate_kinase()

        self.logger.info(
            f"Glycolysis complete. Produced {self.pyruvate} pyruvate molecules"
        )
        return self.pyruvate

    def step1_hexokinase(self):
        if self.glucose > 0 and self.atp >= 1:
            self.glucose -= 1
            self.atp -= 1
            self.adp += 1
            self.logger.info("Step 1: Hexokinase - Glucose phosphorylation")

    def step2_phosphoglucose_isomerase(self):
        self.logger.info("Step 2: Phosphoglucose isomerase - Isomerization")

    def step3_phosphofructokinase(self):
        if self.atp >= 1:
            self.atp -= 1
            self.adp += 1
            self.logger.info("Step 3: Phosphofructokinase - Phosphorylation")

    def step4_aldolase(self):
        self.logger.info("Step 4: Aldolase - Splitting fructose-1,6-bisphosphate")

    def step5_triose_phosphate_isomerase(self):
        self.logger.info("Step 5: Triose phosphate isomerase - Isomerization")

    def step6_glyceraldehyde_3_phosphate_dehydrogenase(self):
        if self.nad >= 2:
            self.nad -= 2
            self.nadh += 2
            self.logger.info(
                "Step 6: Glyceraldehyde 3-phosphate dehydrogenase - Oxidation and phosphorylation"
            )

    def step7_phosphoglycerate_kinase(self):
        self.atp += 2
        self.adp -= 2
        self.logger.info("Step 7: Phosphoglycerate kinase - ATP generation")

    def step8_phosphoglycerate_mutase(self):
        self.logger.info("Step 8: Phosphoglycerate mutase - Shifting phosphate group")

    def step9_enolase(self):
        self.logger.info("Step 9: Enolase - Dehydration")

    def step10_pyruvate_kinase(self):
        self.atp += 2
        self.adp -= 2
        self.pyruvate += 2
        self.logger.info(
            "Step 10: Pyruvate kinase - ATP generation and pyruvate formation"
        )


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
        self.calcium = Metabolite("Ca2+", 0, 1000)  # Add calcium metabolite
        self.calcium_threshold = 800  # Threshold for calcium overload
        self.calcium_boost_factor = 1.2  # ATP production boost from calcium
        self.max_proton_gradient = 200  # Maximum sustainable proton gradient
        self.leak_rate = 0.1  # Base leak rate
        self.leak_steepness = 0.1  # Steepness of the logistic curve
        self.leak_midpoint = 150  # Midpoint of the logistic curve

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
        """Simulates the Krebs cycle with calcium-dependent boost."""
        logger.info(f"Krebs cycle processing {acetyl_coa_amount} units of acetyl-CoA")
        # Apply calcium-dependent boost
        calcium_boost = 1 + (self.calcium.quantity / self.calcium.max_quantity) * (
            self.calcium_boost_factor - 1
        )

        for _ in range(acetyl_coa_amount):
            self.atp.quantity = min(
                self.atp.quantity
                + self.atp_per_substrate_phosphorylation * calcium_boost,
                self.atp.max_quantity,
            )
            self.nadh.quantity = min(
                self.nadh.quantity + 3 * calcium_boost, self.nadh.max_quantity
            )
            self.fadh2.quantity = min(
                self.fadh2.quantity + 1 * calcium_boost, self.fadh2.max_quantity
            )

        return (
            acetyl_coa_amount * self.atp_per_substrate_phosphorylation * calcium_boost
        )

    def calculate_proton_leak(self):
        """Calculate the proton leak using a logistic function."""
        relative_gradient = self.proton_gradient / self.max_proton_gradient
        leak = self.leak_rate / (
            1
            + math.exp(
                -self.leak_steepness * (self.proton_gradient - self.leak_midpoint)
            )
        )
        return leak

    def update_proton_gradient(self, protons_pumped):
        """Update the proton gradient considering nonlinear leak."""
        self.proton_gradient += protons_pumped
        leak = self.calculate_proton_leak()
        self.proton_gradient = max(0, self.proton_gradient - leak)
        logger.info(f"Proton gradient: {self.proton_gradient:.2f}, Leak: {leak:.2f}")

    def oxidative_phosphorylation(self, cytoplasmic_nadh_used: int = 0):
        """Simulates oxidative phosphorylation with nonlinear proton leak."""
        total_oxygen_required = (
            self.nadh.quantity + cytoplasmic_nadh_used
        ) * self.oxygen_per_nadh + self.fadh2.quantity * self.oxygen_per_fadh2
        available_oxygen = min(self.oxygen.quantity, total_oxygen_required)

        if available_oxygen < total_oxygen_required:
            logger.warning("Not enough oxygen for complete oxidative phosphorylation")

        oxygen_consumed = available_oxygen
        self.oxygen.quantity -= oxygen_consumed

        # Calculate oxidation based on available oxygen
        nadh_oxidized = min(
            self.nadh.quantity, int(available_oxygen / self.oxygen_per_nadh)
        )
        available_oxygen -= nadh_oxidized * self.oxygen_per_nadh

        cytoplasmic_nadh_oxidized = min(
            cytoplasmic_nadh_used, int(available_oxygen / self.oxygen_per_nadh)
        )
        available_oxygen -= cytoplasmic_nadh_oxidized * self.oxygen_per_nadh

        fadh2_oxidized = min(
            self.fadh2.quantity, int(available_oxygen / self.oxygen_per_fadh2)
        )

        # Calculate protons pumped
        protons_pumped = (
            nadh_oxidized + cytoplasmic_nadh_oxidized
        ) * 10 + fadh2_oxidized * 6
        self.update_proton_gradient(protons_pumped)

        # Calculate ATP production based on proton gradient
        atp_production_efficiency = min(
            1, self.proton_gradient / self.max_proton_gradient
        )

        # Apply calcium-dependent boost
        calcium_boost = 1 + (self.calcium.quantity / self.calcium.max_quantity) * (
            self.calcium_boost_factor - 1
        )

        mitochondrial_nadh_atp = (
            nadh_oxidized
            * self.atp_per_nadh
            * atp_production_efficiency
            * calcium_boost
        )
        cytoplasmic_nadh_atp = (
            cytoplasmic_nadh_oxidized
            * (self.atp_per_nadh - 1)
            * atp_production_efficiency
            * calcium_boost
        )
        fadh2_atp = (
            fadh2_oxidized
            * self.atp_per_fadh2
            * atp_production_efficiency
            * calcium_boost
        )
        total_atp = int(mitochondrial_nadh_atp + cytoplasmic_nadh_atp + fadh2_atp)

        self.atp.quantity = min(self.atp.quantity + total_atp, self.atp.max_quantity)
        self.nadh.quantity -= nadh_oxidized
        self.fadh2.quantity -= fadh2_oxidized

        logger.info(f"ATP produced in oxidative phosphorylation: {total_atp}")
        logger.info(f"Oxygen consumed: {oxygen_consumed}")
        return total_atp

    def buffer_calcium(self, cytoplasmic_calcium: int):
        """Simulates calcium buffering by the mitochondrion."""
        calcium_uptake = min(
            cytoplasmic_calcium, self.calcium.max_quantity - self.calcium.quantity
        )
        self.calcium.quantity += calcium_uptake
        logger.info(f"Mitochondrion buffered {calcium_uptake} units of calcium")

        if self.calcium.quantity > self.calcium_threshold:
            logger.warning(
                "Calcium overload detected. Risk of mitochondrial dysfunction."
            )

        return calcium_uptake

    def release_calcium(self, amount: int):
        """Releases calcium from the mitochondrion."""
        released = min(amount, self.calcium.quantity)
        self.calcium.quantity -= released
        logger.info(f"Mitochondrion released {released} units of calcium")
        return released

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
        self.cytoplasmic_calcium = Metabolite("Ca2+", 100, 1000)

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
            glucose_processed += 1

            # Calculate ATP produced in glycolysis
            glycolysis_atp = (
                self.cytoplasm.atp.quantity
                - initial_atp
                + self.mitochondrion.atp.quantity
            )
            total_atp_produced += glycolysis_atp

            cytoplasmic_nadh = self.cytoplasm.nadh.quantity
            self.cytoplasm.nadh.quantity = 0  # Reset cytoplasmic NADH

            # NADH shuttle
            mitochondrial_nadh = self.mitochondrion.transfer_cytoplasmic_nadh(
                cytoplasmic_nadh
            )

            # Pyruvate to Acetyl-CoA
            acetyl_coa = self.mitochondrion.pyruvate_to_acetyl_coa(pyruvate)

            # Calcium dynamics
            calcium_to_buffer = min(10, self.cytoplasmic_calcium.quantity)
            buffered_calcium = self.mitochondrion.buffer_calcium(calcium_to_buffer)
            self.cytoplasmic_calcium.quantity -= buffered_calcium

            # Simulate calcium release (e.g., every 10 time steps)
            if int(self.simulation_time / self.time_step) % 10 == 0:
                released_calcium = self.mitochondrion.release_calcium(5)
                self.cytoplasmic_calcium.quantity = min(
                    self.cytoplasmic_calcium.quantity + released_calcium,
                    self.cytoplasmic_calcium.max_quantity,
                )

            # Krebs cycle
            krebs_atp = self.mitochondrion.krebs_cycle(acetyl_coa)
            total_atp_produced += krebs_atp

            # Oxidative phosphorylation
            ox_phos_atp = self.mitochondrion.oxidative_phosphorylation(cytoplasmic_nadh)
            total_atp_produced += ox_phos_atp

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
        logger.info(f"Remaining oxygen: {self.mitochondrion.oxygen.quantity}")

        return total_atp_produced

    def reset(self):
        """Reset the entire cell state."""
        self.cytoplasm.reset()
        self.mitochondrion.reset()
        self.simulation_time = 0
        self.cytoplasmic_calcium = Metabolite(
            "Ca2+", 100, 1000
        )  # Reset cytoplasmic calcium
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
        logger.info(f"Mitochondrial Calcium: {cell.mitochondrion.calcium.quantity}")
        logger.info(f"Cytoplasmic Calcium: {cell.cytoplasmic_calcium.quantity}")
        logger.info(f"Proton Gradient: {cell.mitochondrion.proton_gradient:.2f}")

        # Reset the cell for the next simulation
        cell.reset()

    logger.info("Simulation complete.")
