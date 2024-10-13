class MetaboliteError(Exception):
    """Base class for exceptions in this module."""

    pass


class UnknownMetaboliteError(MetaboliteError):
    """Exception raised when trying to access an unknown metabolite."""

    pass


class InsufficientMetaboliteError(MetaboliteError):
    """Exception raised when there is insufficient quantity of a metabolite for a reaction."""

    pass


class QuantityError(MetaboliteError):
    """Exception raised for errors in the quantity of metabolites."""

    pass


class GlycolysisError(Exception):
    pass
