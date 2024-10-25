from pyology.common_enzymes import *
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

    lactate_dehydrogenase = Reaction(
        name="Lactate Dehydrogenase",
        substrates={"pyruvate": 1, "NADH": 1},
        products={"lactate": 1, "NAD+": 1},
        enzyme="Lactate dehydrogenase",
    )


class KrebsCycleReactions:
    citrate_synthase = Reaction(
        name="Citrate Synthase",
        enzyme=citrate_synthase,
        substrates={"Acetyl_CoA": 1, "Oxaloacetate": 1, "H2O": 1},
        products={"Citrate": 1, "CoA": 1},
    )

    aconitase = Reaction(
        name="Aconitase",
        enzyme=aconitase,
        substrates={"Citrate": 1},
        products={"Isocitrate": 1},
        reversible=True,
    )

    isocitrate_dehydrogenase = Reaction(
        name="Isocitrate Dehydrogenase",
        enzyme=isocitrate_dehydrogenase,
        substrates={"Isocitrate": 1, "NAD+": 1},
        products={"α_Ketoglutarate": 1, "CO2": 1, "NADH": 1},
    )

    alpha_ketoglutarate_dehydrogenase = Reaction(
        name="α_Ketoglutarate Dehydrogenase",
        enzyme=alpha_ketoglutarate_dehydrogenase,
        substrates={"α_Ketoglutarate": 1, "NAD+": 1, "CoA": 1},
        products={"Succinyl_CoA": 1, "CO2": 1, "NADH": 1},
    )

    succinyl_coa_synthetase = Reaction(
        name="Succinyl_CoA Synthetase",
        enzyme=succinyl_coa_synthetase,
        substrates={"Succinyl_CoA": 1, "ADP": 1, "Pi": 1},
        products={"Succinate": 1, "CoA": 1, "ATP": 1},
    )

    succinate_dehydrogenase = Reaction(
        name="Succinate Dehydrogenase",
        enzyme=succinate_dehydrogenase,
        substrates={"Succinate": 1, "FAD": 1},
        products={"Fumarate": 1, "FADH2": 1},
    )

    fumarase = Reaction(
        name="Fumarase",
        enzyme=fumarase,
        substrates={"Fumarate": 1, "H2O": 1},
        products={"Malate": 1},
        reversible=True,
    )

    malate_dehydrogenase = Reaction(
        name="Malate Dehydrogenase",
        enzyme=malate_dehydrogenase,
        substrates={"Malate": 1, "NAD+": 1},
        products={"Oxaloacetate": 1, "NADH": 1},
    )
