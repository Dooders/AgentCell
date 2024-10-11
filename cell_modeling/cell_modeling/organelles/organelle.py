"""
Benefits of Using an Organelle Metaclass
    Consistency: 
        Ensures all organelle classes have required attributes and methods.
    Automatic Registration: 
        Keeps track of all organelle classes for easy management.
    Shared Functionality: 
        Can inject common methods or properties, reducing code duplication.
    Error Prevention: 
        Catches errors during class creation rather than at runtime.
"""


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

        if "function" not in namespace or not callable(namespace["function"]):
            raise TypeError(f"Class '{name}' must implement a 'function' method.")

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


# organelle.py


class Organelle(metaclass=OrganelleMeta):
    """
    Base class for organelles, using OrganelleMeta as the metaclass.
    """

    name = "Organelle"  # This satisfies the 'name' attribute requirement

    def function(self):
        """
        Placeholder method to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the 'function' method.")
