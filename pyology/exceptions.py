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


class PathwayError(Exception):
    """Base class for errors in metabolic pathways."""

    pass


class GlycolysisError(PathwayError):
    """Exception raised for errors in the glycolysis pathway."""

    pass


class KrebsCycleError(PathwayError):
    """Exception raised for errors in the Krebs Cycle pathway."""

    pass


class ReactionError(Exception):
    """Exception raised for errors in biochemical reactions."""

    pass


class InsufficientSubstrateError(ReactionError):
    """Exception raised when there is insufficient substrate for a reaction."""

    pass


class OrganelleError(PyologyError):
    """Exception raised for errors during organelle operations."""

    pass


class GlycolysisRateError(OrganelleError):
    """Exception raised when a glycolysis rate is invalid."""

    pass


class MetaboliteNotFoundError(OrganelleError):
    """Exception raised when a metabolite is not found in the organelle."""

    pass
