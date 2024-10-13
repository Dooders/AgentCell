from typing import Dict
from .enzymes import Enzyme

class Reaction:
    def __init__(self, name: str, enzyme: Enzyme, consume: Dict[str, float], produce: Dict[str, float]):
        self.name = name
        self.enzyme = enzyme
        self.consume = consume
        self.produce = produce
    
    def execute(self, organelle, time_step: float = 1.0) -> float:
        substrate = list(self.consume.keys())[0]  # Assume first consumed metabolite is the substrate
        substrate_conc = organelle.get_metabolite_quantity(substrate)
        
        # Calculate reaction rate
        reaction_rate = self.enzyme.calculate_rate(substrate_conc, organelle.metabolites) * time_step
        
        # Determine actual rate based on available metabolites
        actual_rate = min(reaction_rate, substrate_conc, 
                          *[organelle.get_metabolite_quantity(met) / amount 
                            for met, amount in self.consume.items()])
        
        # Consume metabolites
        for metabolite, amount in self.consume.items():
            organelle.change_metabolite_quantity(metabolite, -amount * actual_rate)
        
        # Produce metabolites
        for metabolite, amount in self.produce.items():
            organelle.change_metabolite_quantity(metabolite, amount * actual_rate)
        
        return actual_rate
