from pyology.enzymes import Enzyme

hexokinase = Enzyme(
    name="Hexokinase",
    k_cat=1.0,
    k_m={"glucose": 0.1},
)

phosphoglucose_isomerase = Enzyme(
    name="Phosphoglucose Isomerase",
    k_cat=100,
    k_m={"glucose_6_phosphate": 10},
)

phosphofructokinase = Enzyme(
    name="Phosphofructokinase",
    k_cat=100,
    k_m={"fructose_6_phosphate": 10},
)

aldolase = Enzyme(
    name="Aldolase",
    k_cat=100,
    k_m={"fructose_1_6_bisphosphate": 10},
)

triose_phosphate_isomerase = Enzyme(
    name="Triose Phosphate Isomerase",
    k_cat=100,
    k_m={"glyceraldehyde_3_phosphate": 10},
)

glyceraldehyde_3_phosphate_dehydrogenase = Enzyme(
    name="Glyceraldehyde 3-Phosphate Dehydrogenase",
    k_cat=100,
    k_m={"glyceraldehyde_3_phosphate": 10},
)

phosphoglycerate_kinase = Enzyme(
    name="Phosphoglycerate Kinase",
    k_cat=100,
    k_m={"bisphosphoglycerate_1_3": 10},
)

phosphoglycerate_mutase = Enzyme(
    name="Phosphoglycerate Mutase",
    k_cat=100,
    k_m={"phosphoglycerate_3": 10},
)

enolase = Enzyme(
    name="Enolase",
    k_cat=100,
    k_m={"phosphoglycerate": 10},
)

pyruvate_kinase = Enzyme(
    name="Pyruvate Kinase",
    k_cat=100,
    k_m={"phosphoenolpyruvate": 10},
)

pyruvate_dehydrogenase = Enzyme(
    name="Pyruvate Dehydrogenase",
    k_cat=100,
    k_m={"pyruvate": 10},
)

pyruvate_carboxylase = Enzyme(
    name="Pyruvate Carboxylase",
    k_cat=100,
    k_m={"pyruvate": 10},
)

phosphoglycerate_mutate = Enzyme(
    name="Phosphoglycerate Mutase",
    k_cat=100,
    k_m={"phosphoglycerate_3": 10},
)
