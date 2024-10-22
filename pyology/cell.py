from typing import Dict

from .constants import TIME_STEP
from .cytoplasm import Cytoplasm
from .mitochondrion import KrebsCycle, Mitochondrion
from .organelle import Organelle


class Cell(Organelle):
    """
    Represents a cell in the simulation.

    Parameters
    ----------
    logger : logging.Logger, optional
        The logger to use for logging messages.
    debug : bool, optional
        Whether to enable debug mode.

    Attributes
    ----------
    cytoplasm : Cytoplasm
        The cytoplasm of the cell.
    mitochondrion : Mitochondrion
        The mitochondrion of the cell.
    krebs_cycle : KrebsCycle
        The Krebs cycle of the cell.
    simulation_time : float
        The current simulation time.
    time_step : float
        The time step for the simulation.
    base_glycolysis_rate : float
        The base glycolysis rate for the cell.
    glycolysis_rate : float
        The current glycolysis rate for the cell.
    debug : bool
        Whether to enable debug mode.
    logger : logging.Logger
        The logger to use for logging messages.

    Methods
    -------
    get_cell_state(self, glucose_processed: float, total_atp_produced: float) -> Dict[str, float]:
        Helper method to get the current state of the cell.
    reset(self) -> None:
        Reset the entire cell state.
    """

    name = "Cell"

    def __init__(self, logger=None, debug=False) -> None:
        super().__init__()
        self.cytoplasm = Cytoplasm(logger=logger, debug=debug)
        self.mitochondrion = Mitochondrion()
        self.krebs_cycle = KrebsCycle()
        self.simulation_time = 0
        self.time_step = TIME_STEP
        self.base_glycolysis_rate = 1.0
        self.glycolysis_rate = self.base_glycolysis_rate
        self.debug = debug
        self.logger = logger

    def get_cell_state(
        self, glucose_processed: float, total_atp_produced: float
    ) -> Dict[str, float]:
        """
        Helper method to get the current state of the cell.

        Parameters
        ----------
        glucose_processed : float
            The amount of glucose processed by the cell.
        total_atp_produced : float
            The total amount of ATP produced by the cell.

        Returns
        -------
        Dict[str, float]
            A dictionary containing the current state of the cell.
        """
        return {
            "simulation_time": self.simulation_time,
            "glucose_processed": glucose_processed,
            "total_atp_produced": total_atp_produced,
            "cytoplasm_atp": self.metabolites["atp"].quantity,
            "mitochondrion_atp": self.metabolites["atp"].quantity,
            "cytoplasm_nadh": self.metabolites["nadh"].quantity,
            "mitochondrion_nadh": self.metabolites["nadh"].quantity,
            "mitochondrion_fadh2": self.metabolites["fadh2"].quantity,
            "mitochondrial_calcium": self.metabolites["calcium"].quantity,
            "proton_gradient": self.mitochondrion.proton_gradient,
            "oxygen_remaining": self.metabolites["oxygen"].quantity,
        }

    def reset(self) -> None:
        """Reset the entire cell state."""
        self.metabolites.reset()
        self.simulation_time = 0
        if self.logger:
            self.logger.info("Cell state reset")
        self.glycolysis_rate = self.base_glycolysis_rate
