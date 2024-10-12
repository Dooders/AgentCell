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
import random
from dataclasses import dataclass

from organelle import Organelle

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class Metabolite:
    name: str
    quantity: int  # in molecules
    max_quantity: int


class Cytoplasm:
    def __init__(self):
        self.glucose = 0
        self.pyruvate = 0
        self.atp = Metabolite("ATP", 0, 100)
        self.nadh = 0

    def glycolysis(self, glucose_amount: int) -> int:
        """
        Simulates the glycolysis of glucose in the cytoplasm.

        Parameters
        ----------
        glucose_amount : int
            The amount of glucose to be glycolysed.

        Returns
        -------
        int
            The amount of pyruvate produced.
        """
        logger.info(f"Glycolysis of {glucose_amount} units of glucose in cytoplasm")
        # Net ATP production (2 ATP per glucose)
        atp_produced = glucose_amount * 2
        self.atp.quantity += atp_produced
        # NADH production (2 NADH per glucose)
        self.nadh += glucose_amount * 2
        self.pyruvate += glucose_amount * 2
        return self.pyruvate


class Mitochondrion(Organelle):
    name = "Mitochondrion"
    """
    Represents the mitochondrion, a double-membrane organelle with inner folds
    called cristae that generates ATP through cellular respiration.

    Methods
    -------
    electron_transport_chain : None
        Simulates the transfer of electrons from NADH and FADH2 to oxygen,
        pumping protons across the mitochondrial membrane and generating a proton
        gradient that drives ATP synthesis.
    glycolysis : int
        Simulates the glycolysis of glucose.
    krebs_cycle : None
        Simulates the Krebs cycle processing of pyruvate.
    oxidative_phosphorylation : None
        Simulates the oxidative phosphorylation process using the electron transport
        chain and ATP synthase, including proton leak and gradual ATP production.
    produce_atp : int
        Simulates the production of ATP from glucose.
    function : str
        Implement the main function of the mitochondrion.
    """

    def __init__(self) -> None:
        self.nadh = Metabolite("NADH", 0, 100)
        self.fadh2 = Metabolite("FADH2", 0, 100)
        self.oxygen = Metabolite(
            "O2", 1_000_000, 100
        )  # Initial oxygen level (1 million molecules)
        self.atp = Metabolite("ATP", 0, 100)
        self.proton_gradient = 0  # in protons
        self.ros = Metabolite("ROS", 0, 100)

        self.nadh_max = 100_000  # Maximum NADH capacity
        self.fadh2_max = 40_000  # Maximum FADH2 capacity
        self.oxygen_threshold = (
            200_000  # Threshold below which ETC efficiency decreases
        )

        self.proton_leak_rate = 0.05  # Base proton leak rate (5%)
        self.membrane_integrity = 1.0  # 1.0 represents full integrity
        self.atp_synthase_efficiency = 0.75  # 75% efficiency in ATP production
        self.proton_pump_efficiency = 1.0  # Starting at 100% efficiency

        self.ros_threshold = 50_000  # Threshold for ROS damage
        self.ros_damage = 0  # Cumulative ROS damage

        self.metabolic_load = 0  # Current metabolic load
        self.max_metabolic_load = 100_000  # Maximum metabolic load

        self.nadh_production_rate = 10  # Add this line with an appropriate value
        self.fadh2_production_rate = 5  # Add this line with an appropriate value

        self.ros_level = 0  # Initialize ROS level to 0

        logger.info("Mitochondrion initialized with updated metabolic parameters")

    def electron_transport_chain(self) -> None:
        """
        Simulates the electron transport chain, pumping protons and consuming oxygen.
        """
        protons_pumped = 0
        efficiency = min(1.0, self.oxygen.quantity / self.oxygen_threshold)
        efficiency *= self.proton_pump_efficiency

        nadh_consumed = min(
            self.nadh.quantity, 1000
        )  # Consume up to 1000 NADH molecules
        fadh2_consumed = min(
            self.fadh2.quantity, 500
        )  # Consume up to 500 FADH2 molecules

        # Oxygen consumption: 0.5 O2 per NADH/FADH2
        oxygen_consumed = (nadh_consumed + fadh2_consumed) // 2

        if nadh_consumed > 0 and self.oxygen.quantity > 0:
            protons_pumped += 10 * efficiency * nadh_consumed
            self.nadh.quantity -= nadh_consumed

        if fadh2_consumed > 0 and self.oxygen.quantity > 0:
            protons_pumped += 6 * efficiency * fadh2_consumed
            self.fadh2.quantity -= fadh2_consumed

        # Adjust proton pumping based on available oxygen
        protons_pumped = min(
            protons_pumped, self.oxygen.quantity * 4
        )  # 4 protons per O2 reduced

        self.proton_gradient += int(protons_pumped)
        self.oxygen.quantity = max(0, self.oxygen.quantity - oxygen_consumed)

        # ROS generation
        electron_leakage = 1 - efficiency
        ros_generated = int(
            (nadh_consumed + fadh2_consumed) * 0.01 * electron_leakage
        )  # 1% ROS generation rate
        ros_generated = min(
            ros_generated, self.oxygen.quantity
        )  # ROS production limited by available oxygen
        self.ros.quantity += ros_generated
        logger.debug(f"ROS generated: {ros_generated} molecules")

        # Update metabolic load
        self.metabolic_load = min(
            self.metabolic_load + nadh_consumed + fadh2_consumed,
            self.max_metabolic_load,
        )

        # Dynamic proton pump efficiency
        load_factor = self.metabolic_load / self.max_metabolic_load
        ros_factor = self.ros.quantity / self.ros_threshold
        self.proton_pump_efficiency = max(
            0.5, 1 - (load_factor * 0.3 + ros_factor * 0.2)
        )

        # ROS damage calculation
        if self.ros.quantity > self.ros_threshold:
            damage = (
                self.ros.quantity - self.ros_threshold
            ) * 0.0001  # 0.01% damage per excess ROS molecule
            self.ros_damage += damage
            self.membrane_integrity = max(0.5, self.membrane_integrity - damage)
            logger.debug(
                f"ROS damage: {damage:.4f}, Total damage: {self.ros_damage:.4f}"
            )
            logger.debug(f"Updated membrane integrity: {self.membrane_integrity:.4f}")

        # Dynamic proton leak rate
        self.proton_leak_rate = (
            0.05 + (1 - self.membrane_integrity) * 0.1 + ros_factor * 0.05
        )

        logger.debug(f"Proton gradient: {self.proton_gradient} protons")
        logger.debug(f"Oxygen remaining: {self.oxygen.quantity} molecules")
        logger.debug(f"Proton pump efficiency: {self.proton_pump_efficiency:.4f}")

    def oxidative_phosphorylation(self) -> None:
        """
        Simulates ATP production through oxidative phosphorylation.
        """
        atp_produced = 0
        protons_leaked = int(self.proton_gradient * self.proton_leak_rate)
        self.proton_gradient -= protons_leaked

        while self.proton_gradient >= 4:
            atp_produced += 1 * self.atp_synthase_efficiency
            self.proton_gradient -= 4

        self.atp.quantity += int(atp_produced)
        logger.info(f"ATP produced: {int(atp_produced)} molecules")

    def pyruvate_to_acetyl_coa(self, pyruvate_amount: int) -> int:
        """
        Simulates the conversion of pyruvate to acetyl-CoA by the pyruvate dehydrogenase complex.

        Parameters
        ----------
        pyruvate_amount : int
            The amount of pyruvate to be converted.

        Returns
        -------
        int
            The amount of acetyl-CoA produced.
        """
        logger.info(f"Converting {pyruvate_amount} units of pyruvate to acetyl-CoA")
        acetyl_coa_produced = pyruvate_amount
        self.nadh.quantity += pyruvate_amount
        if self.nadh.quantity > self.nadh_max:
            self.nadh.quantity = self.nadh_max
        # CO2 production could be tracked here if needed
        logger.debug(f"Acetyl-CoA produced: {acetyl_coa_produced}, NADH: {self.nadh}")
        return acetyl_coa_produced

    def process_pyruvate(self, pyruvate_amount: int) -> None:
        """
        Processes pyruvate received from glycolysis in the cytoplasm.

        Parameters
        ----------
        pyruvate_amount : int
            The amount of pyruvate to be processed.
        """
        logger.info(f"Processing {pyruvate_amount} units of pyruvate from cytoplasm")
        acetyl_coa = self.pyruvate_to_acetyl_coa(pyruvate_amount)
        self.krebs_cycle(acetyl_coa)

    def krebs_cycle(self, acetyl_coa_amount: int) -> None:
        """
        Simulates the Krebs cycle processing of acetyl-CoA.

        The Krebs cycle is a series of chemical reactions that occur in the
        mitochondrial matrix. It uses acetyl-CoA to produce ATP, NADH, and FADH2.

        Parameters
        ----------
        acetyl_coa_amount : int
            The amount of acetyl-CoA to be processed. Comes from pyruvate conversion.
        """
        logger.info(f"Krebs cycle processing {acetyl_coa_amount} units of acetyl-CoA")
        for _ in range(acetyl_coa_amount):
            # Update ATP
            new_atp_quantity = min(self.atp.quantity + 1, self.atp.max_quantity)
            self.atp.quantity = (
                new_atp_quantity  # 1 GTP (equivalent to ATP) per acetyl-CoA
            )

            # Update NADH
            new_nadh_quantity = min(self.nadh.quantity + 3, self.nadh_max)
            self.nadh.quantity = new_nadh_quantity  # 3 NADH per acetyl-CoA

            # Update FADH2
            new_fadh2_quantity = min(self.fadh2.quantity + 1, self.fadh2_max)
            self.fadh2.quantity = new_fadh2_quantity  # 1 FADH2 per acetyl-CoA

        logger.debug(
            f"After Krebs cycle: ATP: {self.atp}, NADH: {self.nadh}, FADH2: {self.fadh2}"
        )

    def update_nadh_fadh2(self) -> None:
        """
        Updates NADH and FADH2 levels based on production rates and maximum capacity.
        """
        self.nadh.quantity = min(
            self.nadh.quantity + self.nadh_production_rate, self.nadh_max
        )
        self.fadh2.quantity = min(
            self.fadh2.quantity + self.fadh2_production_rate, self.fadh2_max
        )
        logger.debug(f"Updated NADH: {self.nadh}, FADH2: {self.fadh2}")

    def function(self) -> str:
        """
        Implement the main function of the mitochondrion.

        Returns
        -------
        str
            A description of the main function of the mitochondrion.
        """
        return "Produce energy through cellular respiration"


class Cell:
    def __init__(self):
        self.cytoplasm = Cytoplasm()
        self.mitochondrion = Mitochondrion()

    def produce_atp(self, glucose_amount: int) -> int:
        """
        Simulates the production of ATP from glucose in the entire cell.
        """
        # Convert self.cytoplasm.atp to a Metabolite object if it's not already
        if isinstance(self.cytoplasm.atp, int):
            self.cytoplasm.atp = Metabolite("ATP", self.cytoplasm.atp, 100)

        initial_atp = self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity

        # Glycolysis in cytoplasm
        pyruvate = self.cytoplasm.glycolysis(glucose_amount)

        # Transfer pyruvate to mitochondrion
        self.mitochondrion.process_pyruvate(pyruvate)

        # Oxidative phosphorylation in mitochondrion
        for _ in range(10):
            self.mitochondrion.oxidative_phosphorylation()
            self.mitochondrion.update_nadh_fadh2()

        total_atp = (
            self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity - initial_atp
        )
        logger.info(f"Total ATP produced in the cell: {total_atp}")
        return total_atp


# Simulation code
if __name__ == "__main__":
    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create a Cell instance
    cell = Cell()

    # Simulate ATP production with different amounts of glucose
    glucose_amounts = [1, 2, 5, 10]

    for glucose in glucose_amounts:
        logger.info(f"\nSimulating ATP production with {glucose} glucose units:")
        cell.produce_atp(glucose)

        # Log the current state of the cell
        logger.info(f"Cytoplasm ATP: {cell.cytoplasm.atp}")
        logger.info(f"Cytoplasm NADH: {cell.cytoplasm.nadh}")
        logger.info(f"Mitochondrion ATP: {cell.mitochondrion.atp}")
        logger.info(f"Mitochondrion NADH: {cell.mitochondrion.nadh}")
        logger.info(f"Mitochondrion FADH2: {cell.mitochondrion.fadh2}")
        logger.info(
            f"Mitochondrion proton gradient: {cell.mitochondrion.proton_gradient}"
        )
        logger.info(f"Mitochondrion oxygen: {cell.mitochondrion.oxygen}")
        logger.info(f"Mitochondrion ROS level: {cell.mitochondrion.ros_level}")
        logger.info(f"Mitochondrion ROS damage: {cell.mitochondrion.ros_damage}")
        logger.info(
            f"Mitochondrion proton pump efficiency: {cell.mitochondrion.proton_pump_efficiency}"
        )

        # Reset the cell for the next simulation
        cell = Cell()

    logger.info("Simulation complete.")
