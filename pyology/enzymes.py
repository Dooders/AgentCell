"""
This module provides the Enzyme class for modeling enzyme kinetics in biochemical reactions.

The Enzyme class supports advanced features such as:
- Multiple substrates and products
- Cooperative binding (Hill equation)
- Various inhibition types (competitive, non-competitive, uncompetitive)
- Enzyme activation and regulation

Example usage:
--------------
from pyology.enzymes import Enzyme
from pyology.metabolite import Metabolite

# Create an enzyme instance
complex_enzyme = Enzyme(
    name="Complex Enzyme",
    k_cat=100,
    k_m={"substrate1": 10, "substrate2": 5},
    inhibitors={
        "inhibitor1": {"type": "competitive", "ki": 1},
        "inhibitor2": {"type": "noncompetitive", "ki": 2},
    },
    activators={"activator1": 0.5},
    hill_coefficients={"substrate1": 2, "substrate2": 1},
)

# Create metabolites
metabolites = {
    "substrate1": Metabolite(name="substrate1", quantity=20),
    "substrate2": Metabolite(name="substrate2", quantity=15),
    "inhibitor1": Metabolite(name="inhibitor1", quantity=0.5),
    "activator1": Metabolite(name="activator1", quantity=1),
    "product1": Metabolite(name="product1", quantity=0),
}

# Calculate reaction rate
rate = complex_enzyme.calculate_rate(metabolites)
print(f"Reaction rate: {rate}")

# Simulate catalysis
time_step = 0.1
complex_enzyme.catalyze(metabolites, time_step)

# Check updated metabolite quantities
for name, metabolite in metabolites.items():
    print(f"{name}: {metabolite.quantity}")

# Regulate downstream enzymes
downstream_enzyme = Enzyme(name="Downstream Enzyme", k_cat=50, k_m={"product1": 2})
complex_enzyme.downstream_enzymes.append(downstream_enzyme)
complex_enzyme.regulate_enzyme(downstream_enzyme, "activate")
"""

from typing import Dict, List

from .metabolite import Metabolite


class Enzyme:
    """
    Represents an enzyme that catalyzes a biochemical reaction.

    Parameters
    ----------
    name : str
        The name of the enzyme.
    k_cat : float
        The catalytic constant (turnover number) of the enzyme.
    k_m : Dict[str, float]
        The Michaelis constants for multiple substrates. 
        For example, {"glucose": 10}
    inhibitors : Dict[str, Dict[str, float]], optional
        The inhibition constants for multiple substrates. Defaults to None.
    activators : Dict[str, float], optional
        The activation constants for multiple substrates. Defaults to None.
    active : bool, optional
        Whether the enzyme is active. Defaults to True.
    downstream_enzymes : List[Enzyme], optional
        The enzymes that are downstream of this enzyme. Defaults to None.
    hill_coefficients : Dict[str, float], optional
        The Hill coefficients for multiple substrates. Defaults to None.

    Methods
    -------
    calculate_rate : function
        Calculates the rate of the enzyme's reaction.
    activate : function
        Activates the enzyme and its downstream enzymes.
    deactivate : function
        Deactivates the enzyme.
    regulate_enzyme : function
        Regulates another enzyme by activating or deactivating it.
    catalyze : function
        Simulates the catalysis over a time step dt, handling multiple
        substrates and products.
    """

    def __init__(
        self,
        name: str,
        k_cat: float,
        k_m: Dict[str, float],
        inhibitors: Dict[str, Dict[str, float]] = None,
        activators: Dict[str, float] = None,
        active: bool = True,
        downstream_enzymes: List["Enzyme"] = None,
        hill_coefficients: Dict[str, float] = None,
    ):
        self.name = name
        self.k_cat = k_cat
        self.k_m = k_m
        self.inhibitors = inhibitors or {}
        self.activators = activators or {}
        self.active = active
        self.downstream_enzymes = downstream_enzymes or []
        self.hill_coefficients = hill_coefficients or {}

    def calculate_rate(self, metabolites: Dict[str, Metabolite]) -> float:
        """
        Calculates the rate of the enzyme's reaction, including advanced kinetics.

        Parameters
        ----------
        metabolites : Dict[str, Metabolite]
            The metabolites in the cell.

        Returns
        -------
        float
            The rate of the enzyme's reaction.
        """
        if not self.active:
            return 0.0

        rate = self.k_cat
        rate *= self._calculate_kinetics(metabolites)
        rate *= self._calculate_inhibition_effects(metabolites)
        rate *= self._calculate_activation_effects(metabolites)

        return rate

    def _calculate_kinetics(self, metabolites: Dict[str, Metabolite]) -> float:
        """
        Calculates the Michaelis-Menten kinetics with cooperative binding (Hill equation).

        Parameters
        ----------
        metabolites : Dict[str, Metabolite]
            The metabolites in the cell.

        Returns
        -------
        float
            The kinetics factor for the rate calculation.
        """
        kinetics_factor = 1.0
        for substrate, k_m in self.k_m.items():
            metabolite = metabolites.get(substrate)
            if metabolite is None:
                return 0.0  # If a required substrate is missing, rate is 0
            conc = metabolite.quantity
            n = self.hill_coefficients.get(
                substrate, 1
            )  # Default to 1 if not specified
            kinetics_factor *= conc**n / (k_m**n + conc**n)
        return kinetics_factor

    def _calculate_inhibition_effects(
        self, metabolites: Dict[str, Metabolite]
    ) -> float:
        """
        Calculates the inhibition effects on the enzyme's reaction rate.

        Parameters
        ----------
        metabolites : Dict[str, Metabolite]
            The metabolites in the cell.

        Returns
        -------
        float
            The inhibition factor for the rate calculation.
        """
        inhibition_factor = 1.0
        for inhibitor, inhibitor_info in self.inhibitors.items():
            metabolite = metabolites.get(inhibitor)
            if metabolite:
                conc = metabolite.quantity
                inhibition_type = inhibitor_info.get("type", "competitive")
                ki = inhibitor_info["ki"]

                # Use the first substrate in k_m for inhibition calculations
                substrate = next(iter(self.k_m))
                k_m = self.k_m[substrate]

                if inhibition_type == "competitive":
                    inhibition_factor *= k_m / (
                        k_m + metabolites[substrate].quantity * (1 + conc / ki)
                    )
                elif inhibition_type == "noncompetitive":
                    inhibition_factor *= 1 / (1 + conc / ki)
                elif inhibition_type == "uncompetitive":
                    inhibition_factor *= 1 / (
                        1 + k_m / (ki * (k_m + metabolites[substrate].quantity))
                    )
        return inhibition_factor

    def _calculate_activation_effects(
        self, metabolites: Dict[str, Metabolite]
    ) -> float:
        """
        Calculates the activation effects on the enzyme's reaction rate.

        Parameters
        ----------
        metabolites : Dict[str, Metabolite]
            The metabolites in the cell.

        Returns
        -------
        float
            The activation factor for the rate calculation.
        """
        activation_factor = 1.0
        for substrate, activator_constant in self.activators.items():
            metabolite = metabolites.get(substrate)
            if metabolite:
                conc = metabolite.quantity
                activation_factor *= 1 + conc / activator_constant
        return activation_factor

    def activate(self) -> None:
        """
        Activates the enzyme and its downstream enzymes.
        """
        self.active = True
        for enzyme in self.downstream_enzymes:
            enzyme.activate()

    def deactivate(self) -> None:
        """
        Deactivates the enzyme.
        """
        self.active = False

    def regulate_enzyme(self, target_enzyme: "Enzyme", action: str) -> None:
        """
        Regulates another enzyme by activating or deactivating it.

        Parameters
        ----------
        target_enzyme : Enzyme
            The enzyme to be regulated.
        action : str
            The action to perform on the target enzyme ('activate' or 'deactivate').

        Raises
        ------
        ValueError
            If an invalid action is provided.
        """
        if action == "activate":
            target_enzyme.activate()
        elif action == "deactivate":
            target_enzyme.deactivate()
        else:
            raise ValueError("Invalid action. Use 'activate' or 'deactivate'.")

    def catalyze(self, metabolites: Dict[str, Metabolite], dt: float):
        """
        Simulates the catalysis over a time step dt, handling multiple substrates and products.

        Parameters
        ----------
        metabolites : Dict[str, Metabolite]
            The metabolites involved in the reaction.
        dt : float
            The time step for the simulation.
        """
        rate = self.calculate_rate(metabolites)
        if rate == 0.0:
            return  # No reaction occurs

        # Define the reaction stoichiometry
        stoichiometry = {
            substrate: -1 for substrate in self.k_m.keys()  # All substrates
        }
        stoichiometry.update(
            {
                f"product{i+1}": 1
                for i in range(
                    len(self.k_m)
                )  # Assuming equal number of products as substrates
            }
        )

        # Calculate the change in metabolite quantities
        delta = rate * dt
        for metabolite_name, coefficient in stoichiometry.items():
            metabolite = metabolites.get(metabolite_name)
            if metabolite is None:
                if coefficient > 0:
                    # Create new product if it doesn't exist
                    metabolites[metabolite_name] = Metabolite(
                        name=metabolite_name,
                        quantity=coefficient * delta,
                        max_quantity=100.0,
                    )
                else:
                    # If a required substrate is missing, stop the reaction
                    return
            else:
                # Update existing metabolite quantity
                new_quantity = metabolite.quantity + coefficient * delta
                metabolite.quantity = max(new_quantity, 0.0)

        # Trigger downstream enzymes in the cascade***
        for enzyme in self.downstream_enzymes:
            self.regulate_enzyme(enzyme, "activate")
