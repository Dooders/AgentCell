import math
from typing import Dict

from .exceptions import GlycolysisError
from .mitochondrion import GlycolysisSteps


class GlycolysisPathway:
    """
    Class representing the glycolysis pathway.
    """

    def __init__(self, organelle):
        self.organelle = organelle

    def glycolysis(self, glucose_units: float) -> float:
        """
        Perform glycolysis on the given number of glucose units.

        Glycolysis is the process by which glucose is converted into pyruvate,
        releasing energy in the form of ATP.

        Parameters
        ----------
        glucose_units : float
            The number of glucose units to process.

        Returns
        -------
        float
            The amount of pyruvate produced.
        """
        glucose_units = math.floor(glucose_units)
        if glucose_units < 0:
            raise ValueError("The number of glucose units cannot be negative.")
        if glucose_units == 0:
            return 0

        try:
            self.organelle.change_metabolite_quantity("glucose", -glucose_units)
            for _ in range(glucose_units):
                for step in GlycolysisSteps:
                    if not getattr(self, step.value)():
                        raise GlycolysisError(f"Failed at step: {step.name}")
            return self.organelle.get_metabolite_quantity("pyruvate")
        except ValueError as e:
            raise GlycolysisError(f"Glycolysis failed: {str(e)}")

    def ensure_metabolite_availability(self, metabolite: str, amount: float) -> bool:
        """
        Ensure that a metabolite is available in sufficient quantity.

        Parameters
        ----------
        metabolite : str
            The name of the metabolite to ensure availability of.
        amount : float
            The amount of the metabolite to ensure availability of.

        Returns
        -------
        bool
            True if the metabolite is available in sufficient quantity, False otherwise.
        """
        if not self.is_metabolite_available(metabolite, amount):
            if metabolite == "atp" and self.is_metabolite_available("adp", amount):
                self.organelle.change_metabolite_quantity("adp", -amount)
                self.organelle.change_metabolite_quantity("atp", amount)
            elif metabolite == "adp" and self.is_metabolite_available("atp", amount):
                self.organelle.change_metabolite_quantity("atp", -amount)
                self.organelle.change_metabolite_quantity("adp", amount)
            else:
                raise ValueError(f"Insufficient {metabolite} for reaction")

    def is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        """
        Check if a metabolite is available in sufficient quantity.

        Parameters
        ----------
        metabolite : str
            The name of the metabolite to check availability of.
        amount : float
            The amount of the metabolite to check availability of.

        Returns
        -------
        bool
            True if the metabolite is available in sufficient quantity, False otherwise.
        """
        if metabolite in self.organelle.metabolites:
            return self.organelle.metabolites[metabolite].quantity >= amount
        else:
            raise ValueError(f"Unknown metabolite: {metabolite}")

    def consume_metabolites(self, **metabolites: Dict[str, float]) -> bool:
        """
        Consume a given amount of each metabolite.

        Parameters
        ----------
        metabolites : Dict[str, float]
            A dictionary of metabolite names and their corresponding amounts to consume.

        Returns
        -------
        bool
            True if the metabolites were consumed successfully, False otherwise.
        """
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise TypeError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise TypeError("Amounts must be numbers.")
            if amount < 0:
                raise ValueError(f"Cannot consume a negative amount of {metabolite}.")
            if metabolite not in self.organelle.metabolites:
                raise ValueError(f"Unknown metabolite: {metabolite}")
            if self.organelle.metabolites[metabolite].quantity < amount:
                raise ValueError(f"Insufficient {metabolite} for reaction.")

        # If all validations pass, proceed to consume
        for metabolite, amount in metabolites.items():
            self.organelle.metabolites[metabolite].quantity -= amount
        return True

    def produce_metabolites(self, **metabolites: Dict[str, float]) -> bool:
        """
        Produce a given amount of each metabolite.

        Parameters
        ----------
        metabolites : Dict[str, float]
            A dictionary of metabolite names and their corresponding amounts to produce.

        Returns
        -------
        bool
            True if the metabolites were produced successfully, False otherwise.
        """
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise TypeError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise TypeError("Amounts must be numbers.")
            if amount < 0:
                raise ValueError(f"Cannot produce a negative amount of {metabolite}.")
            if metabolite not in self.organelle.metabolites:
                raise ValueError(f"Unknown metabolite: {metabolite}")
            new_quantity = self.organelle.metabolites[metabolite].quantity + amount
            if new_quantity > self.organelle.metabolites[metabolite].max_quantity:
                raise ValueError(
                    f"Cannot exceed max quantity for {metabolite}. Attempted to set {metabolite} to {new_quantity}, but max is {self.organelle.metabolites[metabolite].max_quantity}."
                )

        # If all validations pass, proceed to produce
        for metabolite, amount in metabolites.items():
            self.organelle.metabolites[metabolite].quantity += amount
        return True

    def step1_hexokinase(self) -> bool:
        """
        Step 1 of glycolysis: Hexokinase reaction.

        This step consumes 1 glucose and 1 ATP, and produces 1 glucose-6-phosphate and 1 ADP.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("glucose", 1)
        self.ensure_metabolite_availability("atp", 1)
        if self.consume_metabolites(glucose=1, atp=1):
            return self.produce_metabolites(glucose_6_phosphate=1, adp=1)
        return False

    def step2_phosphoglucose_isomerase(self) -> bool:
        """
        Step 2 of glycolysis: Phosphoglucose isomerase reaction.

        This step consumes 1 glucose-6-phosphate and produces 1 fructose-6-phosphate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("glucose_6_phosphate", 1)
        if self.consume_metabolites(glucose_6_phosphate=1):
            return self.produce_metabolites(fructose_6_phosphate=1)
        return False

    def step3_phosphofructokinase(self) -> bool:
        """
        Step 3 of glycolysis: Phosphofructokinase reaction.

        This step consumes 1 ATP and produces 1 ADP.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("fructose_6_phosphate", 1)
        self.ensure_metabolite_availability("atp", 1)
        if self.consume_metabolites(fructose_6_phosphate=1, atp=1):
            return self.produce_metabolites(fructose_1_6_bisphosphate=1, adp=1)
        return False

    def step4_aldolase(self) -> bool:
        """
        Step 4 of glycolysis: Aldolase reaction.

        This step consumes 1 fructose-1,6-bisphosphate and produces 1 glyceraldehyde-3-phosphate and 1 dihydroxyacetone phosphate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("fructose_1_6_bisphosphate", 1)
        if self.consume_metabolites(fructose_1_6_bisphosphate=1):
            return self.produce_metabolites(
                glyceraldehyde_3_phosphate=1, dihydroxyacetone_phosphate=1
            )
        return False

    def step5_triose_phosphate_isomerase(self) -> bool:
        """
        Step 5 of glycolysis: Triose phosphate isomerase reaction.

        This step converts dihydroxyacetone phosphate to glyceraldehyde-3-phosphate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("dihydroxyacetone_phosphate", 1)
        if self.consume_metabolites(dihydroxyacetone_phosphate=1):
            return self.produce_metabolites(glyceraldehyde_3_phosphate=1)
        return False

    def step6_glyceraldehyde_3_phosphate_dehydrogenase(self) -> bool:
        """
        Step 6 of glycolysis: Glyceraldehyde-3-phosphate dehydrogenase reaction.

        This step consumes 1 glyceraldehyde-3-phosphate and 1 NAD+, and produces 1 1,3-bisphosphoglycerate and 1 NADH.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("glyceraldehyde_3_phosphate", 1)
        self.ensure_metabolite_availability("nad", 1)
        if self.consume_metabolites(glyceraldehyde_3_phosphate=1, nad=1):
            return self.produce_metabolites(bisphosphoglycerate_1_3=1, nadh=1)
        return False

    def step7_phosphoglycerate_kinase(self) -> bool:
        """
        Step 7 of glycolysis: Phosphoglycerate kinase reaction.

        This step consumes 1 1,3-bisphosphoglycerate and 1 ADP, and produces 1 3-phosphoglycerate and 1 ATP.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("bisphosphoglycerate_1_3", 1)
        self.ensure_metabolite_availability("adp", 1)
        if self.consume_metabolites(bisphosphoglycerate_1_3=1, adp=1):
            return self.produce_metabolites(phosphoglycerate_3=1, atp=1)
        return False

    def step8_phosphoglycerate_mutase(self) -> bool:
        """
        Step 8 of glycolysis: Phosphoglycerate mutase reaction.

        This step consumes 1 3-phosphoglycerate and produces 1 2-phosphoglycerate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("phosphoglycerate_3", 1)
        if self.consume_metabolites(phosphoglycerate_3=1):
            return self.produce_metabolites(phosphoglycerate_2=1)
        return False

    def step9_enolase(self) -> bool:
        """
        Step 9 of glycolysis: Enolase reaction.

        This step consumes 1 2-phosphoglycerate and produces 1 phosphoenolpyruvate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("phosphoglycerate_2", 1)
        if self.consume_metabolites(phosphoglycerate_2=1):
            return self.produce_metabolites(phosphoenolpyruvate=1)
        return False

    def step10_pyruvate_kinase(self) -> bool:
        """
        Step 10 of glycolysis: Pyruvate kinase reaction.

        This step consumes 1 phosphoenolpyruvate and 1 ADP, and produces 1 pyruvate and 1 ATP.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("phosphoenolpyruvate", 1)
        self.ensure_metabolite_availability("adp", 1)
        if self.consume_metabolites(phosphoenolpyruvate=1, adp=1):
            return self.produce_metabolites(pyruvate=1, atp=1)
        return False
