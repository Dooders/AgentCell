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

from dataclasses import dataclass
import logging
import time

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
        self.atp = Metabolite("ATP", 0, 100)
        self.nadh = Metabolite("NADH", 0, 100)

    def glycolysis(self, glucose_amount: int) -> int:
        """Simulates glycolysis in the cytoplasm."""
        logger.info(f"Glycolysis of {glucose_amount} units of glucose in cytoplasm")
        atp_produced = glucose_amount * 2
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
        self.nadh = Metabolite("NADH", 0, 100)
        self.fadh2 = Metabolite("FADH2", 0, 100)
        self.atp = Metabolite("ATP", 0, 100)
        self.oxygen = Metabolite("O2", 1_000_000, 1_000_000)
        self.proton_gradient = 0
        self.ros = Metabolite("ROS", 0, 100)

        self.atp_synthase_efficiency = 0.9
        self.proton_pump_efficiency = 0.95
        self.nadh_to_atp_ratio = 2.5
        self.fadh2_to_atp_ratio = 1.5
        self.proton_gradient_threshold = 1000

    def pyruvate_to_acetyl_coa(self, pyruvate_amount: int) -> int:
        """Converts pyruvate to acetyl-CoA."""
        logger.info(f"Converting {pyruvate_amount} units of pyruvate to acetyl-CoA")
        acetyl_coa_produced = pyruvate_amount
        self.nadh.quantity = min(
            self.nadh.quantity + pyruvate_amount, self.nadh.max_quantity
        )
        return acetyl_coa_produced

    def krebs_cycle(self, acetyl_coa_amount: int):
        """Simulates the Krebs cycle."""
        logger.info(f"Krebs cycle processing {acetyl_coa_amount} units of acetyl-CoA")
        for _ in range(acetyl_coa_amount):
            self.atp.quantity = min(self.atp.quantity + 1, self.atp.max_quantity)
            self.nadh.quantity = min(self.nadh.quantity + 3, self.nadh.max_quantity)
            self.fadh2.quantity = min(self.fadh2.quantity + 1, self.fadh2.max_quantity)

    def electron_transport_chain(self):
        """Simulates the electron transport chain."""
        efficiency = self.proton_pump_efficiency
        nadh_consumed = min(self.nadh.quantity, 1000)
        fadh2_consumed = min(self.fadh2.quantity, 500)
        oxygen_consumed = (nadh_consumed + fadh2_consumed) // 2
        protons_pumped = int((10 * nadh_consumed + 6 * fadh2_consumed) * efficiency)

        self.proton_gradient += protons_pumped
        self.oxygen.quantity = max(0, self.oxygen.quantity - oxygen_consumed)
        self.nadh.quantity -= nadh_consumed
        self.fadh2.quantity -= fadh2_consumed

    def oxidative_phosphorylation(self):
        """Simulates oxidative phosphorylation."""
        if self.proton_gradient < self.proton_gradient_threshold:
            return

        max_atp_production = (
            self.proton_gradient - self.proton_gradient_threshold
        ) // 4
        nadh_contribution = min(
            self.nadh.quantity, max_atp_production / self.nadh_to_atp_ratio
        )
        fadh2_contribution = min(
            self.fadh2.quantity,
            (max_atp_production - nadh_contribution * self.nadh_to_atp_ratio)
            / self.fadh2_to_atp_ratio,
        )

        atp_produced = int(
            (
                nadh_contribution * self.nadh_to_atp_ratio
                + fadh2_contribution * self.fadh2_to_atp_ratio
            )
            * self.atp_synthase_efficiency
        )

        self.atp.quantity = min(self.atp.quantity + atp_produced, self.atp.max_quantity)
        self.nadh.quantity -= int(nadh_contribution)
        self.fadh2.quantity -= int(fadh2_contribution)
        self.proton_gradient -= atp_produced * 4

        logger.info(f"ATP produced: {atp_produced} molecules")

    def reset(self):
        """Reset mitochondrion state."""
        self.__init__()
        logger.info("Mitochondrion state reset")


class Cell:
    def __init__(self):
        self.cytoplasm = Cytoplasm()
        self.mitochondrion = Mitochondrion()
        self.simulation_time = 0  # in seconds
        self.time_step = 0.1  # 100 milliseconds per step

    def produce_atp(self, glucose_amount: int, duration: float) -> int:
        """
        Simulates ATP production in the entire cell for a specified duration.

        Parameters:
        -----------
        glucose_amount : int
            The amount of glucose available for the simulation.
        duration : float
            The duration of the simulation in seconds.

        Returns:
        --------
        int
            The total amount of ATP produced during the simulation.
        """
        initial_atp = self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity
        self.simulation_time = 0

        # Glycolysis in cytoplasm (assume it takes 1 second)
        pyruvate = self.cytoplasm.glycolysis(glucose_amount)
        self.simulation_time += 1

        # Pyruvate processing and Krebs cycle in mitochondrion (assume it takes 2 seconds)
        acetyl_coa = self.mitochondrion.pyruvate_to_acetyl_coa(pyruvate)
        self.mitochondrion.krebs_cycle(acetyl_coa)
        self.simulation_time += 2

        # Continuous processes: electron transport chain and oxidative phosphorylation
        while self.simulation_time < duration:
            self.mitochondrion.electron_transport_chain()
            self.mitochondrion.oxidative_phosphorylation()
            self.simulation_time += self.time_step

        total_atp = self.cytoplasm.atp.quantity + self.mitochondrion.atp.quantity - initial_atp
        logger.info(f"Total ATP produced in the cell over {duration} seconds: {total_atp}")
        return total_atp

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
    simulation_duration = 60  # 60 seconds of cellular activity

    for glucose in glucose_amounts:
        logger.info(f"\nSimulating ATP production with {glucose} glucose units for {simulation_duration} seconds:")
        start_time = time.time()
        atp_produced = cell.produce_atp(glucose, simulation_duration)
        end_time = time.time()

        # Log the current state of the cell
        logger.info(f"Total ATP produced: {atp_produced}")
        logger.info(f"Cytoplasm ATP: {cell.cytoplasm.atp.quantity}")
        logger.info(f"Cytoplasm NADH: {cell.cytoplasm.nadh.quantity}")
        logger.info(f"Mitochondrion ATP: {cell.mitochondrion.atp.quantity}")
        logger.info(f"Mitochondrion NADH: {cell.mitochondrion.nadh.quantity}")
        logger.info(f"Mitochondrion FADH2: {cell.mitochondrion.fadh2.quantity}")
        logger.info(
            f"Mitochondrion proton gradient: {cell.mitochondrion.proton_gradient}"
        )
        logger.info(f"Mitochondrion oxygen: {cell.mitochondrion.oxygen.quantity}")
        logger.info(f"Simulation time: {cell.simulation_time:.2f} seconds")
        logger.info(f"Real computation time: {end_time - start_time:.2f} seconds")

        # Reset the cell for the next simulation
        cell.reset()

    logger.info("Simulation complete.")
