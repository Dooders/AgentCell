import math
from typing import Dict

from .enzymes import Enzyme
from .exceptions import GlycolysisError, MetaboliteError
from .mitochondrion import GlycolysisSteps


class GlycolysisPathway:
    """
    Class representing the glycolysis pathway.
    """

    def __init__(self, organelle):
        self.organelle = organelle
        self.define_enzymes()
        self.time_step = 0.1  # Default time step in seconds

    def define_enzymes(self):
        """Define enzymes for each step of glycolysis."""
        self.enzymes = {
            "hexokinase": Enzyme(
                "Hexokinase", vmax=10.0, km=0.1, inhibitors={"glucose_6_phosphate": 0.5}
            ),
            "phosphoglucose_isomerase": Enzyme(
                "Phosphoglucose Isomerase", vmax=12.0, km=0.2
            ),
            "phosphofructokinase": Enzyme(
                "Phosphofructokinase",
                vmax=8.0,
                km=0.15,
                inhibitors={"atp": 1.0},
                activators={"adp": 0.5, "amp": 0.1},
            ),
            "aldolase": Enzyme("Aldolase", vmax=7.0, km=0.3),
            "triose_phosphate_isomerase": Enzyme(
                "Triose Phosphate Isomerase", vmax=15.0, km=0.1
            ),
            "glyceraldehyde_3_phosphate_dehydrogenase": Enzyme(
                "Glyceraldehyde 3-Phosphate Dehydrogenase",
                vmax=6.0,
                km=0.25,
                inhibitors={"nadh": 0.5},
            ),
            "phosphoglycerate_kinase": Enzyme(
                "Phosphoglycerate Kinase", vmax=9.0, km=0.2
            ),
            "phosphoglycerate_mutase": Enzyme(
                "Phosphoglycerate Mutase", vmax=11.0, km=0.15
            ),
            "enolase": Enzyme("Enolase", vmax=7.5, km=0.3),
            "pyruvate_kinase": Enzyme(
                "Pyruvate Kinase",
                vmax=10.0,
                km=0.2,
                inhibitors={"atp": 0.8},
                activators={"fructose_1_6_bisphosphate": 0.3},
            ),
        }

    def calculate_reaction_rate(self, enzyme_name: str, substrate_conc: float) -> float:
        """Calculate the reaction rate based on enzyme kinetics and regulation."""
        enzyme = self.enzymes[enzyme_name]
        metabolite_levels = {
            metabolite: self.organelle.get_metabolite_quantity(metabolite)
            for metabolite in self.organelle.metabolites
        }
        return enzyme.calculate_rate(substrate_conc, metabolite_levels) * self.time_step

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

        This step consumes glucose and ATP, and produces glucose-6-phosphate and ADP.
        """
        substrate_conc = self.organelle.get_metabolite_quantity("glucose")
        reaction_rate = self.calculate_reaction_rate("hexokinase", substrate_conc)

        actual_rate = min(
            reaction_rate, substrate_conc, self.organelle.get_metabolite_quantity("atp")
        )

        self.consume_metabolites(glucose=actual_rate, atp=actual_rate)
        self.produce_metabolites(glucose_6_phosphate=actual_rate, adp=actual_rate)

    def step2_phosphoglucose_isomerase(self) -> None:
        """
        Step 2 of glycolysis: Phosphoglucose isomerase reaction.

        This step consumes glucose-6-phosphate and produces fructose-6-phosphate.
        """
        substrate_conc = self.organelle.get_metabolite_quantity("glucose_6_phosphate")
        reaction_rate = self.calculate_reaction_rate(
            "phosphoglucose_isomerase", substrate_conc
        )

        actual_rate = min(reaction_rate, substrate_conc)

        self.consume_metabolites(glucose_6_phosphate=actual_rate)
        self.produce_metabolites(fructose_6_phosphate=actual_rate)

    def step3_phosphofructokinase(self) -> None:
        """
        Step 3 of glycolysis: Phosphofructokinase reaction.

        This step consumes fructose-6-phosphate and ATP, and produces fructose-1,6-bisphosphate and ADP.
        """
        substrate_conc = self.organelle.get_metabolite_quantity("fructose_6_phosphate")
        reaction_rate = self.calculate_reaction_rate(
            "phosphofructokinase", substrate_conc
        )

        actual_rate = min(
            reaction_rate, substrate_conc, self.organelle.get_metabolite_quantity("atp")
        )

        self.consume_metabolites(fructose_6_phosphate=actual_rate, atp=actual_rate)
        self.produce_metabolites(fructose_1_6_bisphosphate=actual_rate, adp=actual_rate)

    def step4_aldolase(self) -> None:
        """
        Step 4 of glycolysis: Aldolase reaction.

        This step splits fructose-1,6-bisphosphate into
        glyceraldehyde-3-phosphate (G3P) and dihydroxyacetone phosphate (DHAP).
        """
        substrate_conc = self.organelle.get_metabolite_quantity(
            "fructose_1_6_bisphosphate"
        )
        reaction_rate = self.calculate_reaction_rate("aldolase", substrate_conc)

        actual_rate = min(reaction_rate, substrate_conc)

        self.consume_metabolites(fructose_1_6_bisphosphate=actual_rate)
        self.produce_metabolites(
            glyceraldehyde_3_phosphate=actual_rate,
            dihydroxyacetone_phosphate=actual_rate,
        )

    def step5_triose_phosphate_isomerase(self) -> None:
        """
        Step 5 of glycolysis: Triose phosphate isomerase reaction.

        This step converts dihydroxyacetone phosphate (DHAP) to glyceraldehyde-3-phosphate (G3P).
        """
        substrate_conc = self.organelle.get_metabolite_quantity(
            "dihydroxyacetone_phosphate"
        )
        reaction_rate = self.calculate_reaction_rate(
            "triose_phosphate_isomerase", substrate_conc
        )

        actual_rate = min(reaction_rate, substrate_conc)

        self.consume_metabolites(dihydroxyacetone_phosphate=actual_rate)
        self.produce_metabolites(glyceraldehyde_3_phosphate=actual_rate)

    def step6_glyceraldehyde_3_phosphate_dehydrogenase(self) -> None:
        """
        Step 6 of glycolysis: Glyceraldehyde-3-phosphate dehydrogenase reaction.

        This step consumes glyceraldehyde-3-phosphate, NAD+, and Pi,
        and produces 1,3-bisphosphoglycerate, NADH, and H+.
        """
        substrate_conc = self.organelle.get_metabolite_quantity(
            "glyceraldehyde_3_phosphate"
        )
        reaction_rate = self.calculate_reaction_rate(
            "glyceraldehyde_3_phosphate_dehydrogenase", substrate_conc
        )

        actual_rate = min(
            reaction_rate,
            substrate_conc,
            self.organelle.get_metabolite_quantity("nad"),
            self.organelle.get_metabolite_quantity("pi"),
        )

        self.consume_metabolites(
            glyceraldehyde_3_phosphate=actual_rate, nad=actual_rate, pi=actual_rate
        )
        self.produce_metabolites(
            bisphosphoglycerate_1_3=actual_rate, nadh=actual_rate, h_plus=actual_rate
        )

    def step7_phosphoglycerate_kinase(self) -> None:
        """
        Step 7 of glycolysis: Phosphoglycerate kinase reaction.

        This step consumes 1,3-bisphosphoglycerate and ADP, and produces 3-phosphoglycerate and ATP.
        """
        substrate_conc = self.organelle.get_metabolite_quantity(
            "bisphosphoglycerate_1_3"
        )
        reaction_rate = self.calculate_reaction_rate(
            "phosphoglycerate_kinase", substrate_conc
        )

        actual_rate = min(
            reaction_rate, substrate_conc, self.organelle.get_metabolite_quantity("adp")
        )

        self.consume_metabolites(bisphosphoglycerate_1_3=actual_rate, adp=actual_rate)
        self.produce_metabolites(phosphoglycerate_3=actual_rate, atp=actual_rate)

    def step8_phosphoglycerate_mutase(self) -> None:
        """
        Step 8 of glycolysis: Phosphoglycerate mutase reaction.

        This step consumes 3-phosphoglycerate and produces 2-phosphoglycerate.
        """
        substrate_conc = self.organelle.get_metabolite_quantity("phosphoglycerate_3")
        reaction_rate = self.calculate_reaction_rate(
            "phosphoglycerate_mutase", substrate_conc
        )

        actual_rate = min(reaction_rate, substrate_conc)

        self.consume_metabolites(phosphoglycerate_3=actual_rate)
        self.produce_metabolites(phosphoglycerate_2=actual_rate)

    def step9_enolase(self) -> None:
        """
        Step 9 of glycolysis: Enolase reaction.

        This step consumes 2-phosphoglycerate and produces phosphoenolpyruvate and H2O.
        """
        substrate_conc = self.organelle.get_metabolite_quantity("phosphoglycerate_2")
        reaction_rate = self.calculate_reaction_rate("enolase", substrate_conc)

        actual_rate = min(reaction_rate, substrate_conc)

        self.consume_metabolites(phosphoglycerate_2=actual_rate)
        self.produce_metabolites(phosphoenolpyruvate=actual_rate, h2o=actual_rate)

    def step10_pyruvate_kinase(self) -> None:
        """
        Step 10 of glycolysis: Pyruvate kinase reaction.

        This step consumes phosphoenolpyruvate and ADP, and produces pyruvate and ATP.
        """
        substrate_conc = self.organelle.get_metabolite_quantity("phosphoenolpyruvate")
        reaction_rate = self.calculate_reaction_rate("pyruvate_kinase", substrate_conc)

        actual_rate = min(
            reaction_rate, substrate_conc, self.organelle.get_metabolite_quantity("adp")
        )

        self.consume_metabolites(phosphoenolpyruvate=actual_rate, adp=actual_rate)
        self.produce_metabolites(pyruvate=actual_rate, atp=actual_rate)
