class MetaboliteError(Exception):
    """Base class for exceptions related to metabolites."""

    pass


class UnknownMetaboliteError(MetaboliteError):
    """Raised when a metabolite is unknown."""

    pass


class InsufficientMetaboliteError(MetaboliteError):
    """Raised when there is not enough metabolite for a reaction."""

    pass


class QuantityError(MetaboliteError):
    """Raised when an invalid quantity is specified."""

    pass


class GlycolysisError(Exception):
    pass
