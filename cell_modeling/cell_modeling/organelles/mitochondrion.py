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
        logger.info("Mitochondrion initialized")

    def electron_transport_chain(self) -> None:
        """
        Simulates the transfer of electrons from NADH and FADH2 to oxygen,
        pumping protons across the mitochondrial membrane and generating a proton
        gradient that drives ATP synthesis.
        """
        protons_pumped = 0

        # Complex I: NADH to Ubiquinone
        if self.nadh > 0:
            protons_pumped += 4  # 4 H+ per NADH
            self.nadh -= 1

        # Complex II: FADH2 to Ubiquinone (no protons pumped)
        if self.fadh2 > 0:
            self.fadh2 -= 1

        # Complex III: Ubiquinol to Cytochrome c
        protons_pumped += 4  # 4 H+ per cycle

        # Complex IV: Cytochrome c to Oxygen
        protons_pumped += 2  # 2 H+ per 1/2 O2 reduced

        # Add some variability to the proton gradient
        protons_pumped += random.randint(-1, 1)

        self.proton_gradient += protons_pumped
        logger.debug(f"Proton gradient after ETC: {self.proton_gradient}")

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
        # Initial ATP investment
        self.atp -= glucose_amount * 2
        # Net ATP production
        atp_produced = glucose_amount * 4
        self.atp += atp_produced
        # NADH production
        self.nadh += glucose_amount * 2
        pyruvate = glucose_amount * 2  # Each glucose yields 2 pyruvate molecules
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
            self.nadh += 4  # 3 NADH from Krebs cycle + 1 from pyruvate dehydrogenase
            self.fadh2 += 1  # 1 FADH2 per pyruvate

        logger.debug(
            f"After Krebs cycle: ATP: {self.atp}, NADH: {self.nadh}, FADH2: {self.fadh2}"
        )

    def oxidative_phosphorylation(self) -> None:
        """
        Simulates the oxidative phosphorylation process using the electron
        transport chain and ATP synthase, including proton leak and gradual ATP
        production.
        """
        logger.info("Performing oxidative phosphorylation")
        total_atp_produced = 0

        while self.nadh > 0 or self.fadh2 > 0:
            # Run the electron transport chain
            self.electron_transport_chain()

            # Simulate proton leak
            leaked_protons = int(self.proton_gradient * self.proton_leak_rate)
            self.proton_gradient -= leaked_protons
            logger.debug(f"Protons leaked: {leaked_protons}")

            # Simulate ATP synthase using the proton gradient
            while self.proton_gradient >= 3:  # 3 protons minimum for ATP production
                protons_used = 3
                atp_produced = 1 * self.atp_synthase_efficiency
                self.atp += atp_produced
                total_atp_produced += atp_produced
                self.proton_gradient -= protons_used

        # Round the total ATP produced to the nearest whole number
        total_atp_produced = round(total_atp_produced)
        self.atp = round(self.atp)

        logger.info(f"ATP produced in oxidative phosphorylation: {total_atp_produced}")
        logger.debug(f"Remaining proton gradient: {self.proton_gradient}")

    def produce_atp(self, glucose_amount: int) -> int:
        """
        Simulates the production of ATP from glucose.

        ATP is produced in three steps:
            1. Glycolysis: Glucose is broken down into pyruvate, producing 2 ATP
                per glucose.
            2. Krebs cycle: Pyruvate is converted into acetyl-CoA, producing 1
                ATP per pyruvate.
            3. Oxidative phosphorylation: The electron transport chain and ATP
                synthase are used to produce ATP from ADP and inorganic phosphate.

        Parameters
        ----------
        glucose_amount : int
            The amount of glucose to be used for ATP production. Comes from the
            cytosol. Comes from the glycolysis.

        Returns
        -------
        int
            The amount of ATP produced. Used for the cytosol.
        """
        pyruvate: int = self.glycolysis(glucose_amount)
        self.krebs_cycle(pyruvate)
        self.oxidative_phosphorylation()
        logger.info(f"Total ATP produced: {self.atp}")
        return self.atp

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
        mito.produce_atp(glucose)

        # Log the current state of the mitochondrion
        logger.info(f"Current ATP: {mito.atp}")
        logger.info(f"Remaining NADH: {mito.nadh}")
        logger.info(f"Remaining FADH2: {mito.fadh2}")
        logger.info(f"Remaining proton gradient: {mito.proton_gradient}")

        # Reset the mitochondrion for the next simulation
        mito.atp = 0
        mito.nadh = 0
        mito.fadh2 = 0
        mito.proton_gradient = 0

    logger.info("Simulation complete.")
