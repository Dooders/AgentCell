initial_state = {
    "glucose": 1.0,
    "atp": 100.0,
    "adp": 10.0,
    "bisphosphoglycerate_1_3": 10.0,
    "phosphoglycerate": 10.0,
    "phosphoglycerate_3": 10.0,
    "phosphoglycerate_2": 10.0,
    "nad": 10.0,
    "nad+": 20.0,
    "nadh": 10.0,
    "fad": 10.0,
    "dihydroxyacetone_phosphate": 10.0,
    "pyruvate": 0.0,
    "oxygen": 1000.0,
    "h2o": 1000.0,
    "pi": 10.0,
    "phosphoglycerate_1_3": 10.0,
    "oxaloacetate": 10.0,
    "citrate": 10.0,
    "coa": 10.0,
    "isocitrate": 10.0,
    "α_ketoglutarate": 10.0,
    "succinyl_coa": 10.0,
    "succinate": 10.0,
    "fumarate": 10.0,
    "malate": 10.0,
}

final_state = {
    "glucose": 0.0,
    "atp": 102.0,
    "adp": 8.0,
    "bisphosphoglycerate_1_3": 10.0,
    "phosphoglycerate": 10.0,
    "phosphoglycerate_3": 10.0,
    "phosphoglycerate_2": 10.0,
    "nad": 10.0,
    "nad+": 18.0,
    "nadh": 12.0,
    "fad": 10.0,
    "dihydroxyacetone_phosphate": 10.0,
    "pyruvate": 2.0,
    "oxygen": 1000.0,
    "h2o": 1002.0,
    "pi": 8.0,
    "phosphoglycerate_1_3": 10.0,
    "oxaloacetate": 10.0,
    "citrate": 10.0,
    "coa": 10.0,
    "isocitrate": 10.0,
    "α_ketoglutarate": 10.0,
    "succinyl_coa": 10.0,
    "succinate": 10.0,
    "fumarate": 10.0,
    "malate": 10.0,
}

template = {
    metabolite: final_state[metabolite] - initial_state[metabolite]
    for metabolite in initial_state.keys()
}


final_template = {
    "glucose": -1.0,
    "atp": 2.0,
    "adp": 2.0,
    "nad+": -2.0,
    "nadh": 2.0,
    "pi": -2.0,
    "pyruvate": 2.0,
    "h2o": 2.0,
}

