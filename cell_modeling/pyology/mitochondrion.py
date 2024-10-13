import logging
import math
from enum import Enum
from typing import Dict

from .constants import *
from .data import Metabolite
from .exceptions import *
from .organelle import Organelle
from .reactions import KrebsCycle

logger = logging.getLogger(__name__)


class GlycolysisSteps(Enum):
    STEP1_HEXOKINASE = "Hexokinase"
    STEP2_PHOSPHOGLUCOSE_ISOMERASE = "Phosphoglucose Isomerase"
    STEP3_PHOSPHOFRUCTOKINASE = "Phosphofructokinase"
    STEP4_ALDOLASE = "Aldolase"
    STEP5_TRIOSE_PHOSPHATE_ISOMERASE = "Triose Phosphate Isomerase"
    STEP6_GLYCERALDEHYDE_3_PHOSPHATE_DEHYDROGENASE = (
        "Glyceraldehyde 3-Phosphate Dehydrogenase"
    )
    STEP7_PHOSPHOGLYCERATE_KINASE = "Phosphoglycerate Kinase"
    STEP8_PHOSPHOGLYCERATE_MUTASE = "Phosphoglycerate Mutase"
    STEP9_ENOLASE = "Enolase"
    STEP10_PYRUVATE_KINASE = "Pyruvate Kinase"


class Mitochondrion(Organelle):
    name = "Mitochondrion"
    """
    Simulates the electron transport chain with individual complexes.

    Proton gradient and ATP synthesis are modeled well, including a proton leak
    for added realism.

    Calcium buffering and its effect on mitochondrial function are included,
    which adds another layer of detail.

    Feedback inhibition for ATP levels is implemented, mimicking real cellular
    regulation mechanisms.
    """

    def __init__(self):
        super().__init__()
        self.add_metabolite("nadh", 0, 1000)
        self.add_metabolite("fadh2", 0, 1000)
        self.add_metabolite("atp", 0, 1000)
        self.add_metabolite("adp", 100, 1000)
        self.add_metabolite("oxygen", 1000, 1000)
        self.add_metabolite("ubiquinone", 100, 1000)
        self.add_metabolite("ubiquinol", 0, 1000)
        self.add_metabolite("cytochrome_c_oxidized", 100, 1000)
        self.add_metabolite("cytochrome_c_reduced", 0, 1000)
        self.add_metabolite("co2", 0, 1000000)
        self.add_metabolite("calcium", 0, 1000)
        self.add_metabolite("oxaloacetate", 0, 1000)

        self.proton_gradient = 0
        self.atp_per_nadh = 2.5
        self.atp_per_fadh2 = 1.5
        self.atp_per_substrate_phosphorylation = 1
        self.oxygen_per_nadh = 0.5
        self.oxygen_per_fadh2 = 0.5

        self.calcium_threshold = CALCIUM_THRESHOLD
        self.calcium_boost_factor = CALCIUM_BOOST_FACTOR
        self.max_proton_gradient = MAX_PROTON_GRADIENT
        self.leak_rate = LEAK_RATE
        self.leak_steepness = LEAK_STEEPNESS
        self.leak_midpoint = LEAK_MIDPOINT

        self.krebs_cycle = KrebsCycle()

    def change_metabolite_quantity(self, metabolite: str, amount: float):
        """
        Changes the quantity of a metabolite, ensuring it doesn't go negative.

        Args:
            metabolite (str): The name of the metabolite to change.
            amount (float): The amount to change the metabolite by (positive or negative).

        Returns:
            float: The actual amount changed (may be different if preventing negative values).
        """
        if metabolite not in self.metabolites:
            self.metabolites[metabolite] = Metabolite(metabolite, 0)

        current_quantity = self.metabolites[metabolite].quantity
        new_quantity = max(current_quantity + amount, 0)
        actual_change = new_quantity - current_quantity

        self.metabolites[metabolite].quantity = new_quantity

        if actual_change != amount:
            logger.warning(
                f"Attempted to decrease {metabolite} by {-amount}, but only decreased by {-actual_change} to prevent negative quantity."
            )

        return actual_change

    def consume_metabolites(self, **metabolites: Dict[str, float]) -> bool:
        """
        Consume multiple metabolites at once.
        Returns True if all metabolites were consumed successfully, False otherwise.
        """
        temp_changes = {}
        for metabolite, amount in metabolites.items():
            actual_change = self.change_metabolite_quantity(metabolite, -amount)
            if abs(actual_change) < abs(amount):
                # Revert changes if not all metabolites could be consumed
                for rev_metabolite, rev_amount in temp_changes.items():
                    self.change_metabolite_quantity(rev_metabolite, rev_amount)
                logger.warning(f"Insufficient {metabolite} for reaction")
                return False
            temp_changes[metabolite] = actual_change
        return True

    def produce_metabolites(self, **metabolites: Dict[str, float]) -> None:
        """
        Produce multiple metabolites at once.
        """
        for metabolite, amount in metabolites.items():
            actual_change = self.change_metabolite_quantity(metabolite, amount)
            if actual_change != amount:
                logger.warning(
                    f"Could not produce full amount of {metabolite}. Produced {actual_change} instead of {amount}."
                )

    def krebs_cycle_process(self, acetyl_coa_amount: int):
        """Processes acetyl-CoA through the Krebs cycle"""
        logger.info(
            f"Processing {acetyl_coa_amount} units of acetyl-CoA through the Krebs cycle"
        )

        self.krebs_cycle.add_substrate("Acetyl-CoA", acetyl_coa_amount)

        # Ensure there's enough oxaloacetate to start the cycle
        if self.metabolites["oxaloacetate"].quantity < acetyl_coa_amount:
            oxaloacetate_needed = (
                acetyl_coa_amount - self.metabolites["oxaloacetate"].quantity
            )
            if not self.consume_metabolites(oxaloacetate=oxaloacetate_needed):
                logger.warning("Insufficient oxaloacetate to start Krebs cycle")
                return 0

        total_nadh = 0
        total_fadh2 = 0
        total_atp = 0

        for metabolites, cofactors in self.krebs_cycle.krebs_cycle_iterator(
            num_cycles=acetyl_coa_amount
        ):
            total_nadh += cofactors["nadh"]
            total_fadh2 += cofactors["fadh2"]
            total_atp += cofactors["gtp"]  # GTP is equivalent to ATP

        # Transfer the products to the mitochondrion
        self.produce_metabolites(nadh=total_nadh, fadh2=total_fadh2, atp=total_atp)

        # Reset the Krebs cycle for the next round
        self.krebs_cycle.reset()

        return total_nadh + total_fadh2

    def pyruvate_to_acetyl_coa(self, pyruvate_amount: int) -> int:
        """Converts pyruvate to Acetyl-CoA."""
        logger.info(f"Converting {pyruvate_amount} units of pyruvate to Acetyl-CoA")
        acetyl_coa_produced = pyruvate_amount
        self.change_metabolite_quantity("nadh", pyruvate_amount)
        self.change_metabolite_quantity("co2", pyruvate_amount)
        return acetyl_coa_produced

    def calculate_oxygen_needed(self, pyruvate_amount: int) -> float:
        """
        Calculate the amount of oxygen needed for cellular respiration based on pyruvate amount.
        """
        # Assuming each pyruvate molecule requires 2.5 oxygen molecules
        # (This is an approximation, you may need to adjust based on your model's specifics)
        return pyruvate_amount * 2.5

    def cellular_respiration(self, pyruvate_amount: int):
        """Simulates the entire cellular respiration process with feedback inhibition"""
        if self.metabolites["oxygen"].quantity <= 0:
            logger.warning("No oxygen available. Cellular respiration halted.")
            return 0

        acetyl_coa = self.pyruvate_to_acetyl_coa(pyruvate_amount)
        self.krebs_cycle.add_substrate("Acetyl-CoA", acetyl_coa)

        # Implement feedback inhibition
        atp_inhibition_factor = 1 / (
            1 + self.metabolites["atp"].quantity / 1000
        )  # Example threshold
        self.krebs_cycle.enzymes["citrate_synthase"].activity *= atp_inhibition_factor
        self.krebs_cycle.enzymes[
            "isocitrate_dehydrogenase"
        ].activity *= atp_inhibition_factor

        # Use the new generator-based method for the Krebs cycle
        for reaction_name, result in self.krebs_cycle.reaction_iterator():
            logger.info(f"Completed Krebs cycle step: {reaction_name}")
            if result is False:
                logger.warning(
                    f"Krebs cycle step {reaction_name} failed due to insufficient substrates"
                )
                break

            # After each reaction, check the state of metabolites
            logger.info("Current metabolite state in Krebs cycle:")
            for metabolite, quantity in self.krebs_cycle.metabolite_iterator():
                logger.info(f"  {metabolite}: {quantity:.2f}")

        # Transfer NADH and FADH2 from Krebs cycle to ETC
        self.change_metabolite_quantity("NADH", self.krebs_cycle.cofactors["NADH"])
        self.change_metabolite_quantity("FADH2", self.krebs_cycle.cofactors["FADH2"])

        # Check ADP availability
        if self.metabolites["adp"].quantity < 10:  # Arbitrary threshold
            logger.warning("Low ADP levels. Oxidative phosphorylation may be limited.")

        # Example of updating a method that uses consume_metabolites
        oxygen_needed = self.calculate_oxygen_needed(pyruvate_amount)
        if self.consume_metabolites(oxygen=oxygen_needed):
            # proceed with respiration
            atp_produced = self.oxidative_phosphorylation()
        else:
            logger.warning("Insufficient oxygen for cellular respiration")
            return 0

        # Add ATP from substrate-level phosphorylation in Krebs cycle
        atp_produced += self.krebs_cycle.cofactors["GTP"]  # GTP is equivalent to ATP

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

    def complex_I(self):
        """Simulates Complex I activity."""
        if self.is_metabolite_available("nadh", 1) and self.is_metabolite_available(
            "ubiquinone", 1
        ):
            reaction_rate = min(
                self.metabolites["nadh"].quantity,
                self.metabolites["ubiquinone"].quantity,
            )
            if self.consume_metabolites(nadh=reaction_rate, ubiquinone=reaction_rate):
                self.produce_metabolites(ubiquinol=reaction_rate)
                self.update_proton_gradient(PROTONS_PER_NADH * reaction_rate)  # Updated
                logger.info(
                    f"Complex I: Oxidized {reaction_rate} NADH, pumped {PROTONS_PER_NADH * reaction_rate} protons"
                )
                return reaction_rate
        logger.warning("Insufficient NADH or ubiquinone for Complex I")
        return 0

    def complex_II(self):
        """Simulates Complex II activity."""
        if self.is_metabolite_available("fadh2", 1) and self.is_metabolite_available(
            "ubiquinone", 1
        ):
            reaction_rate = min(
                self.metabolites["fadh2"].quantity,
                self.metabolites["ubiquinone"].quantity,
            )
            if self.consume_metabolites(fadh2=reaction_rate, ubiquinone=reaction_rate):
                self.produce_metabolites(ubiquinol=reaction_rate)
                logger.info(f"Complex II: Oxidized {reaction_rate} FADH2")
                return reaction_rate
        logger.warning("Insufficient FADH2 or ubiquinone for Complex II")
        return 0

    def complex_III(self):
        """Simulates Complex III activity."""
        if self.is_metabolite_available(
            "ubiquinol", 1
        ) and self.is_metabolite_available("cytochrome_c_oxidized", 1):
            reaction_rate = min(
                self.metabolites["ubiquinol"].quantity,
                self.metabolites["cytochrome_c_oxidized"].quantity,
            )
            if self.consume_metabolites(
                ubiquinol=reaction_rate, cytochrome_c_oxidized=reaction_rate
            ):
                self.produce_metabolites(
                    ubiquinone=reaction_rate, cytochrome_c_reduced=reaction_rate
                )
                self.update_proton_gradient(PROTONS_PER_FADH2 * reaction_rate)
                logger.info(
                    f"Complex III: Transferred {reaction_rate} electron pairs, pumped {PROTONS_PER_FADH2 * reaction_rate} protons"
                )
                return reaction_rate
        logger.warning("Insufficient ubiquinol or cytochrome c for Complex III")
        return 0

    def complex_IV(self):
        """Simulates Complex IV activity."""
        if self.is_metabolite_available(
            "cytochrome_c_reduced", 1
        ) and self.is_metabolite_available("oxygen", 0.5):
            reaction_rate = min(
                self.metabolites["cytochrome_c_reduced"].quantity,
                self.metabolites["oxygen"].quantity * 2,
            )  # 2 cytochrome c per O2
            oxygen_consumed = reaction_rate / 2
            if self.consume_metabolites(
                cytochrome_c_reduced=reaction_rate, oxygen=oxygen_consumed
            ):
                self.produce_metabolites(cytochrome_c_oxidized=reaction_rate)
                self.update_proton_gradient(PROTONS_PER_FADH2 * reaction_rate)
                logger.info(
                    f"Complex IV: Consumed {oxygen_consumed} O2, pumped {PROTONS_PER_FADH2 * reaction_rate} protons"
                )
                return reaction_rate
        if self.metabolites["oxygen"].quantity <= 0:
            logger.warning("Insufficient oxygen for Complex IV")
        else:
            logger.warning("Insufficient reduced cytochrome c for Complex IV")
        return 0

    def is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        """Check if a metabolite is available in sufficient quantity."""
        if hasattr(self, metabolite):
            return getattr(self, metabolite).quantity >= amount
        else:
            logger.warning(f"Unknown metabolite: {metabolite}")
            return False

    def atp_synthase(self):
        """Synthesizes ATP using the proton gradient."""
        protons_required_per_atp = PROTONS_PER_ATP
        possible_atp = int(self.proton_gradient / protons_required_per_atp)
        atp_produced = min(possible_atp, self.metabolites["adp"].quantity)
        if self.consume_metabolites(adp=atp_produced):
            self.produce_metabolites(atp=atp_produced)
            self.proton_gradient -= atp_produced * protons_required_per_atp
            logger.info(f"ATP Synthase: Produced {atp_produced} ATP")
            return atp_produced
        logger.warning("Insufficient ADP for ATP synthesis")
        return 0

    def replenish_ubiquinone(self):
        """Replenishes ubiquinone from ubiquinol"""
        replenish_amount = min(
            self.metabolites["ubiquinol"].quantity,
            self.metabolites["ubiquinone"].max_quantity
            - self.metabolites["ubiquinone"].quantity,
        )
        self.change_metabolite_quantity("ubiquinone", replenish_amount)
        self.change_metabolite_quantity("ubiquinol", -replenish_amount)
        logger.info(f"Replenished {replenish_amount} ubiquinone")

    def replenish_cytochrome_c(self):
        """Replenishes oxidized cytochrome c from reduced form"""
        replenish_amount = min(
            self.metabolites["cytochrome_c_reduced"].quantity,
            self.metabolites["cytochrome_c_oxidized"].max_quantity
            - self.metabolites["cytochrome_c_oxidized"].quantity,
        )
        self.change_metabolite_quantity("cytochrome_c_oxidized", replenish_amount)
        self.change_metabolite_quantity("cytochrome_c_reduced", -replenish_amount)
        logger.info(f"Replenished {replenish_amount} oxidized cytochrome c")

    def oxidative_phosphorylation(self, cytoplasmic_nadh_used: int = 0):
        """Simulates oxidative phosphorylation with the electron transport chain."""
        if self.metabolites["oxygen"].quantity <= 0:
            logger.warning("No oxygen available. Oxidative phosphorylation halted.")
            return 0

        total_nadh = self.metabolites["nadh"].quantity + cytoplasmic_nadh_used

        # Run the electron transport chain
        electrons_through_complex_I = self.complex_I()
        electrons_through_complex_II = self.complex_II()
        electrons_through_complex_III = self.complex_III()
        electrons_through_complex_IV = self.complex_IV()

        # ATP production via ATP synthase
        atp_produced = self.atp_synthase()

        # Replenish ubiquinone and cytochrome c
        self.replenish_ubiquinone()
        self.replenish_cytochrome_c()

        # Calculate efficiency
        total_electrons = electrons_through_complex_I + electrons_through_complex_II
        if total_electrons > 0:
            efficiency = atp_produced / total_electrons
            logger.info(
                f"Oxidative phosphorylation efficiency: {efficiency:.2f} ATP per electron pair"
            )

        return atp_produced

    def buffer_calcium(self, cytoplasmic_calcium: int):
        """Simulates calcium buffering by the mitochondrion."""
        calcium_uptake = min(
            cytoplasmic_calcium,
            self.metabolites["calcium"].max_quantity
            - self.metabolites["calcium"].quantity,
        )
        self.change_metabolite_quantity("calcium", calcium_uptake)
        logger.info(f"Mitochondrion buffered {calcium_uptake} units of calcium")

        if self.metabolites["calcium"].quantity > self.calcium_threshold:
            logger.warning(
                "Calcium overload detected. Risk of mitochondrial dysfunction."
            )

        return calcium_uptake

    def release_calcium(self, amount: int):
        """Releases calcium from the mitochondrion."""
        released = min(amount, self.metabolites["calcium"].quantity)
        self.change_metabolite_quantity("calcium", -released)
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
        shuttle_efficiency = SHUTTLE_EFFICIENCY
        mitochondrial_nadh = int(cytoplasmic_nadh * shuttle_efficiency)
        self.change_metabolite_quantity("nadh", mitochondrial_nadh)
        logger.info(
            f"Transferred {cytoplasmic_nadh} cytoplasmic NADH, produced {mitochondrial_nadh} mitochondrial NADH"
        )
        return mitochondrial_nadh
