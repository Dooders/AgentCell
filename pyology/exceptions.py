class PyologyError(Exception):
    """Base exception class for Pyology errors."""
    pass

class MetaboliteError(PyologyError):
    """Exception raised for errors related to metabolites."""
    pass

class QuantityError(MetaboliteError):
    """Exception raised when a metabolite quantity is invalid."""
    pass

class UnknownMetaboliteError(MetaboliteError):
    """Exception raised when an unknown metabolite is referenced."""
    pass

class InsufficientMetaboliteError(MetaboliteError):
    """Exception raised when there's not enough of a metabolite for a reaction."""
    pass

class GlycolysisError(PyologyError):
    """Exception raised for errors during glycolysis."""
    pass

class ReactionError(PyologyError):
    """Exception raised when a reaction fails to execute."""
    pass
