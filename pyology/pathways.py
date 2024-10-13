import math
from typing import Dict

from .exceptions import GlycolysisError, MetaboliteError
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

        Raises
        ------
        GlycolysisError
            If glycolysis fails at any step.
        """
        glucose_units = math.floor(glucose_units)
        if glucose_units < 0:
            raise GlycolysisError("The number of glucose units cannot be negative.")
        if glucose_units == 0:
            return 0

        try:
            # Check if there's enough glucose before starting the process
            self.ensure_metabolite_availability("glucose", glucose_units)

            # Now consume the glucose
            self.consume_metabolites(glucose=glucose_units)

            for _ in range(glucose_units):
                # Steps 1-4 occur once per glucose molecule
                for step in list(GlycolysisSteps)[:4]:
                    getattr(self, step.value)()

                # Step 5 occurs once to convert DHAP to G3P
                self.step5_triose_phosphate_isomerase()

                # Steps 6-10 occur twice per glucose molecule
                for _ in range(2):
                    for step in list(GlycolysisSteps)[5:]:
                        getattr(self, step.value)()

                # Adjust net ATP gain
                self.produce_metabolites(atp=2)

            return self.organelle.get_metabolite_quantity("pyruvate")
        except MetaboliteError as e:
            raise GlycolysisError(f"Glycolysis failed: {str(e)}")

    def ensure_metabolite_availability(self, metabolite: str, amount: float) -> None:
        """
        Ensure that a metabolite is available in sufficient quantity.

        Parameters
        ----------
        metabolite : str
            The name of the metabolite to ensure availability of.
        amount : float
            The amount of the metabolite to ensure availability of.

        Raises
        ------
        MetaboliteError
            If the metabolite is not available in sufficient quantity.
        """
        if not self.is_metabolite_available(metabolite, amount):
            if metabolite == "atp" and self.is_metabolite_available("adp", amount):
                self.organelle.change_metabolite_quantity("adp", -amount)
                self.organelle.change_metabolite_quantity("atp", amount)
            elif metabolite == "adp" and self.is_metabolite_available("atp", amount):
                self.organelle.change_metabolite_quantity("atp", -amount)
                self.organelle.change_metabolite_quantity("adp", amount)
            else:
                raise MetaboliteError(f"Insufficient {metabolite} for reaction")

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

        Raises
        ------
        MetaboliteError
            If the metabolite is unknown.
        """
        if metabolite in self.organelle.metabolites:
            return self.organelle.metabolites[metabolite].quantity >= amount
        else:
            raise MetaboliteError(f"Unknown metabolite: {metabolite}")

    def consume_metabolites(self, **metabolites: Dict[str, float]) -> None:
        """
        Consume a given amount of each metabolite.

        Parameters
        ----------
        metabolites : Dict[str, float]
            A dictionary of metabolite names and their corresponding amounts to consume.

        Raises
        ------
        MetaboliteError
            If there's an issue with metabolite consumption.
        """
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise MetaboliteError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise MetaboliteError("Amounts must be numbers.")
            if amount < 0:
                raise MetaboliteError(
                    f"Cannot consume a negative amount of {metabolite}."
                )
            if metabolite not in self.organelle.metabolites:
                raise MetaboliteError(f"Unknown metabolite: {metabolite}")
            if self.organelle.metabolites[metabolite].quantity < amount:
                raise MetaboliteError(f"Insufficient {metabolite} for reaction.")

        # If all validations pass, proceed to consume
        for metabolite, amount in metabolites.items():
            self.organelle.metabolites[metabolite].quantity -= amount

    def produce_metabolites(self, **metabolites: Dict[str, float]) -> None:
        """
        Produce a given amount of each metabolite.

        Parameters
        ----------
        metabolites : Dict[str, float]
            A dictionary of metabolite names and their corresponding amounts to produce.

        Raises
        ------
        MetaboliteError
            If there's an issue with metabolite production.
        """
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise MetaboliteError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise MetaboliteError("Amounts must be numbers.")
            if amount < 0:
                raise MetaboliteError(
                    f"Cannot produce a negative amount of {metabolite}."
                )
            if metabolite not in self.organelle.metabolites:
                raise MetaboliteError(f"Unknown metabolite: {metabolite}")
            new_quantity = self.organelle.metabolites[metabolite].quantity + amount
            if new_quantity > self.organelle.metabolites[metabolite].max_quantity:
                raise MetaboliteError(
                    f"Cannot exceed max quantity for {metabolite}. Attempted to set {metabolite} to {new_quantity}, but max is {self.organelle.metabolites[metabolite].max_quantity}."
                )

        # If all validations pass, proceed to produce
        for metabolite, amount in metabolites.items():
            self.organelle.metabolites[metabolite].quantity += amount

    def step1_hexokinase(self) -> None:
        """
        Step 1 of glycolysis: Hexokinase reaction.

        This step consumes 1 glucose and 1 ATP, and produces 1 glucose-6-phosphate and 1 ADP.

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("glucose", 1)
        self.ensure_metabolite_availability("atp", 1)
        self.consume_metabolites(glucose=1, atp=1)
        self.produce_metabolites(glucose_6_phosphate=1, adp=1)

    def step2_phosphoglucose_isomerase(self) -> None:
        """
        Step 2 of glycolysis: Phosphoglucose isomerase reaction.

        This step consumes 1 glucose-6-phosphate and produces 1 fructose-6-phosphate.

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("glucose_6_phosphate", 1)
        self.consume_metabolites(glucose_6_phosphate=1)
        self.produce_metabolites(fructose_6_phosphate=1)

    def step3_phosphofructokinase(self) -> None:
        """
        Step 3 of glycolysis: Phosphofructokinase reaction.

        This step consumes 1 ATP and produces 1 ADP.

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("fructose_6_phosphate", 1)
        self.ensure_metabolite_availability("atp", 1)
        self.consume_metabolites(fructose_6_phosphate=1, atp=1)
        self.produce_metabolites(fructose_1_6_bisphosphate=1, adp=1)

    def step4_aldolase(self) -> None:
        """
        Step 4 of glycolysis: Aldolase reaction.

        This step splits fructose-1,6-bisphosphate into
        glyceraldehyde-3-phosphate (G3P) and dihydroxyacetone phosphate (DHAP).

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("fructose_1_6_bisphosphate", 1)
        self.consume_metabolites(fructose_1_6_bisphosphate=1)
        self.produce_metabolites(
            glyceraldehyde_3_phosphate=1, dihydroxyacetone_phosphate=1
        )

    def step5_triose_phosphate_isomerase(self) -> None:
        """
        Step 5 of glycolysis: Triose phosphate isomerase reaction.

        This step converts dihydroxyacetone phosphate (DHAP) to glyceraldehyde-3-phosphate (G3P).

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("dihydroxyacetone_phosphate", 1)
        self.consume_metabolites(dihydroxyacetone_phosphate=1)
        self.produce_metabolites(glyceraldehyde_3_phosphate=1)

    def step6_glyceraldehyde_3_phosphate_dehydrogenase(self) -> None:
        """
        Step 6 of glycolysis: Glyceraldehyde-3-phosphate dehydrogenase reaction.

        This step consumes 1 glyceraldehyde-3-phosphate, 1 NAD+, and 1 Pi,
        and produces 1 1,3-bisphosphoglycerate, 1 NADH, and 1 H+.

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("glyceraldehyde_3_phosphate", 1)
        self.ensure_metabolite_availability("nad", 1)
        self.ensure_metabolite_availability("pi", 1)
        self.consume_metabolites(glyceraldehyde_3_phosphate=1, nad=1, pi=1)
        self.produce_metabolites(bisphosphoglycerate_1_3=1, nadh=1, h_plus=1)

    def step7_phosphoglycerate_kinase(self) -> None:
        """
        Step 7 of glycolysis: Phosphoglycerate kinase reaction.

        This step consumes 1 1,3-bisphosphoglycerate and 1 ADP, and produces 1 3-phosphoglycerate and 1 ATP.

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("bisphosphoglycerate_1_3", 1)
        self.ensure_metabolite_availability("adp", 1)
        self.consume_metabolites(bisphosphoglycerate_1_3=1, adp=1)
        self.produce_metabolites(phosphoglycerate_3=1, atp=1)

    def step8_phosphoglycerate_mutase(self) -> None:
        """
        Step 8 of glycolysis: Phosphoglycerate mutase reaction.

        This step consumes 1 3-phosphoglycerate and produces 1 2-phosphoglycerate.

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("phosphoglycerate_3", 1)
        self.consume_metabolites(phosphoglycerate_3=1)
        self.produce_metabolites(phosphoglycerate_2=1)

    def step9_enolase(self) -> None:
        """
        Step 9 of glycolysis: Enolase reaction.

        This step consumes 1 2-phosphoglycerate and produces 1 phosphoenolpyruvate and 1 H2O.

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("phosphoglycerate_2", 1)
        self.consume_metabolites(phosphoglycerate_2=1)
        self.produce_metabolites(phosphoenolpyruvate=1, h2o=1)

    def step10_pyruvate_kinase(self) -> None:
        """
        Step 10 of glycolysis: Pyruvate kinase reaction.

        This step consumes 1 phosphoenolpyruvate and 1 ADP, and produces 1 pyruvate and 1 ATP.

        Raises
        ------
        GlycolysisError
            If the reaction fails.
        """
        self.ensure_metabolite_availability("phosphoenolpyruvate", 1)
        self.ensure_metabolite_availability("adp", 1)
        self.consume_metabolites(phosphoenolpyruvate=1, adp=1)
        self.produce_metabolites(pyruvate=1, atp=1)
