import logging
from unittest.mock import Mock, patch

import pytest

from pyology.energy_calculations import (
    calculate_base_energy_state,
    calculate_cell_energy_state,
    calculate_energy_state,
    calculate_glycolysis_energy_state,
    calculate_proton_gradient_energy,
    calculate_total_adenine_nucleotides,
    get_quantity,
)
from pyology.metabolite import Metabolite
from pyology.cell import Cell
from pyology.organelle import Organelle


# Helper function to create a mock organelle with specified metabolites
def create_mock_organelle(metabolites):
    mock_organelle = Mock(spec=Organelle)
    mock_organelle.get_metabolite_quantity.side_effect = lambda m: metabolites.get(m, 0)
    return mock_organelle


@pytest.fixture
def mock_logger():
    return Mock(spec=logging.Logger)


def test_get_quantity():
    assert get_quantity(5) == 5
    assert get_quantity(3.14) == 3.14

    mock_metabolite = Mock()
    mock_metabolite.quantity = 10
    assert get_quantity(mock_metabolite) == 10

    with pytest.raises(TypeError):
        get_quantity("not a number or metabolite")


def test_calculate_base_energy_state():
    metabolites = {
        "ATP": 10,
        "glucose": 5,
        "NADH": Mock(quantity=3),
    }
    energy_values = {
        "ATP": 50,
        "glucose": 686,
        "NADH": 158,
    }
    expected_energy = 10 * 50 + 5 * 686 + 3 * 158
    assert calculate_base_energy_state(metabolites, energy_values) == expected_energy


def test_calculate_cell_energy_state():
    mock_cell = Mock()
    mock_cell.cytoplasm.metabolites = {"ATP": 5, "proton_gradient": 2}
    mock_cell.mitochondrion.metabolites = {"ATP": 8, "proton_gradient": 3}
    mock_cell.mitochondrion.proton_gradient = 10

    expected_energy = (5 + 8) * 50 + (2 + 3 + 10) * 5
    assert calculate_cell_energy_state(mock_cell) == expected_energy


def test_calculate_glycolysis_energy_state():
    mock_organelle = Mock()
    mock_organelle.metabolites = {
        "glucose": 2,
        "ATP": 4,
        "pyruvate": 1,
    }
    expected_energy = 2 * 686 + 4 * 50 + 1 * 343
    assert calculate_glycolysis_energy_state(mock_organelle) == expected_energy


def test_calculate_total_adenine_nucleotides():
    mock_organelle = create_mock_organelle(
        {
            "ATP": 5,
            "ADP": 3,
            "AMP": 2,
        }
    )
    assert calculate_total_adenine_nucleotides(mock_organelle) == 10


def test_calculate_energy_state(mock_logger):
    mock_organelle = create_mock_organelle(
        {
            "ATP": 10,
            "GTP": 5,
            "NADH": 3,
            "FADH2": 2,
            "Acetyl_CoA": 4,
        }
    )

    with patch(
        "pyology.energy_calculations.calculate_proton_gradient_energy", return_value=100
    ):
        energy_state = calculate_energy_state(mock_organelle, mock_logger)

    expected_energy = (10 * 50) + (5 * 50) + (3 * 158) + (2 * 105) + (4 * 31) + 100
    assert energy_state == pytest.approx(expected_energy)

    # Check if logger was called with correct information
    mock_logger.info.assert_called()
    assert mock_logger.info.call_count == 7  # 6 energy contributions + total


def test_calculate_proton_gradient_energy():
    mock_organelle = Mock(spec=Organelle)
    energy = calculate_proton_gradient_energy(mock_organelle)
    expected_energy = 21.819010515
    assert energy == pytest.approx(expected_energy)


def test_calculate_base_energy_state_empty():
    assert calculate_base_energy_state({}, {}) == 0


def test_calculate_cell_energy_state_empty():
    mock_cell = Mock()
    mock_cell.cytoplasm.metabolites = {}
    mock_cell.mitochondrion.metabolites = {}
    mock_cell.mitochondrion.proton_gradient = 0
    assert calculate_cell_energy_state(mock_cell) == 0


def test_calculate_glycolysis_energy_state_empty():
    mock_organelle = Mock()
    mock_organelle.metabolites = {}
    assert calculate_glycolysis_energy_state(mock_organelle) == 0


def test_calculate_total_adenine_nucleotides_empty():
    mock_organelle = create_mock_organelle({})
    assert calculate_total_adenine_nucleotides(mock_organelle) == 0


def test_calculate_energy_state_empty(mock_logger):
    mock_organelle = create_mock_organelle({})
    with patch(
        "pyology.energy_calculations.calculate_proton_gradient_energy", return_value=0
    ):
        energy_state = calculate_energy_state(mock_organelle, mock_logger)
    assert energy_state == 0
