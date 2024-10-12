import logging
import math
from enum import Enum
from typing import Dict, List

from .constants import *
from .data import Effector, Enzyme
from .exceptions import *
from .organelle import Organelle

logger = logging.getLogger(__name__)


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

    def change_metabolite_quantity(self, metabolite_name: str, amount: float):
        """Centralized method to change metabolite quantities."""
        if metabolite_name in self.metabolites:
            metabolite = self.metabolites[metabolite_name]
            metabolite.quantity = max(
                0, min(metabolite.quantity + amount, metabolite.max_quantity)
            )
        else:
            logger.warning(f"Unknown metabolite: {metabolite_name}")

    def consume_metabolites(self, **metabolites: Dict[str, float]):
        """Consume multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            if self.is_metabolite_available(metabolite, amount):
                self.metabolites[metabolite].quantity -= amount
            else:
                logger.warning(f"Insufficient {metabolite} for reaction")
                return False
        return True

    def produce_metabolites(self, **metabolites: Dict[str, float]):
        """Produce multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            self.metabolites[metabolite].quantity += amount

    def krebs_cycle_process(self, acetyl_coa_amount: int):
        """Processes acetyl-CoA through the Krebs cycle"""
        logger.info(
            f"Processing {acetyl_coa_amount} units of acetyl-CoA through the Krebs cycle"
        )

        self.krebs_cycle.add_substrate("Acetyl-CoA", acetyl_coa_amount)

        # Ensure there's enough oxaloacetate to start the cycle
        if self.metabolites["oxaloacetate"].quantity < acetyl_coa_amount:
            self.krebs_cycle.add_substrate(
                "oxaloacetate",
                acetyl_coa_amount - self.metabolites["oxaloacetate"].quantity,
            )

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
        self.change_metabolite_quantity("nadh", total_nadh)
        self.change_metabolite_quantity("fadh2", total_fadh2)
        self.change_metabolite_quantity("atp", total_atp)

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

        atp_produced = self.oxidative_phosphorylation()

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
                self.metabolites["cytochrome_c_reduced"].quantity,
                self.metabolites["oxygen"].quantity * 2,
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
        self.change_metabolite_quantity("atp", atp_produced)
        self.change_metabolite_quantity("adp", -atp_produced)
        self.proton_gradient -= atp_produced * protons_required_per_atp
        logger.info(f"ATP Synthase: Produced {atp_produced} ATP")
        return atp_produced

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


class KrebsCycle(Organelle):
    name = "Krebs Cycle"
    """
    Krebs cycle is modeled step-by-step, with each enzyme's activity influenced
    by effectors and inhibitors.

    Uses Michaelis-Menten kinetics and Hill equations, which are common for
    modeling enzyme-catalyzed reactions.

    Includes regulation of enzyme activity by cofactors like ATP and ADP, which
    is a realistic representation of metabolic regulation.
    """

    def __init__(self):
        super().__init__()
        self.add_metabolite("Acetyl-CoA", 0, 1000)
        self.add_metabolite("Oxaloacetate", 0, 1000)
        self.add_metabolite("Citrate", 0, 1000)
        self.add_metabolite("Isocitrate", 0, 1000)
        self.add_metabolite("α-Ketoglutarate", 0, 1000)
        self.add_metabolite("Succinyl-CoA", 0, 1000)
        self.add_metabolite("Succinate", 0, 1000)
        self.add_metabolite("Fumarate", 0, 1000)
        self.add_metabolite("Malate", 0, 1000)

        self.cofactors = {
            "NAD": INITIAL_NAD,
            "NADH": 0,
            "FAD": 100,
            "FADH2": 0,
            "Coenzyme-A": 100,
            "ATP": 100,
            "ADP": 0,
            "GTP": 0,
            "GDP": 0,
            "CO2": 0,
        }
        self.enzymes = {
            "citrate_synthase": Enzyme("Citrate Synthase"),
            "aconitase": Enzyme("Aconitase"),
            "isocitrate_dehydrogenase": Enzyme("Isocitrate Dehydrogenase"),
            "alpha_ketoglutarate_dehydrogenase": Enzyme(
                "α-Ketoglutarate Dehydrogenase"
            ),
            "succinyl_coa_synthetase": Enzyme("Succinyl-CoA Synthetase"),
            "succinate_dehydrogenase": Enzyme("Succinate Dehydrogenase"),
            "fumarase": Enzyme("Fumarase"),
            "malate_dehydrogenase": Enzyme("Malate Dehydrogenase"),
        }

    def is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        """Check if a metabolite is available in sufficient quantity."""
        if metabolite in self.metabolites:
            return self.metabolites[metabolite].quantity >= amount
        elif metabolite in self.cofactors:
            return self.cofactors[metabolite] >= amount
        else:
            logger.warning(f"Unknown metabolite: {metabolite}")
            return False

    def consume_metabolites(self, **metabolites: Dict[str, float]):
        """Consume multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise TypeError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise TypeError("Amounts must be numbers.")
            if amount < 0:
                raise ValueError(f"Cannot consume a negative amount of {metabolite}.")
            if metabolite not in self.metabolites and metabolite not in self.cofactors:
                raise ValueError(f"Unknown metabolite: {metabolite}")
            if self.is_metabolite_available(metabolite, amount):
                if metabolite in self.metabolites:
                    self.metabolites[metabolite].quantity -= amount
                elif metabolite in self.cofactors:
                    self.cofactors[metabolite] -= amount
            else:
                raise ValueError(f"Insufficient {metabolite} for reaction")
        return True

    def produce_metabolites(self, **metabolites: Dict[str, float]):
        """Produce multiple metabolites at once."""
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise TypeError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise TypeError("Amounts must be numbers.")
            if amount < 0:
                raise ValueError(f"Cannot produce a negative amount of {metabolite}.")
            if metabolite in self.metabolites:
                new_quantity = self.metabolites[metabolite].quantity + amount
                if new_quantity > self.metabolites[metabolite].max_quantity:
                    raise ValueError(
                        f"Cannot exceed max quantity for {metabolite}. Attempted to set {metabolite} to {new_quantity}, but max is {self.metabolites[metabolite].max_quantity}."
                    )
                self.metabolites[metabolite].quantity = new_quantity
            elif metabolite in self.cofactors:
                self.cofactors[metabolite] += amount
            else:
                raise ValueError(f"Unknown metabolite: {metabolite}")
        return True

    def step1_citrate_synthase(self):
        """Acetyl-CoA + Oxaloacetate to Citrate"""
        enzyme = self.enzymes["citrate_synthase"]
        substrate_conc = min(
            self.metabolites["Acetyl-CoA"].quantity,
            self.metabolites["Oxaloacetate"].quantity,
        )
        reaction_rate = michaelis_menten(
            substrate_conc, enzyme.vmax * enzyme.activity, enzyme.km
        )

        if self.consume_metabolites(
            **{"Acetyl-CoA": reaction_rate, "Oxaloacetate": reaction_rate}
        ):
            self.produce_metabolites(Citrate=reaction_rate)
            self.cofactors["Coenzyme-A"] += reaction_rate
            return True
        else:
            logger.warning("Insufficient substrates for step 1")
            return False

    def step2_aconitase(self):
        """Citrate to Isocitrate"""
        enzyme = self.enzymes["aconitase"]
        substrate_conc = self.metabolites["Citrate"].quantity
        reaction_rate = michaelis_menten(
            substrate_conc, enzyme.vmax * enzyme.activity, enzyme.km
        )

        if self.consume_metabolites(Citrate=reaction_rate):
            self.produce_metabolites(Isocitrate=reaction_rate)
        else:
            logger.warning("Insufficient Citrate for step 2")

    def step3_isocitrate_dehydrogenase(self):
        """Isocitrate to α-Ketoglutarate"""
        enzyme = self.enzymes["isocitrate_dehydrogenase"]
        substrate_conc = self.metabolites["Isocitrate"].quantity

        # Define effectors
        atp_effector = Effector("ATP", self.cofactors["ATP"], Ki=100, Ka=1000)
        adp_effector = Effector("ADP", self.cofactors["ADP"], Ki=1000, Ka=100)

        # Calculate regulated enzyme activity
        regulated_activity = allosteric_regulation(
            enzyme.activity,
            inhibitors=[atp_effector],
            activators=[adp_effector],
        )

        # Use Hill equation for cooperative binding
        n = 2  # Hill coefficient
        reaction_rate = hill_equation(
            substrate_conc, enzyme.vmax * regulated_activity, enzyme.km, n
        )

        if self.consume_metabolites(Isocitrate=reaction_rate, NAD=reaction_rate):
            self.produce_metabolites(
                **{
                    "α-Ketoglutarate": reaction_rate,
                    "NADH": reaction_rate,
                    "CO2": reaction_rate,
                }
            )
        else:
            logger.warning("Insufficient substrates or NAD⁺ for step 3")

    def step4_alpha_ketoglutarate_dehydrogenase(self):
        """α-Ketoglutarate to Succinyl-CoA"""
        enzyme = self.enzymes["alpha_ketoglutarate_dehydrogenase"]
        substrate_conc = self.metabolites["α-Ketoglutarate"].quantity

        # Enzyme regulation
        atp_inhibition = self.cofactors["ATP"] / 100
        nadh_inhibition = self.cofactors["NADH"] / 100
        succinyl_coa_inhibition = self.metabolites["Succinyl-CoA"].quantity / 10
        enzyme_activity = (
            1 - (atp_inhibition + nadh_inhibition + succinyl_coa_inhibition) / 3
        )

        reaction_rate = michaelis_menten(
            substrate_conc,
            enzyme.vmax * enzyme_activity * enzyme.activity,
            enzyme.km,
        )

        if self.consume_metabolites(
            **{"α-Ketoglutarate": reaction_rate, "NAD": reaction_rate}
        ):
            self.produce_metabolites(
                **{
                    "Succinyl-CoA": reaction_rate,
                    "NADH": reaction_rate,
                    "CO2": reaction_rate,
                }
            )
        else:
            logger.warning("Insufficient substrates or NAD⁺ for step 4")

    def step5_succinyl_coa_synthetase(self):
        """Succinyl-CoA to Succinate"""
        enzyme = self.enzymes["succinyl_coa_synthetase"]
        substrate_conc = self.metabolites["Succinyl-CoA"].quantity
        reaction_rate = michaelis_menten(
            substrate_conc, enzyme.vmax * enzyme.activity, enzyme.km
        )

        if self.consume_metabolites(
            **{"Succinyl-CoA": reaction_rate, "GDP": reaction_rate}
        ):
            self.produce_metabolites(
                Succinate=reaction_rate,
                GTP=reaction_rate,
                **{"Coenzyme-A": reaction_rate},
            )
        else:
            logger.warning("Insufficient substrates or GDP for step 5")

    def step6_succinate_dehydrogenase(self):
        """Succinate to Fumarate"""
        enzyme = self.enzymes["succinate_dehydrogenase"]
        substrate_conc = self.metabolites["Succinate"].quantity
        reaction_rate = michaelis_menten(
            substrate_conc, enzyme.vmax * enzyme.activity, enzyme.km
        )

        if self.consume_metabolites(Succinate=reaction_rate, FAD=reaction_rate):
            self.produce_metabolites(Fumarate=reaction_rate, FADH2=reaction_rate)
        else:
            logger.warning("Insufficient substrates or FAD for step 6")

    def step7_fumarase(self):
        """Fumarate to Malate"""
        enzyme = self.enzymes["fumarase"]
        substrate_conc = self.metabolites["Fumarate"].quantity
        reaction_rate = michaelis_menten(
            substrate_conc, enzyme.vmax * enzyme.activity, enzyme.km
        )

        if self.consume_metabolites(Fumarate=reaction_rate):
            self.produce_metabolites(Malate=reaction_rate)
        else:
            logger.warning("Insufficient Fumarate for step 7")

    def step8_malate_dehydrogenase(self):
        """Malate to Oxaloacetate"""
        enzyme = self.enzymes["malate_dehydrogenase"]
        substrate_conc = self.metabolites["Malate"].quantity
        reaction_rate = michaelis_menten(
            substrate_conc, enzyme.vmax * enzyme.activity, enzyme.km
        )

        if self.consume_metabolites(Malate=reaction_rate, NAD=reaction_rate):
            self.produce_metabolites(Oxaloacetate=reaction_rate, NADH=reaction_rate)
        else:
            logger.warning("Insufficient substrates or NAD⁺ for step 8")

    def run_cycle(self):
        if self.metabolites["Acetyl-CoA"].quantity > 0:
            self.step1_citrate_synthase()
            self.step2_aconitase()
            self.step3_isocitrate_dehydrogenase()
            self.step4_alpha_ketoglutarate_dehydrogenase()
            self.step5_succinyl_coa_synthetase()
            self.step6_succinate_dehydrogenase()
            self.step7_fumarase()
            self.step8_malate_dehydrogenase()
        else:
            logger.warning("Insufficient Acetyl-CoA to start Krebs cycle")

    def krebs_cycle_iterator(self, num_cycles: int = None):
        """Generator that yields the state after each Krebs cycle."""
        cycles_run = 0
        while num_cycles is None or cycles_run < num_cycles:
            self.run_cycle()
            cycles_run += 1
            yield self.metabolites.copy(), self.cofactors.copy()

    def add_substrate(self, substrate: str, amount: float):
        """Add initial substrate to start the cycle"""
        if not isinstance(substrate, str):
            raise TypeError("Substrate name must be a string.")
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        if substrate == "Acetyl-CoA":
            self.metabolites["Acetyl-CoA"].quantity += amount
        elif substrate in self.metabolites:
            self.metabolites[substrate].quantity += amount
        elif substrate in self.cofactors:
            self.cofactors[substrate] += amount
        else:
            raise ValueError(f"Unknown substrate: {substrate}")

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

    def metabolite_iterator(self):
        """Generator that yields each metabolite name and quantity in the Krebs cycle."""
        for metabolite_name, metabolite in self.metabolites.items():
            yield metabolite_name, metabolite.quantity

    def reaction_iterator(self):
        """Generator that yields each reaction step in the Krebs cycle."""
        reactions = [
            self.step1_citrate_synthase,
            self.step2_aconitase,
            self.step3_isocitrate_dehydrogenase,
            self.step4_alpha_ketoglutarate_dehydrogenase,
            self.step5_succinyl_coa_synthetase,
            self.step6_succinate_dehydrogenase,
            self.step7_fumarase,
            self.step8_malate_dehydrogenase,
        ]
        for reaction in reactions:
            yield reaction.__name__, reaction()

    def run_cycle_with_generators(self):
        """Runs the Krebs cycle using generators for finer control."""
        logger.info("Starting Krebs cycle with generators")

        for reaction_name, result in self.reaction_iterator():
            logger.info(f"Completed {reaction_name}")

            # You can process the result here if needed
            # For example, you might want to check if the reaction was successful
            if result is False:
                logger.warning(f"{reaction_name} failed due to insufficient substrates")
                break

            # After each reaction, you can check the state of metabolites
            logger.info("Current metabolite state:")
            for metabolite, quantity in self.metabolite_iterator():
                logger.info(f"  {metabolite}: {quantity:.2f}")

            # You can also add additional logic here, such as:
            # - Checking for rate-limiting steps
            # - Applying regulatory effects
            # - Pausing or modifying the cycle based on certain conditions

        logger.info("Krebs cycle complete")
