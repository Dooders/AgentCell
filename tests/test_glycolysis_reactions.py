import pytest

from pyology.common_reactions import GlycolysisReactions
from pyology.organelle import Organelle


@pytest.fixture
def organelle():
    org = Organelle()
    # Set initial quantities for all metabolites
    metabolites = {
        "glucose": 5,
        "ATP": 5,
        "ADP": 5,
        "AMP": 5,
        "glucose_6_phosphate": 5,
        "fructose_6_phosphate": 5,
        "fructose_1_6_bisphosphate": 5,
        "dihydroxyacetone_phosphate": 5,
        "glyceraldehyde_3_phosphate": 5,
        "phosphoglycerate": 5,
        "phosphoenolpyruvate": 5,
        "pyruvate": 5,
        "NAD": 5,
        "NADH": 5,
        "bisphosphoglycerate_1_3": 5,
    }
    for name, quantity in metabolites.items():
        org.set_metabolite_quantity(name, quantity)
    return org


def test_hexokinase(organelle):
    reaction = GlycolysisReactions.hexokinase
    initial_glucose = organelle.get_metabolite_quantity("glucose")
    initial_atp = organelle.get_metabolite_quantity("ATP")
    initial_glucose_6_phosphate = organelle.get_metabolite_quantity(
        "glucose_6_phosphate"
    )
    initial_adp = organelle.get_metabolite_quantity("ADP")
    reaction.execute(organelle)

    consumed = min(initial_glucose, initial_atp)

    assert organelle.get_metabolite_quantity("glucose") == pytest.approx(
        initial_glucose - consumed, abs=1e-6
    )
    assert organelle.get_metabolite_quantity("ATP") == pytest.approx(
        initial_atp - consumed, abs=1e-6
    )
    assert organelle.get_metabolite_quantity("glucose_6_phosphate") == pytest.approx(
        initial_glucose_6_phosphate + consumed, abs=1e-6
    )
    assert organelle.get_metabolite_quantity("ADP") == pytest.approx(
        initial_adp + consumed, abs=1e-6
    )


def test_phosphoglucose_isomerase(organelle):
    reaction = GlycolysisReactions.phosphoglucose_isomerase
    initial_glucose_6_phosphate = organelle.get_metabolite_quantity(
        "glucose_6_phosphate"
    )
    initial_fructose_6_phosphate = organelle.get_metabolite_quantity(
        "fructose_6_phosphate"
    )
    reaction.execute(organelle)
    assert organelle.get_metabolite_quantity("glucose_6_phosphate") == pytest.approx(
        0, abs=1e-6
    )
    assert organelle.get_metabolite_quantity("fructose_6_phosphate") == pytest.approx(
        initial_fructose_6_phosphate + initial_glucose_6_phosphate, abs=1e-6
    )


def test_phosphofructokinase(organelle):
    reaction = GlycolysisReactions.phosphofructokinase
    initial_fructose_6_phosphate = organelle.get_metabolite_quantity(
        "fructose_6_phosphate"
    )
    initial_atp = organelle.get_metabolite_quantity("ATP")
    initial_fructose_1_6_bisphosphate = organelle.get_metabolite_quantity(
        "fructose_1_6_bisphosphate"
    )
    initial_adp = organelle.get_metabolite_quantity("ADP")
    reaction.execute(organelle)
    consumed = min(initial_fructose_6_phosphate, initial_atp)
    assert organelle.get_metabolite_quantity("fructose_6_phosphate") == pytest.approx(
        0, abs=1e-6
    )
    assert organelle.get_metabolite_quantity("ATP") == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity(
        "fructose_1_6_bisphosphate"
    ) == pytest.approx(initial_fructose_1_6_bisphosphate + consumed, abs=1e-6)
    assert organelle.get_metabolite_quantity("ADP") == pytest.approx(
        initial_adp + consumed, abs=1e-6
    )


def test_aldolase(organelle):
    reaction = GlycolysisReactions.aldolase
    initial_fructose_1_6_bisphosphate = organelle.get_metabolite_quantity(
        "fructose_1_6_bisphosphate"
    )
    initial_dihydroxyacetone_phosphate = organelle.get_metabolite_quantity(
        "dihydroxyacetone_phosphate"
    )
    initial_glyceraldehyde_3_phosphate = organelle.get_metabolite_quantity(
        "glyceraldehyde_3_phosphate"
    )
    reaction.execute(organelle)
    assert organelle.get_metabolite_quantity(
        "fructose_1_6_bisphosphate"
    ) == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity(
        "dihydroxyacetone_phosphate"
    ) == pytest.approx(
        initial_dihydroxyacetone_phosphate + initial_fructose_1_6_bisphosphate, abs=1e-6
    )
    assert organelle.get_metabolite_quantity(
        "glyceraldehyde_3_phosphate"
    ) == pytest.approx(
        initial_glyceraldehyde_3_phosphate + initial_fructose_1_6_bisphosphate, abs=1e-6
    )


def test_triose_phosphate_isomerase(organelle):
    reaction = GlycolysisReactions.triose_phosphate_isomerase
    initial_glyceraldehyde_3_phosphate = organelle.get_metabolite_quantity(
        "glyceraldehyde_3_phosphate"
    )
    initial_dihydroxyacetone_phosphate = organelle.get_metabolite_quantity(
        "dihydroxyacetone_phosphate"
    )
    reaction.execute(organelle)
    assert organelle.get_metabolite_quantity(
        "glyceraldehyde_3_phosphate"
    ) == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity(
        "dihydroxyacetone_phosphate"
    ) == pytest.approx(
        initial_dihydroxyacetone_phosphate + initial_glyceraldehyde_3_phosphate,
        abs=1e-6,
    )


def test_phosphoglycerate_kinase(organelle):
    reaction = GlycolysisReactions.phosphoglycerate_kinase
    initial_glyceraldehyde_3_phosphate = organelle.get_metabolite_quantity(
        "glyceraldehyde_3_phosphate"
    )
    initial_adp = organelle.get_metabolite_quantity("ADP")
    initial_phosphoglycerate = organelle.get_metabolite_quantity("phosphoglycerate")
    initial_atp = organelle.get_metabolite_quantity("ATP")
    reaction.execute(organelle)
    consumed = min(initial_glyceraldehyde_3_phosphate, initial_adp)
    assert organelle.get_metabolite_quantity(
        "glyceraldehyde_3_phosphate"
    ) == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity("ADP") == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity("phosphoglycerate") == pytest.approx(
        initial_phosphoglycerate + consumed, abs=1e-6
    )
    assert organelle.get_metabolite_quantity("ATP") == pytest.approx(
        initial_atp + consumed, abs=1e-6
    )


def test_phosphoglycerate_mutase(organelle):
    reaction = GlycolysisReactions.phosphoglycerate_mutase
    initial_phosphoglycerate = organelle.get_metabolite_quantity("phosphoglycerate")
    initial_dihydroxyacetone_phosphate = organelle.get_metabolite_quantity(
        "dihydroxyacetone_phosphate"
    )
    reaction.execute(organelle)
    assert organelle.get_metabolite_quantity("phosphoglycerate") == pytest.approx(
        0, abs=1e-6
    )
    assert organelle.get_metabolite_quantity(
        "dihydroxyacetone_phosphate"
    ) == pytest.approx(
        initial_dihydroxyacetone_phosphate + initial_phosphoglycerate, abs=1e-6
    )


def test_enolase(organelle):
    reaction = GlycolysisReactions.enolase
    initial_dihydroxyacetone_phosphate = organelle.get_metabolite_quantity(
        "dihydroxyacetone_phosphate"
    )
    initial_phosphoenolpyruvate = organelle.get_metabolite_quantity(
        "phosphoenolpyruvate"
    )
    reaction.execute(organelle)
    assert organelle.get_metabolite_quantity(
        "dihydroxyacetone_phosphate"
    ) == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity("phosphoenolpyruvate") == pytest.approx(
        initial_phosphoenolpyruvate + initial_dihydroxyacetone_phosphate, abs=1e-6
    )


def test_pyruvate_kinase(organelle):
    reaction = GlycolysisReactions.pyruvate_kinase
    initial_phosphoenolpyruvate = organelle.get_metabolite_quantity(
        "phosphoenolpyruvate"
    )
    initial_adp = organelle.get_metabolite_quantity("ADP")
    initial_pyruvate = organelle.get_metabolite_quantity("pyruvate")
    initial_atp = organelle.get_metabolite_quantity("ATP")
    reaction.execute(organelle)
    consumed = min(initial_phosphoenolpyruvate, initial_adp)
    assert organelle.get_metabolite_quantity("phosphoenolpyruvate") == pytest.approx(
        0, abs=1e-6
    )
    assert organelle.get_metabolite_quantity("ADP") == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity("pyruvate") == pytest.approx(
        initial_pyruvate + consumed, abs=1e-6
    )
    assert organelle.get_metabolite_quantity("ATP") == pytest.approx(
        initial_atp + consumed, abs=1e-6
    )


def test_glyceraldehyde_3_phosphate_dehydrogenase(organelle):
    reaction = GlycolysisReactions.glyceraldehyde_3_phosphate_dehydrogenase
    initial_glyceraldehyde_3_phosphate = organelle.get_metabolite_quantity(
        "glyceraldehyde_3_phosphate"
    )
    initial_nad = organelle.get_metabolite_quantity("NAD")
    initial_bisphosphoglycerate_1_3 = organelle.get_metabolite_quantity(
        "bisphosphoglycerate_1_3"
    )
    initial_nadh = organelle.get_metabolite_quantity("NADH")
    reaction.execute(organelle)
    consumed = min(initial_glyceraldehyde_3_phosphate, initial_nad)
    assert organelle.get_metabolite_quantity(
        "glyceraldehyde_3_phosphate"
    ) == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity("NAD") == pytest.approx(0, abs=1e-6)
    assert organelle.get_metabolite_quantity(
        "bisphosphoglycerate_1_3"
    ) == pytest.approx(initial_bisphosphoglycerate_1_3 + consumed, abs=1e-6)
    assert organelle.get_metabolite_quantity("NADH") == pytest.approx(
        initial_nadh + consumed, abs=1e-6
    )


def test_insufficient_metabolite(organelle):
    reaction = GlycolysisReactions.hexokinase
    organelle.set_metabolite_quantity("glucose", 0)
    organelle.set_metabolite_quantity("ATP", 5)  # Ensure ATP is available

    initial_glucose = organelle.get_metabolite_quantity("glucose")
    initial_atp = organelle.get_metabolite_quantity("ATP")
    initial_glucose_6_phosphate = organelle.get_metabolite_quantity(
        "glucose_6_phosphate"
    )
    initial_adp = organelle.get_metabolite_quantity("ADP")

    reaction.execute(organelle)

    # Check that no changes occurred
    assert organelle.get_metabolite_quantity("glucose") == initial_glucose
    assert organelle.get_metabolite_quantity("ATP") == initial_atp
    assert (
        organelle.get_metabolite_quantity("glucose_6_phosphate")
        == initial_glucose_6_phosphate
    )
    assert organelle.get_metabolite_quantity("ADP") == initial_adp

    print(f"Glucose: {organelle.get_metabolite_quantity('glucose')}")
    print(f"ATP: {organelle.get_metabolite_quantity('ATP')}")
    print(
        f"Glucose-6-phosphate: {organelle.get_metabolite_quantity('glucose_6_phosphate')}"
    )
    print(f"ADP: {organelle.get_metabolite_quantity('ADP')}")
