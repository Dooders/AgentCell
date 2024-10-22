from typing import Dict, List

from .metabolite import Metabolite


class Enzyme:
    """
    Represents an enzyme that catalyzes a biochemical reaction.

    Parameters
    ----------
    name : str
        The name of the enzyme.
    k_cat : float
        The catalytic constant (turnover number) of the enzyme.
    k_m : Dict[str, float]
        The Michaelis constants for multiple substrates.
    inhibitors : Dict[str, float], optional
        The inhibition constants for multiple substrates. Defaults to None.
    activators : Dict[str, float], optional
        The activation constants for multiple substrates. Defaults to None.
    active : bool, optional
        Whether the enzyme is active. Defaults to True.
    downstream_enzymes : List[Enzyme], optional
        The enzymes that are downstream of this enzyme. Defaults to None.

    Methods
    -------
    calculate_rate : function
        Calculates the rate of the enzyme's reaction.
    activate : function
        Activates the enzyme and its downstream enzymes.
    deactivate : function
        Deactivates the enzyme.
    regulate_enzyme : function
        Regulates another enzyme by activating or deactivating it.
    """

    def __init__(
        self,
        name: str,
        k_cat: float,
        k_m: Dict[str, float],
        inhibitors: Dict[str, float] = None,
        activators: Dict[str, float] = None,
        active: bool = True,
        downstream_enzymes: List["Enzyme"] = None,
    ):
        self.name = name
        self.k_cat = k_cat
        self.k_m = k_m
        self.inhibitors = inhibitors or {}
        self.activators = activators or {}
        self.active = active
        self.downstream_enzymes = downstream_enzymes or []

    def calculate_rate(self, metabolites: Dict[str, Metabolite]) -> float:
        """
        Calculates the rate of the enzyme's reaction.

        Parameters
        ----------
        metabolites : Dict[str, Metabolite]
            The metabolites in the cell.

        Returns
        -------
        float
            The rate of the enzyme's reaction.
        """
        if not self.active:
            return 0.0
        rate = self.k_cat
        for substrate, k_m in self.k_m.items():
            metabolite = metabolites.get(substrate)
            if metabolite is None:
                return 0.0  # If a required substrate is missing, rate is 0
            conc = metabolite.quantity
            rate *= conc / (k_m + conc)

        for substrate, inhibitor_constant in self.inhibitors.items():
            metabolite = metabolites.get(substrate)
            if metabolite:
                conc = metabolite.quantity
                rate *= 1 / (1 + conc / inhibitor_constant)

        for substrate, activator_constant in self.activators.items():
            metabolite = metabolites.get(substrate)
            if metabolite:
                conc = metabolite.quantity
                rate *= 1 + conc / activator_constant

        return rate

    def activate(self) -> None:
        """
        Activates the enzyme and its downstream enzymes.
        """
        self.active = True
        for enzyme in self.downstream_enzymes:
            enzyme.activate()

    def deactivate(self) -> None:
        """
        Deactivates the enzyme.
        """
        self.active = False

    def regulate_enzyme(self, target_enzyme: "Enzyme", action: str) -> None:
        """
        Regulates another enzyme by activating or deactivating it.

        Parameters
        ----------
        target_enzyme : Enzyme
            The enzyme to be regulated.
        action : str
            The action to perform on the target enzyme ('activate' or 'deactivate').

        Raises
        ------
        ValueError
            If an invalid action is provided.
        """
        if action == "activate":
            target_enzyme.activate()
        elif action == "deactivate":
            target_enzyme.deactivate()
        else:
            raise ValueError("Invalid action. Use 'activate' or 'deactivate'.")
