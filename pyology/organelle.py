import json
import os
from dataclasses import dataclass, field
from typing import List

import yaml

from .exceptions import (
    GlycolysisRateError,
    InsufficientMetaboliteError,
    QuantityError,
    UnknownMetaboliteError,
)
from .metabolite import Metabolite, Metabolites


@dataclass
class CellMetabolites:
    """
    A data class that initializes a Metabolites instance with basic cell metabolites.

    Attributes
    ----------
    metabolites : Metabolites
        An instance of the Metabolites class containing all basic metabolites.
    """

    metabolites: Metabolites = field(default_factory=Metabolites)

    def __post_init__(self):
        """
        Post-initialization to add basic metabolites to the Metabolites instance.
        """
        # Load metabolites from JSON file
        json_path = os.path.join(os.path.dirname(__file__), "basic_metabolites.json")
        with open(json_path, "r", encoding="utf-8") as f:
            basic_metabolites = json.load(f)

        # Add each metabolite to the Metabolites instance
        for metabolite_info in basic_metabolites:
            self.metabolites.register(
                name=metabolite_info["name"],
                quantity=metabolite_info["quantity"],
                max_quantity=metabolite_info["max_quantity"],
                type=metabolite_info["type"],
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

    def __new__(cls, name: str, bases: tuple, namespace: dict) -> type:
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

        Returns
        -------
        type
            The new instance of the class.
        """
        new_class = super().__new__(cls, name, bases, namespace)
        cls._registry[new_class.name] = new_class
        return new_class

    @classmethod
    def get_registry(cls: type) -> dict:
        """
        Returns the registry of organelle classes.

        Returns
        -------
        dict
            The registry of organelle classes.
        """
        return dict(cls._registry)


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
    validate_initial_state(self) -> None:
        Validates the initial state of the organelle, including metabolite quantities and rates.
    add_metabolite(self, name: str, type: str, quantity: float, max_quantity: float) -> None:
        Adds a metabolite to the organelle or increases its quantity if it already exists.
    change_metabolite_quantity(self, metabolite_name: str, amount: float) -> None:
        Changes the quantity of a metabolite in the organelle.
    is_metabolite_available(self, metabolite: str, amount: float) -> bool:
        Checks if a metabolite is available in the organelle.
    consume_metabolites(self, **metabolites: float) -> None:
        Consumes metabolites from the organelle.
    produce_metabolites(self, **metabolites: float) -> None:
        Produces metabolites in the organelle.
    """

    name = "Organelle"

    def __init__(self, metabolites_list: List[str] = None, logger=None, debug=False):
        self.metabolites = Metabolites.from_list(metabolites_list)
        self._glycolysis_rate = 1.0
        self.validate_initial_state()

    @property
    def glycolysis_rate(self):
        return self._glycolysis_rate

    @glycolysis_rate.setter
    def glycolysis_rate(self, value):
        if value <= 0:
            raise GlycolysisRateError(f"Invalid glycolysis rate: {value}")
        self._glycolysis_rate = value

    def validate_initial_state(self) -> None:
        """
        Validates the initial state of the organelle, including metabolite
        quantities and rates.

        Raises
        ------
        QuantityError
            If the initial quantity of a metabolite is invalid.
        GlycolysisRateError
            If the glycolysis rate is invalid.
        """
        for name, metabolite in self.metabolites.items():
            if metabolite.quantity < 0 or metabolite.quantity > metabolite.max_quantity:
                raise QuantityError(
                    f"Invalid initial quantity for {name}: {metabolite.quantity}"
                )

        if self.glycolysis_rate <= 0:
            raise GlycolysisRateError(
                f"Invalid glycolysis rate: {self.glycolysis_rate}"
            )

    def add_metabolite(
        self, name: str, type: str, quantity: float, max_quantity: float
    ) -> None:
        """
        Add a metabolite to the organelle or increase its quantity if it already exists.

        Parameters
        ----------
        name : str
            The name of the metabolite.
        type : str
            The type of the metabolite.
        quantity : float
            The quantity of the metabolite.
        max_quantity : float
            The maximum quantity of the metabolite.

        Raises
        ------
        QuantityError
            If the quantity is negative or exceeds the maximum quantity.
        """
        if quantity < 0:
            raise QuantityError(f"Quantity must be non-negative. Got: {quantity}")

        if quantity > max_quantity:
            raise QuantityError(
                f"Initial quantity {quantity} exceeds max quantity {max_quantity}."
            )

        if name in self.metabolites:
            new_quantity = min(self.metabolites[name].quantity + quantity, max_quantity)
            self.metabolites[name].quantity = new_quantity
        else:
            metabolite = Metabolite(name, quantity, max_quantity)
            metabolite.type = type  # Set the type after creation
            self.metabolites[name] = metabolite

    def change_metabolite_quantity(self, metabolite_name: str, amount: float) -> None:
        """
        Changes the quantity of a metabolite in the organelle.

        Parameters
        ----------
        metabolite_name : str
            The name of the metabolite.
        amount : float
            The amount to change the quantity by.

        Raises
        ------
        MetaboliteError
            If the metabolite name is not a string or the amount is not a number.
        UnknownMetaboliteError
            If the metabolite is not found in the organelle.
        """
        if not isinstance(metabolite_name, str):
            raise MetaboliteError("Metabolite name must be a string.")
        if not isinstance(amount, (int, float)):
            raise MetaboliteError("Amount must be a number.")
        if metabolite_name not in self.metabolites:
            raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite_name}")

        metabolite = self.metabolites[metabolite_name]
        new_quantity = metabolite.quantity + amount

        if new_quantity < 0:
            raise QuantityError(
                f"Cannot reduce {metabolite_name} below zero. Current: {metabolite.quantity}, Attempted change: {amount}"
            )
        if new_quantity > metabolite.max_quantity:
            raise QuantityError(
                f"Cannot exceed max quantity for {metabolite_name}. Current: {metabolite.quantity}, Max: {metabolite.max_quantity}, Attempted change: {amount}"
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

        Raises
        ------
        UnknownMetaboliteError
            If the metabolite is not found in the organelle.
        """
        if metabolite not in self.metabolites:
            raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite}")
        return self.metabolites[metabolite].quantity >= amount

    def consume_metabolites(self, **metabolites: float) -> None:
        """
        Consumes metabolites from the organelle.

        Parameters
        ----------
        metabolites : dict
            A dictionary of metabolites to consume.
        """
        for metabolite, amount in metabolites.items():
            if not self.is_metabolite_available(metabolite, amount):
                raise InsufficientMetaboliteError(
                    f"Insufficient {metabolite} for reaction. Required: {amount}, Available: {self.metabolites[metabolite].quantity}"
                )
            self.change_metabolite_quantity(metabolite, -amount)

    def produce_metabolites(self, **metabolites: float) -> None:
        """
        Produces metabolites in the organelle.

        Parameters
        ----------
        metabolites : dict
            A dictionary of metabolites to produce.
        """
        for metabolite, amount in metabolites.items():
            self.change_metabolite_quantity(metabolite, amount)

    def get_metabolite_quantity(self, metabolite: str) -> float:
        """
        Returns the quantity of a metabolite in the organelle.

        Parameters
        ----------
        metabolite : str
            The name of the metabolite.

        Returns
        -------
        float
            The quantity of the metabolite.
        """
        if metabolite not in self.metabolites:
            raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite}")
        return self.metabolites[metabolite].quantity

    def set_metabolite_quantity(self, metabolite: str, quantity: float) -> None:
        """
        Sets the quantity of a metabolite in the organelle.

        Parameters
        ----------
        metabolite : str
            The name of the metabolite.
        quantity : float
            The quantity of the metabolite.
        """
        if metabolite not in self.metabolites:
            raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite}")
        self.metabolites[metabolite].quantity = quantity

    def get_metabolite(self, metabolite_name: str) -> Metabolite:
        """
        Get a metabolite from the cytoplasm.

        Parameters
        ----------
        metabolite_name : str
            The name of the metabolite to retrieve.

        Returns
        -------
        Metabolite
            The requested metabolite object.

        Raises
        ------
        UnknownMetaboliteError
            If the metabolite is not found in the organelle.
        """
        if metabolite_name not in self.metabolites:
            raise UnknownMetaboliteError(f"Unknown metabolite: {metabolite_name}")
        return self.metabolites[metabolite_name]
