import logging
from typing import Dict, Union, TYPE_CHECKING

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

    This function accounts for various forms of energy storage in the cell:
    1. High-energy phosphate compounds (ATP, GTP, etc.)
    2. Reduced coenzymes (NADH, FADH2)
    3. Acetyl-CoA
    4. Concentration gradients of key metabolites

    Parameters
    ----------
    organelle : Organelle
        The organelle to calculate the energy state for.
    logger : logging.Logger
        Logger for output messages.

    Returns
    -------
    float
        The total energy state in kJ/mol.
    """
    total_energy = 0.0

    # Energy from high-energy phosphate compounds
    atp_energy = organelle.get_metabolite_quantity("ATP") * 50  # ~50 kJ/mol
    gtp_energy = organelle.get_metabolite_quantity("GTP") * 50  # ~50 kJ/mol
    total_energy += atp_energy + gtp_energy

    # Energy from reduced coenzymes
    nadh_energy = organelle.get_metabolite_quantity("NADH") * 158  # ~158 kJ/mol
    fadh2_energy = organelle.get_metabolite_quantity("FADH2") * 105  # ~105 kJ/mol
    total_energy += nadh_energy + fadh2_energy

    # Energy from Acetyl-CoA
    acetyl_coa_energy = organelle.get_metabolite_quantity("Acetyl_CoA") * 31  # ~31 kJ/mol
    total_energy += acetyl_coa_energy

    # Energy from concentration gradients
    # This is a simplified approximation and may need refinement
    proton_gradient_energy = calculate_proton_gradient_energy(organelle)
    total_energy += proton_gradient_energy

    # Log the energy contributions
    logger.info(f"Energy from ATP: {atp_energy:.2f} kJ/mol")
    logger.info(f"Energy from GTP: {gtp_energy:.2f} kJ/mol")
    logger.info(f"Energy from NADH: {nadh_energy:.2f} kJ/mol")
    logger.info(f"Energy from FADH2: {fadh2_energy:.2f} kJ/mol")
    logger.info(f"Energy from Acetyl-CoA: {acetyl_coa_energy:.2f} kJ/mol")
    logger.info(f"Energy from proton gradient: {proton_gradient_energy:.2f} kJ/mol")
    logger.info(f"Total energy state: {total_energy:.2f} kJ/mol")

    return total_energy

def calculate_proton_gradient_energy(organelle: "Organelle") -> float:
    """
    Calculate the energy stored in the proton gradient across the mitochondrial membrane.

    This is a simplified calculation and may need to be refined based on more detailed models.

    Parameters
    ----------
    organelle : Organelle
        The organelle (assumed to be mitochondrion) to calculate the proton gradient energy for.

    Returns
    -------
    float
        The energy stored in the proton gradient in kJ/mol.
    """
    # Simplified calculation based on the proton motive force
    # Typical proton motive force is around 200-220 mV
    proton_motive_force = 0.22  # V
    faraday_constant = 96485  # C/mol
    
    # Assuming the gradient is equivalent to moving 3 protons
    n_protons = 3
    
    energy = n_protons * faraday_constant * proton_motive_force
    
    return energy

def calculate_total_adenine_nucleotides(organelle: "Organelle") -> float:
    """
    Calculate the total amount of adenine nucleotides (ATP + ADP + AMP).

    Parameters
    ----------
    organelle : Organelle
        The organelle to calculate the total adenine nucleotides for.

    Returns
    -------
    float
        The total amount of adenine nucleotides in moles.
    """
    atp = organelle.get_metabolite_quantity("ATP")
    adp = organelle.get_metabolite_quantity("ADP")
    amp = organelle.get_metabolite_quantity("AMP")
    
    total_adenine = atp + adp + amp
    
    return total_adenine
