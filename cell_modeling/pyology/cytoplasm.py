from typing import Dict

from .exceptions import GlycolysisError
from .mitochondrion import GlycolysisSteps
from .organelle import Organelle


class Cytoplasm(Organelle):
    name = "Cytoplasm"
    def __init__(self):
        super().__init__()
        self.add_metabolite("glucose", 100, 1000)  # Start with some glucose
        self.add_metabolite("atp", 100, 1000)  # Start with some ATP
        self.add_metabolite("adp", 100, 1000)  # Start with some ADP
        self.add_metabolite("nad", 100, 1000)
        self.add_metabolite("nadh", 0, 1000)
        self.add_metabolite("pyruvate", 0, 1000)
        self.glycolysis_rate = 1.0

    def glycolysis(self, glucose_units: int):
        if not isinstance(glucose_units, int):
            raise TypeError("The number of glucose units must be an integer.")
        if glucose_units < 0:
            raise ValueError("The number of glucose units cannot be negative.")
        if glucose_units == 0:
            return 0  # No action needed for zero units

        # Proceed with glycolysis steps
        try:
            self.change_metabolite_quantity("glucose", -glucose_units)
            for step in GlycolysisSteps:
                getattr(self, f"{step.name.lower()}")()
            return self.get_metabolite_quantity("pyruvate")
        except ValueError as e:
            # Handle the exception or re-raise it
            raise GlycolysisError(f"Glycolysis failed: {str(e)}")

    def ensure_metabolite_availability(self, metabolite: str, amount: float):
        if not self.is_metabolite_available(metabolite, amount):
            if metabolite == "atp" and self.is_metabolite_available("adp", amount):
                self.change_metabolite_quantity("adp", -amount)
                self.change_metabolite_quantity("atp", amount)
            elif metabolite == "adp" and self.is_metabolite_available("atp", amount):
                self.change_metabolite_quantity("atp", -amount)
                self.change_metabolite_quantity("adp", amount)
            else:
                raise ValueError(f"Insufficient {metabolite} for reaction")

    def is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        """Check if a metabolite is available in sufficient quantity."""
        if metabolite in self.metabolites:
            return self.metabolites[metabolite].quantity >= amount
        else:
            raise ValueError(f"Unknown metabolite: {metabolite}")

    def consume_metabolites(self, **metabolites: Dict[str, float]):
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise TypeError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise TypeError("Amounts must be numbers.")
            if amount < 0:
                raise ValueError(f"Cannot consume a negative amount of {metabolite}.")
            if metabolite not in self.metabolites:
                raise ValueError(f"Unknown metabolite: {metabolite}")
            if self.metabolites[metabolite].quantity < amount:
                raise ValueError(f"Insufficient {metabolite} for reaction.")

        # If all validations pass, proceed to consume
        for metabolite, amount in metabolites.items():
            self.metabolites[metabolite].quantity -= amount
        return True

    def produce_metabolites(self, **metabolites: Dict[str, float]):
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise TypeError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise TypeError("Amounts must be numbers.")
            if amount < 0:
                raise ValueError(f"Cannot produce a negative amount of {metabolite}.")
            if metabolite not in self.metabolites:
                raise ValueError(f"Unknown metabolite: {metabolite}")
            new_quantity = self.metabolites[metabolite].quantity + amount
            if new_quantity > self.metabolites[metabolite].max_quantity:
                raise ValueError(
                    f"Cannot exceed max quantity for {metabolite}. Attempted to set {metabolite} to {new_quantity}, but max is {self.metabolites[metabolite].max_quantity}."
                )

        # If all validations pass, proceed to produce
        for metabolite, amount in metabolites.items():
            self.metabolites[metabolite].quantity += amount
        return True

    def step1_hexokinase(self):
        self.ensure_metabolite_availability("atp", 1)
        if self.consume_metabolites(glucose=1, atp=1):
            self.produce_metabolites(adp=1)
        else:
            raise ValueError("Insufficient glucose or ATP for hexokinase step")

    def step2_phosphoglucose_isomerase(self):
        pass

    def step3_phosphofructokinase(self):
        self.ensure_metabolite_availability("atp", 1)
        if self.consume_metabolites(atp=1):
            self.produce_metabolites(adp=1)

    def step4_aldolase(self):
        pass

    def step5_triose_phosphate_isomerase(self):
        pass

    def step6_glyceraldehyde_3_phosphate_dehydrogenase(self):
        self.ensure_metabolite_availability("nad", 2)
        if self.consume_metabolites(nad=2):
            self.produce_metabolites(nadh=2)

    def step7_phosphoglycerate_kinase(self):
        self.ensure_metabolite_availability("adp", 2)
        if self.consume_metabolites(adp=2):
            self.produce_metabolites(atp=2)

    def step8_phosphoglycerate_mutase(self):
        pass

    def step9_enolase(self):
        pass

    def step10_pyruvate_kinase(self):
        self.ensure_metabolite_availability("adp", 2)
        if self.consume_metabolites(adp=2):
            self.produce_metabolites(atp=2, pyruvate=2)

    def reset(self):
        self.__init__()

    def get_metabolite_quantity(self, metabolite_name: str) -> int:
        """Get the quantity of a specific metabolite."""
        if metabolite_name in self.metabolites:
            return self.metabolites[metabolite_name].quantity
        else:
            raise ValueError(f"Unknown metabolite: {metabolite_name}")
