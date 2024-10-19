from typing import Dict, Union

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


def calculate_total_adenine_nucleotides(
    metabolites: Dict[str, Union[float, "Metabolite"]]
) -> float:
    """
    Calculate the total adenine nucleotides in the system.

    Parameters:
    -----------
    metabolites : Dict[str, Union[float, 'Metabolite']]
        A dictionary of metabolites and their quantities or Metabolite objects.

    Returns:
    --------
    float
        The total adenine nucleotides in the system.
    """

    return sum(
        get_quantity(metabolites.get(nucleotide, 0))
        for nucleotide in ["ATP", "ADP", "AMP"]
    )
