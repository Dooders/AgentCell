import logging
from typing import Dict, Union

from pyology.organelle import Organelle

from .metabolite import Metabolite


def get_quantity(value):
    if isinstance(value, (int, float)):
        return value
    elif hasattr(value, "quantity"):
        return value.quantity
    else:
        raise TypeError(f"Unsupported type for metabolite quantity: {type(value)}")


def calculate_base_energy_state(
    metabolites: Dict[str, Union[float, "Metabolite"]], energy_values: Dict[str, float]
) -> float:
    return sum(
        get_quantity(metabolites.get(metabolite, 0)) * energy
        for metabolite, energy in energy_values.items()
    )


def calculate_cell_energy_state(cell) -> float:
    energy_values = {"ATP": 50, "proton_gradient": 5}
    return (
        calculate_base_energy_state(cell.cytoplasm.metabolites, energy_values)
        + calculate_base_energy_state(cell.mitochondrion.metabolites, energy_values)
        + get_quantity(cell.mitochondrion.proton_gradient)
        * energy_values["proton_gradient"]
    )


def calculate_glycolysis_energy_state(organelle) -> float:
    energy_values = {
        "ATP": 50,
        "ADP": 30,
        "glucose": 686,
        "glucose_6_phosphate": 916,
        "fructose_6_phosphate": 916,
        "fructose_1_6_bisphosphate": 1146,
        "glyceraldehyde_3_phosphate": 573,
        "bisphosphoglycerate_1_3": 803,
        "phosphoglycerate_3": 573,
        "phosphoglycerate_2": 573,
        "phosphoenolpyruvate": 803,
        "pyruvate": 343,
    }
    return calculate_base_energy_state(organelle.metabolites, energy_values)


def calculate_total_adenine_nucleotides(organelle: "Organelle") -> float:
    """
    Calculate the total adenine nucleotides in the system.

    Parameters:
    -----------
    organelle : Organelle
        The organelle containing the metabolites.

    Returns:
    --------
    float
        The total adenine nucleotides in the system.
    """

    return sum(
        get_quantity(organelle.get_metabolite_quantity(nucleotide))
        for nucleotide in ["ATP", "ADP", "AMP"]
    )


def calculate_energy_state(organelle: "Organelle", logger: logging.Logger) -> float:
    """
    Calculate the total energy state of the organelle.

    This method calculates the energy state based on the high-energy phosphate bonds
    in ATP, ADP, and other relevant metabolites.

    Parameters
    ----------
    organelle : Organelle
        The organelle containing the metabolites.
    logger : logging.Logger
        The logger to use for logging.

    Returns
    -------
    float
        The total energy state of the organelle.
    """
    # Energy values in kJ/mol
    ATP_ENERGY = 30.5
    ADP_ENERGY = 30.5
    NADH_ENERGY = 158
    FADH2_ENERGY = 105

    energy_state = (
        organelle.get_metabolite_quantity("ATP") * ATP_ENERGY
        + organelle.get_metabolite_quantity("ADP") * ADP_ENERGY
        + organelle.get_metabolite_quantity("NADH") * NADH_ENERGY
        + organelle.get_metabolite_quantity("FADH2") * FADH2_ENERGY
    )

    logger.info(f"Calculated energy state: {energy_state:.2f} kJ/mol")

    return energy_state
