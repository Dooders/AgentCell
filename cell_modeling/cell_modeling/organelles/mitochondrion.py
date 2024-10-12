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

from organelle import Organelle

# Set up logging
logger = logging.getLogger(__name__)


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
        self.atp = 0
        self.nadh = 0
        self.fadh2 = 0
        self.proton_gradient = 0
        self.proton_leak_rate = 0.05  # Reduced to 5% of protons leak per cycle
        self.atp_synthase_efficiency = (
            0.75  # Adjusted to 75% efficiency in ATP production
        )
        self.oxygen = 100  # Initial oxygen level (arbitrary units)
        self.oxygen_threshold = 20  # Threshold below which ETC efficiency decreases
        self.oxygen_uptake_rate = (
            0.5  # Increased rate of oxygen consumption per glucose unit
        )
        self.ros_level = 0
        self.ros_threshold = 50  # Threshold for ROS damage
        self.ros_damage = 0  # Cumulative ROS damage
        self.proton_pump_efficiency = 1.0  # Starting at 100% efficiency
        self.nadh_production_rate = 10  # NADH produced per glucose unit
        self.fadh2_production_rate = 2  # FADH2 produced per glucose unit
        self.nadh_max = 100  # Increased maximum NADH capacity
        self.fadh2_max = 40  # Increased maximum FADH2 capacity
        self.time_step = 0  # Current time step
        self.metabolic_load = 0  # New variable to track metabolic load
        self.max_metabolic_load = 100  # Maximum metabolic load
        self.atp_yield_per_nadh = 2.5  # Adjusted ATP yield per NADH
        self.atp_yield_per_fadh2 = 1.5  # Adjusted ATP yield per FADH2
        self.ros_generation_rate = (
            0.01  # Rate of ROS generation per NADH/FADH2 consumed
        )
        self.nadh_consumption_rate = 0.2  # Rate of NADH consumption per time step
        self.fadh2_consumption_rate = 0.1  # Rate of FADH2 consumption per time step
        logger.info("Mitochondrion initialized with updated metabolic parameters")

    def update_oxygen(self, amount: float) -> None:
        """
        Updates the oxygen level in the mitochondrion.

        Parameters
        ----------
        amount : float
            The amount of oxygen to add (positive) or remove (negative).
        """
        self.oxygen = max(0, self.oxygen + amount)
        logger.debug(f"Oxygen level updated to: {self.oxygen}")

    def electron_transport_chain(self) -> None:
        """
        Simulates the transfer of electrons from NADH and FADH2 to oxygen,
        pumping protons across the mitochondrial membrane and generating a proton
        gradient that drives ATP synthesis. Accounts for oxygen availability and ROS.
        """
        protons_pumped = 0
        efficiency = min(1.0, self.oxygen / self.oxygen_threshold)
        efficiency *= self.proton_pump_efficiency

        nadh_consumed = min(self.nadh, self.nadh_consumption_rate)
        fadh2_consumed = min(self.fadh2, self.fadh2_consumption_rate)

        oxygen_consumed = (
            nadh_consumed + fadh2_consumed * 0.5
        ) * self.oxygen_uptake_rate

        if nadh_consumed > 0 and self.oxygen > 0:
            protons_pumped += 10 * efficiency * nadh_consumed  # Increased from 4 to 10
            self.nadh -= nadh_consumed

        if fadh2_consumed > 0 and self.oxygen > 0:
            protons_pumped += (
                6 * efficiency * fadh2_consumed
            )  # Added proton pumping for FADH2
            self.fadh2 -= fadh2_consumed

        if self.oxygen > 0:
            protons_pumped += 4 * efficiency  # Complex III
            protons_pumped += 2 * efficiency  # Complex IV

        protons_pumped += random.randint(-1, 1)

        self.proton_gradient += protons_pumped
        self.update_oxygen(-oxygen_consumed)

        # ROS generation based on metabolic activity
        ros_generated = self.ros_generation_rate * (nadh_consumed + fadh2_consumed)
        self.ros_level += ros_generated
        logger.debug(f"ROS generated: {ros_generated}")

        # Update metabolic load
        self.metabolic_load = min(
            self.metabolic_load + (nadh_consumed + fadh2_consumed),
            self.max_metabolic_load,
        )

        # Dynamic proton pump efficiency
        load_factor = self.metabolic_load / self.max_metabolic_load
        ros_factor = self.ros_level / self.ros_threshold
        self.proton_pump_efficiency = max(
            0.5, 1 - (load_factor * 0.3 + ros_factor * 0.2)
        )

        # ROS damage calculation
        if self.ros_level > self.ros_threshold:
            damage = (self.ros_level - self.ros_threshold) * 0.1
            self.ros_damage += damage
            logger.debug(f"ROS damage: {damage}, Total damage: {self.ros_damage}")
            logger.debug(
                f"Updated proton pump efficiency: {self.proton_pump_efficiency}"
            )

        # ROS clearance (simplified)
        self.ros_level = max(0, self.ros_level - random.uniform(0, 1))

    def glycolysis(self, glucose_amount: int) -> int:
        """
        Simulates the glycolysis of glucose.

        Glycolysis is the process of breaking down glucose into pyruvate,
        producing 2 ATP per glucose molecule.

        Parameters
        ----------
        glucose_amount : int
            The amount of glucose to be glycolysed. Comes from the cytosol.
            Comes from the mitochondrion.

        Returns
        -------
        int
            The amount of pyruvate produced. Used for the Krebs cycle.
        """
        logger.info(f"Glycolysis of {glucose_amount} units of glucose")
        # Net ATP production (2 ATP per glucose)
        atp_produced = glucose_amount * 2
        self.atp += atp_produced
        # NADH production (2 NADH per glucose)
        self.nadh = min(self.nadh + glucose_amount * 2, self.nadh_max)
        pyruvate = glucose_amount * 2
        return pyruvate

    def krebs_cycle(self, pyruvate_amount: int) -> None:
        """
        Simulates the Krebs cycle processing of pyruvate.

        The Krebs cycle is a series of chemical reactions that occur in the
        mitochondrial matrix. It converts pyruvate into acetyl-CoA, which is
        then used to produce ATP.

        Parameters
        ----------
        pyruvate_amount : int
            The amount of pyruvate to be processed. Comes from the glycolysis.
            Comes from the mitochondrion.
        """
        logger.info(f"Krebs cycle processing {pyruvate_amount} units of pyruvate")
        for _ in range(pyruvate_amount):
            self.atp += 1  # 1 GTP (equivalent to ATP) per pyruvate
            self.nadh = min(self.nadh + 3, self.nadh_max)  # 3 NADH per pyruvate
            self.fadh2 = min(self.fadh2 + 1, self.fadh2_max)  # 1 FADH2 per pyruvate

        logger.debug(
            f"After Krebs cycle: ATP: {self.atp}, NADH: {self.nadh}, FADH2: {self.fadh2}"
        )

    def oxidative_phosphorylation(self) -> None:
        """
        Simulates the oxidative phosphorylation process using the electron
        transport chain and ATP synthase, including proton leak, gradual ATP
        production, oxygen uptake dynamics, and ROS effects.
        """
        logger.info("Performing oxidative phosphorylation")
        total_atp_produced = 0

        while (self.nadh > 0 or self.fadh2 > 0) and self.oxygen > 0:
            self.electron_transport_chain()

            leaked_protons = int(self.proton_gradient * self.proton_leak_rate)
            self.proton_gradient -= leaked_protons

            while self.proton_gradient >= 3:
                protons_used = 3
                atp_produced = (
                    self.atp_yield_per_nadh * self.nadh_consumption_rate
                    + self.atp_yield_per_fadh2 * self.fadh2_consumption_rate
                ) * self.atp_synthase_efficiency
                self.atp += atp_produced
                total_atp_produced += atp_produced
                self.proton_gradient -= protons_used

        # Round the total ATP produced to the nearest whole number
        total_atp_produced = round(total_atp_produced)
        self.atp = round(self.atp)

        # Gradual decrease in metabolic load
        self.metabolic_load = max(0, self.metabolic_load - 1)

        logger.info(f"ATP produced in oxidative phosphorylation: {total_atp_produced}")
        logger.debug(f"Remaining proton gradient: {self.proton_gradient}")
        logger.debug(f"Remaining oxygen: {self.oxygen}")
        logger.debug(f"Current ROS level: {self.ros_level}")
        logger.debug(f"Cumulative ROS damage: {self.ros_damage}")
        logger.debug(f"Proton pump efficiency: {self.proton_pump_efficiency}")

    def update_nadh_fadh2(self) -> None:
        """
        Updates NADH and FADH2 levels based on production rates and maximum capacity.
        """
        self.nadh = min(self.nadh + self.nadh_production_rate, self.nadh_max)
        self.fadh2 = min(self.fadh2 + self.fadh2_production_rate, self.fadh2_max)
        logger.debug(f"Updated NADH: {self.nadh}, FADH2: {self.fadh2}")

    def produce_atp(self, glucose_amount: int) -> int:
        """
        Simulates the production of ATP from glucose over multiple time steps.
        """
        initial_atp = self.atp
        pyruvate: int = self.glycolysis(glucose_amount)
        self.krebs_cycle(pyruvate)

        oxygen_consumed = glucose_amount * self.oxygen_uptake_rate
        self.update_oxygen(-oxygen_consumed)

        for _ in range(10):
            self.time_step += 1
            self.oxidative_phosphorylation()
            # Replenish some NADH and FADH2 to allow for continued ATP production
            self.nadh = min(self.nadh + self.nadh_production_rate, self.nadh_max)
            self.fadh2 = min(self.fadh2 + self.fadh2_production_rate, self.fadh2_max)

        atp_produced = self.atp - initial_atp
        logger.info(f"Total ATP produced: {atp_produced}")
        return atp_produced

    def function(self) -> str:
        """
        Implement the main function of the mitochondrion.

        Returns
        -------
        str
            A description of the main function of the mitochondrion.
        """
        return "Produce energy through cellular respiration"


# Simulation code
if __name__ == "__main__":
    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create a Mitochondrion instance
    mito = Mitochondrion()

    # Simulate ATP production with different amounts of glucose
    glucose_amounts = [1, 2, 5, 10]

    for glucose in glucose_amounts:
        logger.info(f"\nSimulating ATP production with {glucose} glucose units:")
        initial_atp = mito.atp
        mito.produce_atp(glucose)

        # Log the current state of the mitochondrion
        logger.info(f"ATP produced: {mito.atp - initial_atp}")
        logger.info(f"Remaining NADH: {mito.nadh}")
        logger.info(f"Remaining FADH2: {mito.fadh2}")
        logger.info(f"Remaining proton gradient: {mito.proton_gradient}")
        logger.info(f"Remaining oxygen: {mito.oxygen}")
        logger.info(f"ROS level: {mito.ros_level}")
        logger.info(f"ROS damage: {mito.ros_damage}")
        logger.info(f"Proton pump efficiency: {mito.proton_pump_efficiency}")

        # Reset the mitochondrion for the next simulation
        mito.atp = 0
        mito.nadh = 0
        mito.fadh2 = 0
        mito.proton_gradient = 0
        mito.oxygen = 100  # Reset oxygen level
        mito.ros_level = 0  # Reset ROS level
        mito.ros_damage = 0  # Reset ROS damage
        mito.proton_pump_efficiency = 1.0  # Reset proton pump efficiency
        mito.time_step = 0  # Reset time step

    logger.info("Simulation complete.")
