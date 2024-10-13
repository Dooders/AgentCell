def test_glycolysis():
    cytoplasm = Cytoplasm()
    
    # Set initial metabolite quantities
    cytoplasm.change_metabolite_quantity("glucose", 10)
    cytoplasm.change_metabolite_quantity("atp", 20)
    cytoplasm.change_metabolite_quantity("nad", 20)
    
    # Perform glycolysis
    pyruvate_produced = cytoplasm.glycolysis(5)
    
    # Check results
    assert pyruvate_produced == 10  # 2 pyruvate per glucose
    assert cytoplasm.get_metabolite_quantity("glucose") == 5
    assert cytoplasm.get_metabolite_quantity("pyruvate") == 10
    assert cytoplasm.get_metabolite_quantity("atp") > 20  # Net gain in ATP
    assert cytoplasm.get_metabolite_quantity("nadh") == 10  # 2 NADH per glucose
