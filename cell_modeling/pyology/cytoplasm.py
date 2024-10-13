import math
from typing import Dict

from .exceptions import GlycolysisError
from .mitochondrion import GlycolysisSteps
from .organelle import Organelle


class Cytoplasm(Organelle):
    """
    The cytoplasm is the fluid-filled space inside the cell that contains the
    cell's organelles and performs many of the cell's metabolic functions.

    Attributes:
        glycolysis_rate (float): The rate at which glucose is processed during glycolysis.
    """

    name = "Cytoplasm"

    def __init__(self, glycolysis_rate: float = 1.0):
        super().__init__()
        self.add_metabolite("glucose", 100, 1000)  # Start with some glucose
        self.add_metabolite("atp", 100, 1000)  # Start with some ATP
        self.add_metabolite("adp", 100, 1000)  # Start with some ADP
        self.add_metabolite("nad", 100, 1000)
        self.add_metabolite("nadh", 0, 1000)
        self.add_metabolite("pyruvate", 0, 1000)
        self.glycolysis_rate = glycolysis_rate

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
        # Round down to nearest integer
        glucose_units = math.floor(glucose_units)

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
                self.change_metabolite_quantity("adp", -amount)
                self.change_metabolite_quantity("atp", amount)
            elif metabolite == "adp" and self.is_metabolite_available("atp", amount):
                self.change_metabolite_quantity("atp", -amount)
                self.change_metabolite_quantity("adp", amount)
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
        if metabolite in self.metabolites:
            return self.metabolites[metabolite].quantity >= amount
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
            if metabolite not in self.metabolites:
                raise ValueError(f"Unknown metabolite: {metabolite}")
            if self.metabolites[metabolite].quantity < amount:
                raise ValueError(f"Insufficient {metabolite} for reaction.")

        # If all validations pass, proceed to consume
        for metabolite, amount in metabolites.items():
            self.metabolites[metabolite].quantity -= amount
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

    def step1_hexokinase(self) -> bool:
        """
        Step 1 of glycolysis: Hexokinase reaction.

        This step consumes 1 glucose and 1 ATP, and produces 1 ADP.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("atp", 1)
        if self.consume_metabolites(glucose=1, atp=1):
            self.produce_metabolites(adp=1)
        else:
            raise ValueError("Insufficient glucose or ATP for hexokinase step")

    def step2_phosphoglucose_isomerase(self) -> bool:
        """
        Step 2 of glycolysis: Phosphoglucose isomerase reaction.

        This step consumes 1 glucose-6-phosphate and produces 1 fructose-6-phosphate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        pass

    def step3_phosphofructokinase(self) -> bool:
        """
        Step 3 of glycolysis: Phosphofructokinase reaction.

        This step consumes 1 ATP, and produces 1 ADP.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("atp", 1)
        if self.consume_metabolites(atp=1):
            self.produce_metabolites(adp=1)

    def step4_aldolase(self) -> bool:
        """
        Step 4 of glycolysis: Aldolase reaction.

        This step consumes 1 fructose-6-phosphate and produces 2 glyceraldehyde-3-phosphate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("fructose_6_phosphate", 1)
        if self.consume_metabolites(fructose_6_phosphate=1):
            self.produce_metabolites(glyceraldehyde_3_phosphate=2)

    def step5_triose_phosphate_isomerase(self) -> bool:
        """
        Step 5 of glycolysis: Triose phosphate isomerase reaction.

        This step consumes 2 glyceraldehyde-3-phosphate and produces 2 dihydroxyacetone phosphate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("glyceraldehyde_3_phosphate", 2)
        if self.consume_metabolites(glyceraldehyde_3_phosphate=2):
            self.produce_metabolites(dihydroxyacetone_phosphate=2)

    def step6_glyceraldehyde_3_phosphate_dehydrogenase(self) -> bool:
        """
        Step 6 of glycolysis: Glyceraldehyde-3-phosphate dehydrogenase reaction.

        This step consumes 2 dihydroxyacetone phosphate and produces 2 3-phosphoglycerate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("nad", 2)
        if self.consume_metabolites(nad=2):
            self.produce_metabolites(nadh=2)

    def step7_phosphoglycerate_kinase(self) -> bool:
        """
        Step 7 of glycolysis: Phosphoglycerate kinase reaction.

        This step consumes 2 ADP, and produces 2 ATP.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("adp", 2)
        if self.consume_metabolites(adp=2):
            self.produce_metabolites(atp=2)

    def step8_phosphoglycerate_mutase(self) -> bool:
        """
        Step 8 of glycolysis: Phosphoglycerate mutase reaction.

        This step consumes 2 3-phosphoglycerate and produces 2 phosphoenolpyruvate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("phosphoenolpyruvate", 2)
        if self.consume_metabolites(phosphoenolpyruvate=2):
            self.produce_metabolites(pyruvate=2)

    def step9_enolase(self) -> bool:
        """
        Step 9 of glycolysis: Enolase reaction.

        This step consumes 2 phosphoenolpyruvate and produces 2 pyruvate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("adp", 2)
        if self.consume_metabolites(adp=2):
            self.produce_metabolites(atp=2, pyruvate=2)

    def step10_pyruvate_kinase(self) -> bool:
        """
        Step 10 of glycolysis: Pyruvate kinase reaction.

        This step consumes 2 ADP, and produces 2 ATP and 2 pyruvate.

        Returns
        -------
        bool
            True if the reaction was successful, False otherwise.
        """
        self.ensure_metabolite_availability("adp", 2)
        if self.consume_metabolites(adp=2):
            self.produce_metabolites(atp=2, pyruvate=2)

    def reset(self) -> None:
        self.__init__()

    def get_metabolite_quantity(self, metabolite_name: str) -> int:
        """
        Get the quantity of a specific metabolite.
        """
        if metabolite_name in self.metabolites:
            return self.metabolites[metabolite_name].quantity
        else:
            raise ValueError(f"Unknown metabolite: {metabolite_name}")
