from pyology.common_enzymes import (
    aldolase,
    enolase,
    glyceraldehyde_3_phosphate_dehydrogenase,
    hexokinase,
    phosphofructokinase,
    phosphoglucose_isomerase,
    phosphoglycerate_kinase,
    phosphoglycerate_mutate,
    pyruvate_kinase,
    triose_phosphate_isomerase,
)
from pyology.reaction import Reaction


class GlycolysisReactions:
    hexokinase = Reaction(
        name="Hexokinase",
        substrates={"glucose": 1, "ATP": 1},
        products={"glucose_6_phosphate": 1, "ADP": 1},
        enzyme="hexokinase",
    )

    phosphoglucose_isomerase = Reaction(
        name="Phosphoglucose Isomerase",
        substrates={"glucose_6_phosphate": 1},
        products={"fructose_6_phosphate": 1},
        enzyme="Phosphoglucose isomerase",
    )

    phosphofructokinase = Reaction(
        name="Phosphofructokinase",
        substrates={"fructose_6_phosphate": 1, "ATP": 1},
        products={"fructose_1_6_bisphosphate": 1, "ADP": 1},
        enzyme="Phosphofructokinase",
    )

    aldolase = Reaction(
        name="Aldolase",
        substrates={"fructose_1_6_bisphosphate": 1},
        products={"dihydroxyacetone_phosphate": 1, "glyceraldehyde_3_phosphate": 1},
        enzyme="Aldolase",
    )

    triose_phosphate_isomerase = Reaction(
        name="Triose Phosphate Isomerase",
        substrates={"dihydroxyacetone_phosphate": 1},
        products={"glyceraldehyde_3_phosphate": 1},
        enzyme="Triose phosphate isomerase",
    )

    glyceraldehyde_3_phosphate_dehydrogenase = Reaction(
        name="Glyceraldehyde 3-Phosphate Dehydrogenase",
        substrates={"glyceraldehyde_3_phosphate": 1, "NAD+": 1, "Pi": 1},
        products={"bisphosphoglycerate_1_3": 1, "NADH": 1},
        enzyme="Glyceraldehyde 3-phosphate dehydrogenase",
    )

    phosphoglycerate_kinase = Reaction(
        name="Phosphoglycerate Kinase",
        substrates={"bisphosphoglycerate_1_3": 1, "ADP": 1},
        products={"phosphoglycerate_3": 1, "ATP": 1},
        enzyme="Phosphoglycerate kinase",
    )

    phosphoglycerate_mutate = Reaction(
        name="Phosphoglycerate Mutase",
        substrates={"phosphoglycerate_3": 1},
        products={"phosphoglycerate_2": 1},
        enzyme="Phosphoglycerate mutase",
    )

    enolase = Reaction(
        name="Enolase",
        substrates={"phosphoglycerate_2": 1},
        products={"phosphoenolpyruvate": 1, "H2O": 1},
        enzyme="Enolase",
    )

    pyruvate_kinase = Reaction(
        name="Pyruvate Kinase",
        substrates={"phosphoenolpyruvate": 1, "ADP": 1},
        products={"pyruvate": 1, "ATP": 1},
        enzyme="Pyruvate kinase",
    )
