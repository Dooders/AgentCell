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
        """
        if "name" not in namespace:
            raise TypeError(f"Class '{name}' must define a 'name' class attribute.")

        # if "function" not in namespace or not callable(namespace["function"]):
        #     raise TypeError(f"Class '{name}' must implement a 'function' method.")

        # Inject a common method if not defined
        if "common_process" not in namespace:

            def common_process(self):
                print(f"{self.name} performing a common process.")

            namespace["common_process"] = common_process

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
        """
        return dict(mcs._registry)


class Organelle(metaclass=OrganelleMeta):
    """
    Base class for organelles, using OrganelleMeta as the metaclass.
    """

    name = "Organelle"

    def __init__(self):
        self.metabolites: Dict[str, Metabolite] = {}
        self.add_metabolite("glucose", 0, 1000)
        self.add_metabolite("atp", 100, 1000)  # Start with some ATP
        self.add_metabolite("adp", 0, 1000)
        self.add_metabolite("nad", 10, 1000)
        self.add_metabolite("nadh", 0, 1000)
        self.add_metabolite("pyruvate", 0, 1000)
        self.glycolysis_rate = 1.0

    def add_metabolite(self, name: str, quantity: int, max_quantity: int):
        self.metabolites[name] = Metabolite(name, quantity, max_quantity)

    def change_metabolite_quantity(self, metabolite_name: str, amount: float):
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
        if metabolite not in self.metabolites:
            raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite}")
        return self.metabolites[metabolite].quantity >= amount

    def consume_metabolites(self, **metabolites: Dict[str, float]):
        for metabolite, amount in metabolites.items():
            if not isinstance(metabolite, str):
                raise TypeError("Metabolite names must be strings.")
            if not isinstance(amount, (int, float)):
                raise TypeError("Amounts must be numbers.")
            if amount < 0:
                raise QuantityError(
                    f"Cannot consume a negative amount of {metabolite}."
                )
            if metabolite not in self.metabolites:
                raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite}")
            if self.metabolites[metabolite].quantity < amount:
                raise InsufficientMetaboliteError(
                    f"Insufficient {metabolite} for reaction."
                )

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

    def function(self):
        raise NotImplementedError("Subclasses must implement the 'function' method")
