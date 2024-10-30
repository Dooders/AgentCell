import logging
from typing import TYPE_CHECKING, Dict, Union

from .metabolite import Metabolite

if TYPE_CHECKING:
    from pyology.cell import Cell
    from pyology.organelle import Organelle


def get_quantity(value: Union[float, "Metabolite"]) -> float:
    """
    Get the quantity of a metabolite.

    Parameters
    ----------
    value : Union[float, Metabolite]
        The value to get the quantity from.

    Returns
    -------
    float
        The quantity of the metabolite.
    """
    if isinstance(value, (int, float)):
        return value
    elif hasattr(value, "quantity"):
        return value.quantity
    else:
        raise TypeError(f"Unsupported type for metabolite quantity: {type(value)}")


def calculate_base_energy_state(
    metabolites: Dict[str, Union[float, "Metabolite"]], energy_values: Dict[str, float]
) -> float:
    """
    Calculate the base energy state of the organelle.

    Parameters
    ----------
    metabolites : Dict[str, Union[float, Metabolite]]
        The metabolites in the organelle.
    energy_values : Dict[str, float]
        The energy values for the metabolites.

    Returns
    -------
    float
        The base energy state in kJ/mol.
    """
    return sum(
        get_quantity(metabolites.get(metabolite, 0)) * energy
        for metabolite, energy in energy_values.items()
    )


def calculate_cell_energy_state(cell: "Cell") -> float:
    """
    Calculate the energy state of the cell.

    Parameters
    ----------
    cell : Cell
        The cell to calculate the energy state for.

    Returns
    -------
    float
        The energy state of the cell in kJ/mol.
    """
    energy_values = {"ATP": 50, "proton_gradient": 5}
    return (
        calculate_base_energy_state(cell.cytoplasm.metabolites, energy_values)
        + calculate_base_energy_state(cell.mitochondrion.metabolites, energy_values)
        + get_quantity(cell.mitochondrion.proton_gradient)
        * energy_values["proton_gradient"]
    )


def calculate_glycolysis_energy_state(organelle: "Organelle") -> float:
    """
    Calculate the energy state of the glycolysis pathway.

    Parameters
    ----------
    organelle : Organelle
        The organelle to calculate the energy state for.

    Returns
    -------
    float
        The energy state of the glycolysis pathway in kJ/mol.
    """
    energy_values = {
        "ATP": 50,
        "ADP": 30,
        "glucose": 686,
        "glucose-6-phosphate": 916,
        "fructose-6-phosphate": 916,
        "fructose-1-6-bisphosphate": 1146,
        "glyceraldehyde-3-phosphate": 573,
        "1-3-bisphosphoglycerate": 803,
        "3-phosphoglycerate": 573,
        "2-phosphoglycerate": 573,
        "phosphoenolpyruvate": 803,
        "pyruvate": 343,
    }
    return calculate_base_energy_state(organelle.metabolites, energy_values)


def calculate_total_adenine_nucleotides(organelle: "Organelle") -> float:
    """
    Calculate the total adenine nucleotides in the system.

    Parameters
    ----------
    organelle : Organelle
        The organelle containing the metabolites.

    Returns
    -------
    float
        The total amount of adenine nucleotides (ATP + ADP + AMP) in moles.
    """
    return sum(
        organelle.get_metabolite_quantity(nucleotide)
        for nucleotide in ["ATP", "ADP", "AMP"]
    )


# def calculate_energy_state(organelle: "Organelle", logger: logging.Logger) -> float:
#     """
#     Calculate the total energy state of the organelle, with detailed logging for energy debugging.

#     This function accounts for various forms of energy storage in the cell:
#     1. High-energy phosphate compounds (ATP, GTP, etc.)
#     2. Reduced coenzymes (NADH, FADH2)
#     3. Acetyl-CoA
#     4. Concentration gradients of key metabolites

#     Parameters
#     ----------
#     organelle : Organelle
#         The organelle to calculate the energy state for.
#     logger : logging.Logger
#         Logger for output messages.

#     Returns
#     -------
#     float
#         The total energy state in kJ/mol.
#     """
#     total_energy = 0.0

#     # Energy from high-energy phosphate compounds
#     atp_energy = organelle.get_metabolite_quantity("ATP") * 50  # ~50 kJ/mol
#     gtp_energy = organelle.get_metabolite_quantity("GTP") * 50  # ~50 kJ/mol
#     total_energy += atp_energy + gtp_energy

#     # Energy from reduced coenzymes
#     nadh_energy = organelle.get_metabolite_quantity("NADH") * 158  # ~158 kJ/mol
#     fadh2_energy = organelle.get_metabolite_quantity("FADH2") * 105  # ~105 kJ/mol
#     total_energy += nadh_energy + fadh2_energy

#     # Energy from Acetyl-CoA
#     acetyl_coa_energy = (
#         organelle.get_metabolite_quantity("Acetyl_CoA") * 31
#     )  # ~31 kJ/mol
#     total_energy += acetyl_coa_energy

#     # Energy from concentration gradients
#     proton_gradient_energy = calculate_proton_gradient_energy(organelle)
#     total_energy += proton_gradient_energy

#     # Combine energy contributions into a single-line log message
#     energy_log = f"""Total energy state: {total_energy:.2f} kJ/mol | ATP: {atp_energy:.2f}, GTP: {gtp_energy:.2f}, NADH: {nadh_energy:.2f}, FADH2: {fadh2_energy:.2f}, Acetyl-CoA: {acetyl_coa_energy:.2f}, Proton gradient: {proton_gradient_energy:.2f} kJ/mol"""

#     # Log the combined energy contributions
#     logger.info(energy_log)

#     return total_energy

gibbs_free_energies = {
    "ATP": 50,
    "ADP": 30,
    "AMP": 10,
    "GTP": 50,
    "NADH": 158,
    "FADH2": 105,
    "Acetyl_CoA": 31,
    "proton_gradient": 5,
    "glucose": 686,
    "glucose-6-phosphate": 916,
    "fructose-6-phosphate": 916,
    "fructose-1-6-bisphosphate": 1146,
    "glyceraldehyde-3-phosphate": 573,
    "1-3-bisphosphoglycerate": 803,
    "3-phosphoglycerate": 573,
    "2-phosphoglycerate": 573,
    "phosphoenolpyruvate": 803,
    "pyruvate": 343,
    "pyruvate_dehydrogenase": 100,
    "phosphoenolpyruvate_carboxykinase": 100,
    "phosphoenolpyruvate_mutase": 100,
    "pyruvate_kinase": 100,
    "phosphoglycerate_kinase": 100,
    "phosphoglycerate_mutase": 100,
    "phosphoglycerate_phosphatase": 100,
}


def calculate_energy_state(
    organelle_or_dict: Union["Organelle", Dict[str, Dict[str, float]]], 
    logger: logging.Logger, 
    gibbs_free_energies: dict = gibbs_free_energies
) -> float:
    """
    Calculate the total energy from either an Organelle object or a state dictionary using Gibbs free energies.

    Parameters
    ----------
    organelle_or_dict : Union[Organelle, Dict[str, Dict[str, float]]]
        Either an Organelle object or a state dictionary where each metabolite has a nested dict with 'quantity' key.
    logger : logging.Logger
        The logger to use for logging messages.
    gibbs_free_energies : dict
        A dictionary where keys are metabolite names, and values are their standard Gibbs free energies (kJ/mol).

    Returns
    -------
    float
        The total energy in kJ/mol.
    """
    total_energy = 0.0

    # Handle different input types
    if hasattr(organelle_or_dict, 'metabolites'):
        # Input is an Organelle object
        iterate_over = organelle_or_dict.metabolites
    else:
        # Input is a dictionary
        iterate_over = organelle_or_dict.items()

    # Calculate energy contribution of each metabolite
    for item in iterate_over:
        if hasattr(organelle_or_dict, 'metabolites'):
            # For Organelle object
            label = item.label
            quantity = item.quantity
            name = item.name
        else:
            # For dictionary
            label = item[0]
            quantity = item[1]['quantity']  # Access the nested quantity value
            name = label

        # Fetch the Gibbs free energy for the metabolite
        delta_g_f = gibbs_free_energies.get(label, 0.0)
        # Calculate energy contribution
        contribution = quantity * delta_g_f
        # Add to total energy
        total_energy += contribution
        
        if contribution > 0:
            #! remove this or have debug arg
            logger.debug(f"{name} contributes {contribution:.2f} kJ/mol to total energy.")

    return total_energy



def calculate_proton_gradient_energy(organelle: "Organelle") -> float:
    """
    Calculate the energy stored in the proton gradient across the mitochondrial membrane.

    This calculation is based on the chemiosmotic theory and provides a more realistic
    estimate of the energy stored in the proton gradient.

    Parameters
    ----------
    organelle : Organelle
        The organelle (assumed to be mitochondrion) to calculate the proton gradient energy for.

    Returns
    -------
    float
        The energy stored in the proton gradient in kJ/mol.
    """
    # Constants
    R = 8.314  # J/(mol·K), gas constant
    T = 310  # K, typical cellular temperature (37°C)
    F = 96485  # C/mol, Faraday constant

    # Typical values for mitochondrial membrane potential and pH gradient
    delta_psi = 0.18  # V, electrical potential difference
    delta_pH = 0.75  # pH units, typical pH gradient across mitochondrial membrane

    # Calculate the proton motive force (PMF)
    pmf = delta_psi + (2.303 * R * T / F) * delta_pH

    # Convert PMF to kJ/mol
    energy_kj_mol = pmf * F / 1000  # divide by 1000 to convert J to kJ

    return energy_kj_mol
