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
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class Metabolite:
    name: str
    quantity: int
    max_quantity: int


class Cytoplasm:
    def __init__(self):
        self.glucose = Metabolite("Glucose", 0, 1000)
        self.atp = Metabolite("ATP", 0, 1000)
        self.adp = Metabolite("ADP", 0, 1000)
        self.nad = Metabolite("NAD+", 10, 1000)  # Starting NAD+ molecules
        self.nadh = Metabolite("NADH", 0, 1000)
        self.pyruvate = Metabolite("Pyruvate", 0, 1000)
        self.logger = logging.getLogger(__name__)

    def glycolysis(self, glucose_units):
        self.glucose.quantity = glucose_units
        self.logger.info(
            f"Starting glycolysis with {self.glucose.quantity} units of glucose"
        )

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
            f"Glycolysis complete. Produced {self.pyruvate.quantity} pyruvate molecules"
        )
        return self.pyruvate.quantity

    def step1_hexokinase(self):
        if self.glucose.quantity > 0 and self.atp.quantity >= 1:
            self.glucose.quantity -= 1
            self.atp.quantity -= 1
            self.adp.quantity += 1
            self.logger.info("Step 1: Hexokinase - Glucose phosphorylation")

    def step2_phosphoglucose_isomerase(self):
        self.logger.info("Step 2: Phosphoglucose isomerase - Isomerization")

    def step3_phosphofructokinase(self):
        if self.atp.quantity >= 1:
            self.atp.quantity -= 1
            self.adp.quantity += 1
            self.logger.info("Step 3: Phosphofructokinase - Phosphorylation")

    def step4_aldolase(self):
        self.logger.info("Step 4: Aldolase - Splitting fructose-1,6-bisphosphate")

    def step5_triose_phosphate_isomerase(self):
        self.logger.info("Step 5: Triose phosphate isomerase - Isomerization")

    def step6_glyceraldehyde_3_phosphate_dehydrogenase(self):
        if self.nad.quantity >= 2:
            self.nad.quantity -= 2
            self.nadh.quantity += 2
            self.logger.info(
                "Step 6: Glyceraldehyde 3-phosphate dehydrogenase - Oxidation and phosphorylation"
            )

    def step7_phosphoglycerate_kinase(self):
        self.atp.quantity += 2
        self.adp.quantity -= 2
        self.logger.info("Step 7: Phosphoglycerate kinase - ATP generation")

    def step8_phosphoglycerate_mutase(self):
        self.logger.info("Step 8: Phosphoglycerate mutase - Shifting phosphate group")

    def step9_enolase(self):
        self.logger.info("Step 9: Enolase - Dehydration")

    def step10_pyruvate_kinase(self):
        self.atp.quantity += 2
        self.adp.quantity -= 2
        self.pyruvate.quantity += 2
        self.logger.info(
            "Step 10: Pyruvate kinase - ATP generation and pyruvate formation"
        )

    def reset(self):
        self.__init__()
        self.logger.info("Cytoplasm state reset")


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
        self.krebs_cycle = KrebsCycle()

    def krebs_cycle_process(self, acetyl_coa_amount: int):
        """Processes acetyl-CoA through the Krebs cycle"""
        logger.info(
            f"Processing {acetyl_coa_amount} units of acetyl-CoA through the Krebs cycle"
        )

        self.krebs_cycle.add_substrate("acetyl_coa", acetyl_coa_amount)

        # Ensure there's enough oxaloacetate to start the cycle
        if self.krebs_cycle.metabolites["oxaloacetate"] < acetyl_coa_amount:
            self.krebs_cycle.add_substrate(
                "oxaloacetate",
                acetyl_coa_amount - self.krebs_cycle.metabolites["oxaloacetate"],
            )

        for _ in range(acetyl_coa_amount):
            self.krebs_cycle.run_cycle()

        # Transfer the products to the mitochondrion
        self.nadh.quantity += self.krebs_cycle.cofactors["nadh"]
        self.fadh2.quantity += self.krebs_cycle.cofactors["fadh2"]
        self.atp.quantity += self.krebs_cycle.cofactors[
            "gtp"
        ]  # GTP is equivalent to ATP

        # Reset the Krebs cycle for the next round
        self.krebs_cycle.reset()

        return self.krebs_cycle.cofactors["nadh"] + self.krebs_cycle.cofactors["fadh2"]

    def pyruvate_to_acetyl_coa(self, pyruvate_amount: int) -> int:
        """Converts pyruvate to acetyl-CoA."""
        logger.info(f"Converting {pyruvate_amount} units of pyruvate to acetyl-CoA")
        acetyl_coa_produced = pyruvate_amount
        self.nadh.quantity = min(
            self.nadh.quantity + pyruvate_amount, self.nadh.max_quantity
        )
        self.co2.quantity = min(
            self.co2.quantity + pyruvate_amount, self.co2.max_quantity
        )
        return acetyl_coa_produced

    def cellular_respiration(self, pyruvate_amount: int):
        """Simulates the entire cellular respiration process"""
        acetyl_coa = self.pyruvate_to_acetyl_coa(pyruvate_amount)
        krebs_products = self.krebs_cycle_process(acetyl_coa)
        atp_produced = self.oxidative_phosphorylation()
        return atp_produced

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


class KrebsCycle:
    def __init__(self):
        self.metabolites: Dict[str, float] = {
            "acetyl_coa": 0,
            "oxaloacetate": 0,
            "citrate": 0,
            "isocitrate": 0,
            "alpha_ketoglutarate": 0,
            "succinyl_coa": 0,
            "succinate": 0,
            "fumarate": 0,
            "malate": 0,
        }
        self.cofactors = {
            "nad": 100,
            "nadh": 0,
            "fad": 100,
            "fadh2": 0,
            "coenzyme_a": 100,
            "atp": 100,
            "adp": 0,
            "gtp": 0,
            "gdp": 0,
            "co2": 0,
        }

    def michaelis_menten(self, substrate_conc: float, vmax: float, km: float) -> float:
        return (vmax * substrate_conc) / (km + substrate_conc)

    def step1_citrate_synthase(self):
        """Acetyl-CoA + Oxaloacetate to Citrate"""
        substrate_conc = min(
            self.metabolites["acetyl_coa"], self.metabolites["oxaloacetate"]
        )
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = self.michaelis_menten(substrate_conc, vmax, km)

        if (
            self.metabolites["acetyl_coa"] >= reaction_rate
            and self.metabolites["oxaloacetate"] >= reaction_rate
        ):
            self.metabolites["acetyl_coa"] -= reaction_rate
            self.metabolites["oxaloacetate"] -= reaction_rate
            self.metabolites["citrate"] += reaction_rate
            self.cofactors["coenzyme_a"] += reaction_rate
        else:
            logger.warning("Insufficient substrates for step 1")

    def step2_aconitase(self):
        """Citrate to Isocitrate"""
        substrate_conc = self.metabolites["citrate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = self.michaelis_menten(substrate_conc, vmax, km)

        if self.metabolites["citrate"] >= reaction_rate:
            self.metabolites["citrate"] -= reaction_rate
            self.metabolites["isocitrate"] += reaction_rate
        else:
            logger.warning("Insufficient citrate for step 2")

    def step3_isocitrate_dehydrogenase(self):
        """Isocitrate to α-Ketoglutarate"""
        substrate_conc = self.metabolites["isocitrate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        # Enzyme regulation
        atp_inhibition = self.cofactors["atp"] / 100
        nadh_inhibition = self.cofactors["nadh"] / 100
        enzyme_activity = 1 - (atp_inhibition + nadh_inhibition) / 2

        reaction_rate = self.michaelis_menten(
            substrate_conc, vmax * enzyme_activity, km
        )

        if (
            self.metabolites["isocitrate"] >= reaction_rate
            and self.cofactors["nad"] >= reaction_rate
        ):
            self.metabolites["isocitrate"] -= reaction_rate
            self.metabolites["alpha_ketoglutarate"] += reaction_rate
            self.cofactors["nad"] -= reaction_rate
            self.cofactors["nadh"] += reaction_rate
            self.cofactors["co2"] += reaction_rate
        else:
            logger.warning("Insufficient substrates or NAD⁺ for step 3")

    def step4_alpha_ketoglutarate_dehydrogenase(self):
        """α-Ketoglutarate to Succinyl-CoA"""
        substrate_conc = self.metabolites["alpha_ketoglutarate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        # Enzyme regulation
        atp_inhibition = self.cofactors["atp"] / 100
        nadh_inhibition = self.cofactors["nadh"] / 100
        succinyl_coa_inhibition = (
            self.metabolites["succinyl_coa"] / 10
        )  # Assuming max succinyl-CoA is 10
        enzyme_activity = (
            1 - (atp_inhibition + nadh_inhibition + succinyl_coa_inhibition) / 3
        )

        reaction_rate = self.michaelis_menten(
            substrate_conc, vmax * enzyme_activity, km
        )

        if (
            self.metabolites["alpha_ketoglutarate"] >= reaction_rate
            and self.cofactors["nad"] >= reaction_rate
        ):
            self.metabolites["alpha_ketoglutarate"] -= reaction_rate
            self.metabolites["succinyl_coa"] += reaction_rate
            self.cofactors["nad"] -= reaction_rate
            self.cofactors["nadh"] += reaction_rate
            self.cofactors["co2"] += reaction_rate
        else:
            logger.warning("Insufficient substrates or NAD⁺ for step 4")

    def step5_succinyl_coa_synthetase(self):
        """Succinyl-CoA to Succinate"""
        substrate_conc = self.metabolites["succinyl_coa"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = self.michaelis_menten(substrate_conc, vmax, km)

        if (
            self.metabolites["succinyl_coa"] >= reaction_rate
            and self.cofactors["gdp"] >= reaction_rate
        ):
            self.metabolites["succinyl_coa"] -= reaction_rate
            self.metabolites["succinate"] += reaction_rate
            self.cofactors["gdp"] -= reaction_rate
            self.cofactors["gtp"] += reaction_rate
            self.cofactors["coenzyme_a"] += reaction_rate
        else:
            logger.warning("Insufficient substrates or GDP for step 5")

    def step6_succinate_dehydrogenase(self):
        """Succinate to Fumarate"""
        substrate_conc = self.metabolites["succinate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = self.michaelis_menten(substrate_conc, vmax, km)

        if (
            self.metabolites["succinate"] >= reaction_rate
            and self.cofactors["fad"] >= reaction_rate
        ):
            self.metabolites["succinate"] -= reaction_rate
            self.metabolites["fumarate"] += reaction_rate
            self.cofactors["fad"] -= reaction_rate
            self.cofactors["fadh2"] += reaction_rate
        else:
            logger.warning("Insufficient substrates or FAD for step 6")

    def step7_fumarase(self):
        """Fumarate to Malate"""
        substrate_conc = self.metabolites["fumarate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = self.michaelis_menten(substrate_conc, vmax, km)

        if self.metabolites["fumarate"] >= reaction_rate:
            self.metabolites["fumarate"] -= reaction_rate
            self.metabolites["malate"] += reaction_rate
        else:
            logger.warning("Insufficient fumarate for step 7")

    def step8_malate_dehydrogenase(self):
        """Malate to Oxaloacetate"""
        substrate_conc = self.metabolites["malate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = self.michaelis_menten(substrate_conc, vmax, km)

        if (
            self.metabolites["malate"] >= reaction_rate
            and self.cofactors["nad"] >= reaction_rate
        ):
            self.metabolites["malate"] -= reaction_rate
            self.metabolites["oxaloacetate"] += reaction_rate
            self.cofactors["nad"] -= reaction_rate
            self.cofactors["nadh"] += reaction_rate
        else:
            logger.warning("Insufficient substrates or NAD⁺ for step 8")

    def run_cycle(self):
        self.step1_citrate_synthase()
        self.step2_aconitase()
        self.step3_isocitrate_dehydrogenase()
        self.step4_alpha_ketoglutarate_dehydrogenase()
        self.step5_succinyl_coa_synthetase()
        self.step6_succinate_dehydrogenase()
        self.step7_fumarase()
        self.step8_malate_dehydrogenase()

    def add_substrate(self, substrate: str, amount: float):
        """Add initial substrate to start the cycle"""
        if substrate in self.metabolites:
            self.metabolites[substrate] += amount
        elif substrate in self.cofactors:
            self.cofactors[substrate] += amount
        else:
            logger.warning(f"Unknown substrate: {substrate}")

    def display_state(self):
        """Display the current state of metabolites and cofactors"""
        print("Metabolites:")
        for metabolite, amount in self.metabolites.items():
            print(f"  {metabolite}: {amount:.2f}")
        print("\nCofactors:")
        for cofactor, amount in self.cofactors.items():
            print(f"  {cofactor}: {amount:.2f}")

    def reset(self):
        """Reset the Krebs cycle to its initial state"""
        self.__init__()


class Cell:
    def __init__(self):
        self.cytoplasm = Cytoplasm()
        self.mitochondrion = Mitochondrion()
        self.simulation_time = 0
        self.time_step = 0.1  # 0.1 second per time step
        self.cytoplasmic_calcium = Metabolite("Ca2+", 100, 1000)

    def produce_atp(self, glucose, simulation_duration):
        """Simulates ATP production in the entire cell over a specified duration."""
        initial_atp = self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity
        self.simulation_time = 0
        total_atp_produced = 0
        glucose_processed = 0

        while (
            glucose_processed < glucose and self.simulation_time < simulation_duration
        ):
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
            krebs_atp = self.mitochondrion.krebs_cycle_process(acetyl_coa)
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
