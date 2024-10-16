"""
Signal Transduction Pathways
    Modeling Cascades:
        Implement sequences where one activated molecule activates others.
    Feedback Loops:
        Incorporate positive and negative feedback mechanisms.
"""

from typing import Dict

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

    Methods
    -------
    catalyze : function
        Catalyzes a biochemical reaction.
    """

    def __init__(
        self,
        name: str,
        k_cat: float,
        k_m: Dict[str, float],
        inhibitors: Dict[str, float] = None,
        activators: Dict[str, float] = None,
    ):
        self.name = name
        self.k_cat = k_cat
        self.k_m = k_m
        self.inhibitors = inhibitors or {}
        self.activators = activators or {}

    def calculate_rate(self, metabolites: Dict[str, Metabolite]) -> float:
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
