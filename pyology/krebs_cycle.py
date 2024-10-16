import logging
from typing import Dict

from pyology.organelle import Organelle

from .constants import INITIAL_NAD
from .data import Effector, Enzyme
from .utils import michaelis_menten, allosteric_regulation, hill_equation

logger = logging.getLogger(__name__)


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
            logger.info(f"Citrate synthase: Produced {reaction_rate} Citrate")
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
