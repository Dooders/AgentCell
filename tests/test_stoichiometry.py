import pytest

from pyology.cell import Cell
from pyology.common_reactions import GlycolysisReactions
from pyology.reaction import Reaction


@pytest.fixture
def cell():
    cell = Cell()
    # Initialize the cell with required metabolites
    cell.metabolites.register(
        ATP=(10, 100),
        ADP=(10, 100),
        AMP=(10, 100),
        glucose=(10, 100),
        glucose_6_phosphate=(10, 100),
        fructose_6_phosphate=(10, 100),
        fructose_1_6_bisphosphate=(10, 100),
        bisphosphoglycerate_1_3=(10, 100),
        phosphoglycerate_3=(10, 100),
        phosphoenolpyruvate=(10, 100),
        pyruvate=(10, 100),
    )
    return cell


def test_hexokinase_reaction(cell):
    reaction = GlycolysisReactions.hexokinase
    initial_atp = cell.get_metabolite_quantity("ATP")
    initial_adp = cell.get_metabolite_quantity("ADP")
    initial_glucose = cell.get_metabolite_quantity("glucose")
    initial_g6p = cell.get_metabolite_quantity("glucose_6_phosphate")

    reaction.execute(cell)

    assert cell.get_metabolite_quantity("ATP") == initial_atp - 1
    assert cell.get_metabolite_quantity("ADP") == initial_adp + 1
    assert cell.get_metabolite_quantity("glucose") == initial_glucose - 1
    assert cell.get_metabolite_quantity("glucose_6_phosphate") == initial_g6p + 1
    assert initial_atp + initial_adp == cell.get_metabolite_quantity(
        "ATP"
    ) + cell.get_metabolite_quantity("ADP")


def test_phosphofructokinase_reaction(cell):
    reaction = GlycolysisReactions.phosphofructokinase
    initial_atp = cell.get_metabolite_quantity("ATP")
    initial_adp = cell.get_metabolite_quantity("ADP")
    initial_f6p = cell.get_metabolite_quantity("fructose_6_phosphate")
    initial_f16bp = cell.get_metabolite_quantity("fructose_1_6_bisphosphate")

    reaction.execute(cell)

    assert cell.get_metabolite_quantity("ATP") == initial_atp - 1
    assert cell.get_metabolite_quantity("ADP") == initial_adp + 1
    assert cell.get_metabolite_quantity("fructose_6_phosphate") == initial_f6p - 1
    assert (
        cell.get_metabolite_quantity("fructose_1_6_bisphosphate") == initial_f16bp + 1
    )
    assert initial_atp + initial_adp == cell.get_metabolite_quantity(
        "ATP"
    ) + cell.get_metabolite_quantity("ADP")


def test_phosphoglycerate_kinase_reaction(cell):
    reaction = GlycolysisReactions.phosphoglycerate_kinase
    initial_atp = cell.get_metabolite_quantity("ATP")
    initial_adp = cell.get_metabolite_quantity("ADP")
    initial_bpg = cell.get_metabolite_quantity("bisphosphoglycerate_1_3")
    initial_3pg = cell.get_metabolite_quantity("phosphoglycerate_3")

    reaction.execute(cell)

    assert cell.get_metabolite_quantity("ATP") == initial_atp + 1
    assert cell.get_metabolite_quantity("ADP") == initial_adp - 1
    assert cell.get_metabolite_quantity("bisphosphoglycerate_1_3") == initial_bpg - 1
    assert cell.get_metabolite_quantity("phosphoglycerate_3") == initial_3pg + 1
    assert initial_atp + initial_adp == cell.get_metabolite_quantity(
        "ATP"
    ) + cell.get_metabolite_quantity("ADP")


def test_pyruvate_kinase_reaction(cell):
    reaction = GlycolysisReactions.pyruvate_kinase
    initial_atp = cell.get_metabolite_quantity("ATP")
    initial_adp = cell.get_metabolite_quantity("ADP")
    initial_pep = cell.get_metabolite_quantity("phosphoenolpyruvate")
    initial_pyruvate = cell.get_metabolite_quantity("pyruvate")

    reaction.execute(cell)

    assert cell.get_metabolite_quantity("ATP") == initial_atp + 1
    assert cell.get_metabolite_quantity("ADP") == initial_adp - 1
    assert cell.get_metabolite_quantity("phosphoenolpyruvate") == initial_pep - 1
    assert cell.get_metabolite_quantity("pyruvate") == initial_pyruvate + 1
    assert initial_atp + initial_adp == cell.get_metabolite_quantity(
        "ATP"
    ) + cell.get_metabolite_quantity("ADP")


def test_adenine_nucleotide_conservation(cell):
    initial_total = (
        cell.get_metabolite_quantity("ATP")
        + cell.get_metabolite_quantity("ADP")
        + cell.get_metabolite_quantity("AMP")
    )

    # Execute all glycolysis reactions
    for reaction in GlycolysisReactions.__dict__.values():
        if isinstance(reaction, Reaction):
            reaction.execute(cell)

    final_total = (
        cell.get_metabolite_quantity("ATP")
        + cell.get_metabolite_quantity("ADP")
        + cell.get_metabolite_quantity("AMP")
    )

    assert pytest.approx(initial_total, rel=1e-9) == final_total
