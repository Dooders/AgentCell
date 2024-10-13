from typing import Dict

from .data import Metabolite
from .exceptions import (
    InsufficientMetaboliteError,
    QuantityError,
    UnknownMetaboliteError,
)


class OrganelleMeta(type):
    """
    Metaclass that enforces required attributes and methods,
    and automatically registers organelle classes.

    Intended to be used as a metaclass for the Organelle class.

    Parameters
    ----------
    name : str
        The name of the organelle class.
    bases : tuple
        The base classes of the organelle class.
    namespace : dict
        The namespace of the organelle class.

    Methods
    -------
    get_registry : classmethod
        Returns the registry of organelle classes.
    """

    _registry = {}  # Class variable to hold registered organelles

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        """
        Creates a new instance of the class.

        Parameters
        ----------
        name : str
            The name of the organelle class.
        bases : tuple
            The base classes of the organelle class.
        namespace : dict
            The namespace of the organelle class.
        """
        if "name" not in namespace:
            raise AttributeError(
                f"Class '{name}' must define a 'name' class attribute."
            )

        # if "function" not in namespace or not callable(namespace["function"]):
        #     raise NotImplementedError(f"Class '{name}' must implement a 'function' method.")

        cls = super().__new__(mcs, name, bases, namespace)

        # Automatic attribute initialization
        if "structure" not in namespace:
            setattr(cls, "structure", "Unknown")

        # Register the class (excluding the base Organelle class)
        if name != "Organelle":
            mcs._registry[name] = cls

        return cls

    @classmethod
    def get_registry(mcs: type) -> dict:
        """
        Returns the registry of organelle classes.

        Returns
        -------
        dict
            The registry of organelle classes.
        """
        return dict(mcs._registry)


class Organelle(metaclass=OrganelleMeta):
    """
    Base class for organelles, using OrganelleMeta as the metaclass.

    An organelle is a cellular compartment that contains metabolites and enzymes.

    Attributes
    ----------
    name : str
        The name of the organelle.
    metabolites : dict
        A dictionary of metabolites in the organelle.

    Methods
    -------
    add_metabolite(self, name: str, quantity: int, max_quantity: int) -> None:
        Adds a metabolite to the organelle.
    change_metabolite_quantity(self, metabolite_name: str, amount: float) -> None:
        Changes the quantity of a metabolite in the organelle.
    is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        Checks if a metabolite is available in the organelle.
    consume_metabolites(self, **metabolites: Dict[str, float]) -> bool:
        Consumes metabolites from the organelle.
    produce_metabolites(self, **metabolites: float) -> bool:
        Produces metabolites in the organelle.
    """

    name = "Organelle"

    def __init__(self):
        self.metabolites: Dict[str, Metabolite] = {}
        self.add_metabolite("glucose", 0, 1000)
        self.add_metabolite("atp", 100, 1000)
        self.add_metabolite("adp", 0, 1000)
        self.add_metabolite("nad", 10, 1000)
        self.add_metabolite("nadh", 0, 1000)
        self.add_metabolite("pyruvate", 0, 1000)
        self.glycolysis_rate = 1.0

    def add_metabolite(self, name: str, quantity: int, max_quantity: int) -> None:
        """
        Adds a metabolite to the organelle.

        Parameters
        ----------
        name : str
            The name of the metabolite.
        quantity : int
            The initial quantity of the metabolite.
        max_quantity : int
            The maximum quantity of the metabolite.
        """
        # Add type checking for parameters
        if not isinstance(name, str):
            raise TypeError("Metabolite name must be a string.")
        if not isinstance(quantity, int) or not isinstance(max_quantity, int):
            raise TypeError("Quantity and max_quantity must be integers.")
        if quantity < 0 or max_quantity < 0:
            raise ValueError("Quantity and max_quantity must be non-negative.")
        if quantity > max_quantity:
            raise ValueError("Quantity cannot exceed max_quantity.")

        self.metabolites[name] = Metabolite(name, quantity, max_quantity)

    def change_metabolite_quantity(self, metabolite_name: str, amount: float) -> None:
        """
        Changes the quantity of a metabolite in the organelle.

        Parameters
        ----------
        metabolite_name : str
            The name of the metabolite.
        amount : float
            The amount to change the quantity by.
        """
        if not isinstance(metabolite_name, str):
            raise TypeError("Metabolite name must be a string.")
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")
        if metabolite_name not in self.metabolites:
            raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite_name}")

        metabolite = self.metabolites[metabolite_name]
        new_quantity = metabolite.quantity + amount

        if new_quantity < 0:
            raise QuantityError(
                f"Cannot reduce {metabolite_name} below zero. Attempted to set {metabolite_name} to {new_quantity}."
            )
        if new_quantity > metabolite.max_quantity:
            raise QuantityError(
                f"Cannot exceed max quantity for {metabolite_name}. Attempted to set {metabolite_name} to {new_quantity}, but max is {metabolite.max_quantity}."
            )

        metabolite.quantity = new_quantity

    def is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        """
        Checks if a metabolite is available in the organelle.

        Parameters
        ----------
        metabolite : str
            The name of the metabolite.
        amount : float
            The amount of the metabolite to check for.

        Returns
        -------
        bool
            True if the metabolite is available, False otherwise.
        """
        if metabolite not in self.metabolites:
            raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite}")
        return self.metabolites[metabolite].quantity >= amount

    def consume_metabolites(self, **metabolites: Dict[str, float]) -> bool:
        for metabolite, amount in metabolites.items():
            if metabolite not in self.metabolites:
                raise ValueError(f"Unknown metabolite: {metabolite}")
            if self.metabolites[metabolite].quantity < amount:
                if metabolite == "h2o":
                    # Water is abundant, so we'll assume it's always available
                    continue
                raise ValueError(f"Insufficient {metabolite} for reaction.")

        # If all validations pass, proceed to consume
        for metabolite, amount in metabolites.items():
            if metabolite != "h2o":  # We don't track water consumption
                self.metabolites[metabolite].quantity -= amount
        return True

    def produce_metabolites(self, **metabolites: float) -> bool:
        """
        Produces metabolites in the organelle.

        Parameters
        ----------
        metabolites : dict
            The metabolites to produce.

        Returns
        -------
        bool
            True if the metabolites were produced, False otherwise.
        """
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise TypeError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise TypeError("Amounts must be numbers.")
            if amount < 0:
                raise QuantityError(
                    f"Cannot produce a negative amount of {metabolite}."
                )
            if metabolite not in self.metabolites:
                raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite}")
            new_quantity = self.metabolites[metabolite].quantity + amount
            if new_quantity > self.metabolites[metabolite].max_quantity:
                raise QuantityError(
                    f"Cannot exceed max quantity for {metabolite}. Attempted to set {metabolite} to {new_quantity}, but max is {self.metabolites[metabolite].max_quantity}."
                )

        # If all validations pass, proceed to produce
        for metabolite, amount in metabolites.items():
            self.metabolites[metabolite].quantity += amount
        return True
