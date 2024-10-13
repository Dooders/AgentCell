from typing import List


class Effector:
    def __init__(self, concentration: float, Ki: float, Ka: float):
        self.concentration = concentration
        self.Ki = Ki
        self.Ka = Ka


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
