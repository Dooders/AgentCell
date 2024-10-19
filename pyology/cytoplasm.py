from .glycolysis import Glycolysis
from .organelle import Organelle
from .exceptions import InsufficientMetaboliteError


class Cytoplasm(Organelle):
    """
    The cytoplasm is the fluid-filled space inside the cell that contains the
    cell's organelles and performs many of the cell's metabolic functions.

    Attributes
    ----------
    glycolysis_rate (float): The rate at which glucose is processed during glycolysis.

    Methods
    -------
    glycolysis(self, glucose_consumed: float) -> float:
        Perform glycolysis on the specified amount of glucose.
    reset(self) -> None:
        Reset the cytoplasm to its initial state.
    """

    name = "Cytoplasm"

    def __init__(self):
        super().__init__()

    def glycolysis(self, glucose_consumed: float) -> float:
        """
        Perform glycolysis on the specified amount of glucose.

        Parameters
        ----------
        glucose_consumed : float
            The amount of glucose to consume.

        Returns
        -------
        float
            The amount of pyruvate produced.
        """
        initial_atp = self.metabolites["ATP"].quantity
        initial_adp = self.metabolites["ADP"].quantity
        initial_amp = self.metabolites["AMP"].quantity
        initial_total_adenine = initial_atp + initial_adp + initial_amp

        # Perform glycolysis
        pyruvate_produced = Glycolysis.perform(self, glucose_consumed)

        # Calculate net ATP produced
        final_atp = self.metabolites["ATP"].quantity
        net_atp_produced = final_atp - initial_atp

        # Ensure ADP is consumed when ATP is produced
        if self.metabolites["ADP"].quantity >= net_atp_produced:
            self.metabolites["ADP"].quantity -= net_atp_produced
        else:
            # If not enough ADP, convert AMP to ADP
            adp_needed = net_atp_produced - self.metabolites["ADP"].quantity
            if self.metabolites["AMP"].quantity >= adp_needed / 2:
                self.metabolites["AMP"].quantity -= adp_needed / 2
                self.metabolites["ADP"].quantity += adp_needed
                self.metabolites["ADP"].quantity -= net_atp_produced
            else:
                raise InsufficientMetaboliteError(
                    "Not enough ADP or AMP for ATP production in glycolysis"
                )

        final_atp = self.metabolites["ATP"].quantity
        final_adp = self.metabolites["ADP"].quantity
        final_amp = self.metabolites["AMP"].quantity
        final_total_adenine = final_atp + final_adp + final_amp

        assert abs(final_total_adenine - initial_total_adenine) < 1e-6, (
            f"Adenine nucleotide conservation violated in glycolysis. "
            f"Initial: {initial_total_adenine:.6f}, Final: {final_total_adenine:.6f}, "
            f"Difference: {final_total_adenine - initial_total_adenine:.6f}"
        )

        return pyruvate_produced

    def reset(self) -> None:
        self.__init__()
