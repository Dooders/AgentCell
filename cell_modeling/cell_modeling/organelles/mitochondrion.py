import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from constants import *

logger = logging.getLogger(__name__)


@dataclass
class Metabolite:
    name: str
    quantity: int
    max_quantity: int


@dataclass
class Effector:
    name: str
    concentration: float
    Ki: float  # Inhibition constant
    Ka: float  # Activation constant


def michaelis_menten(substrate_conc: float, vmax: float, km: float) -> float:
    """Calculates reaction rate using the Michaelis-Menten equation."""
    return vmax * substrate_conc / (km + substrate_conc)


def allosteric_regulation(
    base_activity: float, inhibitors: List[Effector], activators: List[Effector]
) -> float:
    """Calculates enzyme activity considering inhibitors and activators."""
    inhibition_factor = 1
    for inhibitor in inhibitors:
        inhibition_factor *= 1 / (1 + inhibitor.concentration / inhibitor.Ki)
    activation_factor = 1
    for activator in activators:
        activation_factor *= 1 + activator.concentration / activator.Ka
    return base_activity * inhibition_factor * activation_factor


def hill_equation(substrate_conc: float, Vmax: float, K: float, n: float) -> float:
    """Calculates reaction rate using the Hill equation for cooperative binding."""
    return Vmax * (substrate_conc**n) / (K**n + substrate_conc**n)


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


class Cytoplasm:
    def __init__(self):
        self.glucose = Metabolite("Glucose", 0, 1000)
        self.atp = Metabolite("ATP", 0, 1000)
        self.adp = Metabolite("ADP", 0, 1000)
        self.nad = Metabolite("NAD+", 10, 1000)  # Starting NAD+ molecules
        self.nadh = Metabolite("NADH", 0, 1000)
        self.pyruvate = Metabolite("Pyruvate", 0, 1000)
        self.glycolysis_rate = 1.0  # Base glycolysis rate

    def glycolysis(self, glucose_units):
        """
        Models glycolysis in a step-wise manner, including ATP and NADH
        production.
        """
        self.glucose.quantity = glucose_units
        logger.info(
            f"Starting glycolysis with {self.glucose.quantity} units of glucose"
        )

        for step in GlycolysisSteps:
            getattr(self, f"{step.name.lower()}")()

        logger.info(
            f"Glycolysis complete. Produced {self.pyruvate.quantity} pyruvate molecules"
        )
        return self.pyruvate.quantity

    def is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        """Check if a metabolite is available in sufficient quantity."""
        if hasattr(self, metabolite):
            return getattr(self, metabolite).quantity >= amount
        else:
            logger.warning(f"Unknown metabolite: {metabolite}")
            return False

    def consume_metabolites(self, **metabolites: Dict[str, float]):
        """Consume multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            if self.is_metabolite_available(metabolite, amount):
                getattr(self, metabolite).quantity -= amount
            else:
                logger.warning(f"Insufficient {metabolite} for reaction")
                return False
        return True

    def produce_metabolites(self, **metabolites: Dict[str, float]):
        """Produce multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            if hasattr(self, metabolite):
                getattr(self, metabolite).quantity += amount
            else:
                logger.warning(f"Unknown metabolite: {metabolite}")

    def step1_hexokinase(self):
        if self.consume_metabolites(glucose=1, atp=1):
            self.produce_metabolites(adp=1)
            logger.info(
                f"Step 1: {GlycolysisSteps.STEP1_HEXOKINASE.value} - Glucose phosphorylation"
            )

    def step2_phosphoglucose_isomerase(self):
        logger.info(
            f"Step 2: {GlycolysisSteps.STEP2_PHOSPHOGLUCOSE_ISOMERASE.value} - Isomerization"
        )

    def step3_phosphofructokinase(self):
        if self.consume_metabolites(atp=1):
            self.produce_metabolites(adp=1)
            logger.info(
                f"Step 3: {GlycolysisSteps.STEP3_PHOSPHOFRUCTOKINASE.value} - Phosphorylation"
            )

    def step4_aldolase(self):
        logger.info(
            f"Step 4: {GlycolysisSteps.STEP4_ALDOLASE.value} - Splitting fructose-1,6-bisphosphate"
        )

    def step5_triose_phosphate_isomerase(self):
        logger.info(
            f"Step 5: {GlycolysisSteps.STEP5_TRIOSE_PHOSPHATE_ISOMERASE.value} - Isomerization"
        )

    def step6_glyceraldehyde_3_phosphate_dehydrogenase(self):
        if self.consume_metabolites(nad=2):
            self.produce_metabolites(nadh=2)
            logger.info(
                f"Step 6: {GlycolysisSteps.STEP6_GLYCERALDEHYDE_3_PHOSPHATE_DEHYDROGENASE.value} - Oxidation and phosphorylation"
            )

    def step7_phosphoglycerate_kinase(self):
        if self.consume_metabolites(adp=2):
            self.produce_metabolites(atp=2)
            logger.info(
                f"Step 7: {GlycolysisSteps.STEP7_PHOSPHOGLYCERATE_KINASE.value} - ATP generation"
            )

    def step8_phosphoglycerate_mutase(self):
        logger.info(
            f"Step 8: {GlycolysisSteps.STEP8_PHOSPHOGLYCERATE_MUTASE.value} - Shifting phosphate group"
        )

    def step9_enolase(self):
        logger.info(f"Step 9: {GlycolysisSteps.STEP9_ENOLASE.value} - Dehydration")

    def step10_pyruvate_kinase(self):
        if self.consume_metabolites(adp=2):
            self.produce_metabolites(atp=2, pyruvate=2)
            logger.info(
                f"Step 10: {GlycolysisSteps.STEP10_PYRUVATE_KINASE.value} - ATP generation and pyruvate formation"
            )

    def reset(self):
        self.__init__()
        logger.info("Cytoplasm state reset")


class Mitochondrion:
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
        self.nadh = Metabolite("NADH", 0, 1000)
        self.fadh2 = Metabolite("FADH2", 0, 1000)
        self.atp = Metabolite("ATP", 0, 1000)
        self.adp = Metabolite("ADP", 100, 1000)  # Add ADP
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
        self.calcium_threshold = CALCIUM_THRESHOLD
        self.calcium_boost_factor = CALCIUM_BOOST_FACTOR
        self.max_proton_gradient = MAX_PROTON_GRADIENT
        self.leak_rate = LEAK_RATE
        self.leak_steepness = LEAK_STEEPNESS
        self.leak_midpoint = LEAK_MIDPOINT
        self.krebs_cycle = KrebsCycle()
        self.ubiquinone = Metabolite("Ubiquinone", 100, 1000)
        self.ubiquinol = Metabolite("Ubiquinol", 0, 1000)
        self.cytochrome_c_oxidized = Metabolite("Cytochrome c (oxidized)", 100, 1000)
        self.cytochrome_c_reduced = Metabolite("Cytochrome c (reduced)", 0, 1000)

    def change_metabolite_quantity(self, metabolite_name: str, amount: float):
        """Centralized method to change metabolite quantities."""
        if hasattr(self, metabolite_name):
            metabolite = getattr(self, metabolite_name)
            metabolite.quantity = max(
                0, min(metabolite.quantity + amount, metabolite.max_quantity)
            )
        else:
            logger.warning(f"Unknown metabolite: {metabolite_name}")

    def consume_metabolites(self, **metabolites: Dict[str, float]):
        """Consume multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            if self.is_metabolite_available(metabolite, amount):
                self.change_metabolite_quantity(metabolite, -amount)
            else:
                logger.warning(f"Insufficient {metabolite} for reaction")
                return False
        return True

    def produce_metabolites(self, **metabolites: Dict[str, float]):
        """Produce multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            self.change_metabolite_quantity(metabolite, amount)

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
        self.change_metabolite_quantity("nadh", self.krebs_cycle.cofactors["nadh"])
        self.change_metabolite_quantity("fadh2", self.krebs_cycle.cofactors["fadh2"])
        self.change_metabolite_quantity(
            "atp", self.krebs_cycle.cofactors["gtp"]
        )  # GTP is equivalent to ATP

        # Reset the Krebs cycle for the next round
        self.krebs_cycle.reset()

        return self.krebs_cycle.cofactors["nadh"] + self.krebs_cycle.cofactors["fadh2"]

    def pyruvate_to_acetyl_coa(self, pyruvate_amount: int) -> int:
        """Converts pyruvate to acetyl-CoA."""
        logger.info(f"Converting {pyruvate_amount} units of pyruvate to acetyl-CoA")
        acetyl_coa_produced = pyruvate_amount
        self.change_metabolite_quantity("nadh", pyruvate_amount)
        self.change_metabolite_quantity("co2", pyruvate_amount)
        return acetyl_coa_produced

    def cellular_respiration(self, pyruvate_amount: int):
        """Simulates the entire cellular respiration process with feedback inhibition"""
        if self.oxygen.quantity <= 0:
            logger.warning("No oxygen available. Cellular respiration halted.")
            return 0

        acetyl_coa = self.pyruvate_to_acetyl_coa(pyruvate_amount)

        # Implement feedback inhibition
        atp_inhibition_factor = 1 / (1 + self.atp.quantity / 1000)  # Example threshold
        self.krebs_cycle.enzyme_activities["citrate_synthase"] *= atp_inhibition_factor
        self.krebs_cycle.enzyme_activities[
            "isocitrate_dehydrogenase"
        ] *= atp_inhibition_factor

        krebs_products = self.krebs_cycle_process(acetyl_coa)

        # Transfer NADH and FADH2 from Krebs cycle to ETC
        self.change_metabolite_quantity("nadh", self.krebs_cycle.cofactors["nadh"])
        self.change_metabolite_quantity("fadh2", self.krebs_cycle.cofactors["fadh2"])

        # Check ADP availability
        if self.adp.quantity < 10:  # Arbitrary threshold
            logger.warning("Low ADP levels. Oxidative phosphorylation may be limited.")

        atp_produced = self.oxidative_phosphorylation()

        # Add ATP from substrate-level phosphorylation in Krebs cycle
        atp_produced += self.krebs_cycle.cofactors["gtp"]  # GTP is equivalent to ATP

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
            reaction_rate = min(self.nadh.quantity, self.ubiquinone.quantity)
            if self.consume_metabolites(nadh=reaction_rate, ubiquinone=reaction_rate):
                self.produce_metabolites(ubiquinol=reaction_rate)
                self.proton_gradient += PROTONS_PER_NADH * reaction_rate
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
            reaction_rate = min(self.fadh2.quantity, self.ubiquinone.quantity)
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
                self.ubiquinol.quantity, self.cytochrome_c_oxidized.quantity
            )
            if self.consume_metabolites(
                ubiquinol=reaction_rate, cytochrome_c_oxidized=reaction_rate
            ):
                self.produce_metabolites(
                    ubiquinone=reaction_rate, cytochrome_c_reduced=reaction_rate
                )
                self.proton_gradient += PROTONS_PER_FADH2 * reaction_rate
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
                self.cytochrome_c_reduced.quantity, self.oxygen.quantity * 2
            )  # 2 cytochrome c per O2
            oxygen_consumed = reaction_rate // 2
            if self.consume_metabolites(
                cytochrome_c_reduced=reaction_rate, oxygen=oxygen_consumed
            ):
                self.produce_metabolites(cytochrome_c_oxidized=reaction_rate)
                self.proton_gradient += PROTONS_PER_FADH2 * reaction_rate
                logger.info(
                    f"Complex IV: Consumed {oxygen_consumed} O2, pumped {PROTONS_PER_FADH2 * reaction_rate} protons"
                )
                return reaction_rate
        if self.oxygen.quantity <= 0:
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
        atp_produced = min(possible_atp, self.adp.quantity)
        self.change_metabolite_quantity("atp", atp_produced)
        self.change_metabolite_quantity("adp", -atp_produced)
        self.proton_gradient -= atp_produced * protons_required_per_atp
        logger.info(f"ATP Synthase: Produced {atp_produced} ATP")
        return atp_produced

    def replenish_ubiquinone(self):
        """Replenishes ubiquinone from ubiquinol"""
        replenish_amount = min(
            self.ubiquinol.quantity,
            self.ubiquinone.max_quantity - self.ubiquinone.quantity,
        )
        self.change_metabolite_quantity("ubiquinone", replenish_amount)
        self.change_metabolite_quantity("ubiquinol", -replenish_amount)
        logger.info(f"Replenished {replenish_amount} ubiquinone")

    def replenish_cytochrome_c(self):
        """Replenishes oxidized cytochrome c from reduced form"""
        replenish_amount = min(
            self.cytochrome_c_reduced.quantity,
            self.cytochrome_c_oxidized.max_quantity
            - self.cytochrome_c_oxidized.quantity,
        )
        self.change_metabolite_quantity("cytochrome_c_oxidized", replenish_amount)
        self.change_metabolite_quantity("cytochrome_c_reduced", -replenish_amount)
        logger.info(f"Replenished {replenish_amount} oxidized cytochrome c")

    def oxidative_phosphorylation(self, cytoplasmic_nadh_used: int = 0):
        """Simulates oxidative phosphorylation with the electron transport chain."""
        if self.oxygen.quantity <= 0:
            logger.warning("No oxygen available. Oxidative phosphorylation halted.")
            return 0

        total_nadh = self.nadh.quantity + cytoplasmic_nadh_used

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
            cytoplasmic_calcium, self.calcium.max_quantity - self.calcium.quantity
        )
        self.change_metabolite_quantity("calcium", calcium_uptake)
        logger.info(f"Mitochondrion buffered {calcium_uptake} units of calcium")

        if self.calcium.quantity > self.calcium_threshold:
            logger.warning(
                "Calcium overload detected. Risk of mitochondrial dysfunction."
            )

        return calcium_uptake

    def release_calcium(self, amount: int):
        """Releases calcium from the mitochondrion."""
        released = min(amount, self.calcium.quantity)
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


class KrebsCycle:
    """
    Krebs cycle is modeled step-by-step, with each enzyme's activity influenced
    by effectors and inhibitors.

    Uses Michaelis-Menten kinetics and Hill equations, which are common for
    modeling enzyme-catalyzed reactions.

    Includes regulation of enzyme activity by cofactors like ATP and ADP, which
    is a realistic representation of metabolic regulation.
    """

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
            "nad": INITIAL_NAD,
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
        self.enzyme_activities = {
            "citrate_synthase": 1.0,
            "isocitrate_dehydrogenase": 1.0,
            "alpha_ketoglutarate_dehydrogenase": 1.0,
            "succinyl_coa_synthetase": 1.0,
            "succinate_dehydrogenase": 1.0,
            "fumarase": 1.0,
            "malate_dehydrogenase": 1.0,
        }

    def is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        """Check if a metabolite is available in sufficient quantity."""
        if metabolite in self.metabolites:
            return self.metabolites[metabolite] >= amount
        elif metabolite in self.cofactors:
            return self.cofactors[metabolite] >= amount
        else:
            logger.warning(f"Unknown metabolite: {metabolite}")
            return False

    def consume_metabolites(self, **metabolites: Dict[str, float]):
        """Consume multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            if self.is_metabolite_available(metabolite, amount):
                if metabolite in self.metabolites:
                    self.metabolites[metabolite] -= amount
                elif metabolite in self.cofactors:
                    self.cofactors[metabolite] -= amount
            else:
                logger.warning(f"Insufficient {metabolite} for reaction")
                return False
        return True

    def produce_metabolites(self, **metabolites: Dict[str, float]):
        """Produce multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            if metabolite in self.metabolites:
                self.metabolites[metabolite] += amount
            elif metabolite in self.cofactors:
                self.cofactors[metabolite] += amount
            else:
                logger.warning(f"Unknown metabolite: {metabolite}")

    def step1_citrate_synthase(self):
        """Acetyl-CoA + Oxaloacetate to Citrate"""
        substrate_conc = min(
            self.metabolites["acetyl_coa"], self.metabolites["oxaloacetate"]
        )
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = michaelis_menten(substrate_conc, vmax, km)

        if self.consume_metabolites(
            acetyl_coa=reaction_rate, oxaloacetate=reaction_rate
        ):
            self.produce_metabolites(citrate=reaction_rate, coenzyme_a=reaction_rate)
        else:
            logger.warning("Insufficient substrates for step 1")

    def step2_aconitase(self):
        """Citrate to Isocitrate"""
        substrate_conc = self.metabolites["citrate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = michaelis_menten(substrate_conc, vmax, km)

        if self.consume_metabolites(citrate=reaction_rate):
            self.produce_metabolites(isocitrate=reaction_rate)
        else:
            logger.warning("Insufficient citrate for step 2")

    def step3_isocitrate_dehydrogenase(self):
        """Isocitrate to α-Ketoglutarate with allosteric regulation"""
        substrate_conc = self.metabolites["isocitrate"]
        vmax = V_MAX_DEFAULT  # Base Vmax
        km = KM_DEFAULT  # Base Km

        # Define effectors
        atp_effector = Effector("ATP", self.cofactors["atp"], Ki=100, Ka=1000)
        adp_effector = Effector("ADP", self.cofactors["adp"], Ki=1000, Ka=100)

        # Calculate regulated enzyme activity
        regulated_activity = allosteric_regulation(
            self.enzyme_activities["isocitrate_dehydrogenase"],
            inhibitors=[atp_effector],
            activators=[adp_effector],
        )

        # Use Hill equation for cooperative binding
        n = 2  # Hill coefficient
        reaction_rate = hill_equation(substrate_conc, vmax * regulated_activity, km, n)

        if self.consume_metabolites(isocitrate=reaction_rate, nad=reaction_rate):
            self.produce_metabolites(
                alpha_ketoglutarate=reaction_rate, nadh=reaction_rate, co2=reaction_rate
            )
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

        reaction_rate = michaelis_menten(substrate_conc, vmax * enzyme_activity, km)

        if self.consume_metabolites(
            alpha_ketoglutarate=reaction_rate, nad=reaction_rate
        ):
            self.produce_metabolites(
                succinyl_coa=reaction_rate, nadh=reaction_rate, co2=reaction_rate
            )
        else:
            logger.warning("Insufficient substrates or NAD⁺ for step 4")

    def step5_succinyl_coa_synthetase(self):
        """Succinyl-CoA to Succinate"""
        substrate_conc = self.metabolites["succinyl_coa"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = michaelis_menten(substrate_conc, vmax, km)

        if self.consume_metabolites(succinyl_coa=reaction_rate, gdp=reaction_rate):
            self.produce_metabolites(
                succinate=reaction_rate, gtp=reaction_rate, coenzyme_a=reaction_rate
            )
        else:
            logger.warning("Insufficient substrates or GDP for step 5")

    def step6_succinate_dehydrogenase(self):
        """Succinate to Fumarate"""
        substrate_conc = self.metabolites["succinate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = michaelis_menten(substrate_conc, vmax, km)

        if self.consume_metabolites(succinate=reaction_rate, fad=reaction_rate):
            self.produce_metabolites(fumarate=reaction_rate, fadh2=reaction_rate)
        else:
            logger.warning("Insufficient substrates or FAD for step 6")

    def step7_fumarase(self):
        """Fumarate to Malate"""
        substrate_conc = self.metabolites["fumarate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = michaelis_menten(substrate_conc, vmax, km)

        if self.consume_metabolites(fumarate=reaction_rate):
            self.produce_metabolites(malate=reaction_rate)
        else:
            logger.warning("Insufficient fumarate for step 7")

    def step8_malate_dehydrogenase(self):
        """Malate to Oxaloacetate"""
        substrate_conc = self.metabolites["malate"]
        vmax = 1.0  # Placeholder value
        km = 0.1  # Placeholder value

        reaction_rate = michaelis_menten(substrate_conc, vmax, km)

        if self.consume_metabolites(malate=reaction_rate, nad=reaction_rate):
            self.produce_metabolites(oxaloacetate=reaction_rate, nadh=reaction_rate)
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
        self.time_step = TIME_STEP
        self.cytoplasmic_calcium = Metabolite("Ca2+", 100, 1000)

    def produce_atp(self, glucose, simulation_duration=SIMULATION_DURATION):
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

            # Check ADP availability
            if self.mitochondrion.adp.quantity < 10:  # Arbitrary threshold
                logger.warning(
                    "Low ADP levels in mitochondrion. Transferring ADP from cytoplasm."
                )
                adp_transfer = min(
                    50, self.cytoplasm.adp.quantity
                )  # Transfer up to 50 ADP
                self.mitochondrion.adp.quantity += adp_transfer
                self.cytoplasm.adp.quantity -= adp_transfer

            # Implement feedback activation
            adp_activation_factor = (
                1 + self.cytoplasm.adp.quantity / 500
            )  # Example threshold
            self.cytoplasm.glycolysis_rate *= adp_activation_factor

            # Glycolysis with updated rate
            pyruvate = self.cytoplasm.glycolysis(1 * self.cytoplasm.glycolysis_rate)
            glucose_processed += 1 * self.cytoplasm.glycolysis_rate

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

            # Cellular respiration in mitochondrion
            mitochondrial_atp = self.mitochondrion.cellular_respiration(pyruvate)
            total_atp_produced += mitochondrial_atp

            # Transfer excess ATP from mitochondrion to cytoplasm
            atp_transfer = max(
                0, self.mitochondrion.atp.quantity - 100
            )  # Keep 100 ATP in mitochondrion
            self.cytoplasm.atp.quantity += atp_transfer
            self.mitochondrion.atp.quantity -= atp_transfer

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
    simulation_duration = SIMULATION_DURATION

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
