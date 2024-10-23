from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from pyology.organelle import Organelle
from pyology.reporter import Reporter

from .command_data import CommandData


@dataclass
class CommandExecutionResult:
    result: Any
    initial_values: Dict[str, Any]
    final_values: Dict[str, Any]
    validation_results: Dict[str, Any]


def execute_command(
    organelle: "Organelle",
    command_data: CommandData,
    logger: Reporter,
    debug: bool = True,
) -> CommandExecutionResult:
    """
    Executes a command on an object based on the provided CommandData object,
    tracks specified attributes, logs the results, and performs optional validations.

    Parameters
    ----------
    command_data : CommandData
        The CommandData object containing all necessary information for command execution.
    logger : Reporter
        The logger object to use for logging.
    debug : bool, optional
        Whether to enable debug logging (default is True).

    Returns
    -------
    CommandExecutionResult
        A dataclass containing:
        - result: The result of the executed command
        - initial_values: Initial values of tracked attributes
        - final_values: Final values of tracked attributes
        - validation_results: Results of performed validations
    """
    obj = command_data.obj
    command = command_data.command
    tracked_attributes = command_data.tracked_attributes
    args = command_data.args
    kwargs = command_data.kwargs
    validations = command_data.validations

    initial_values = _log_attribute_values(
        logger, organelle, tracked_attributes, "Initial", debug
    )

    # Execute the command
    try:
        if callable(command):
            result = command(obj, *args, **kwargs)
        else:
            result = getattr(obj, command)(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing command '{command}': {str(e)}")
        raise

    final_values = _log_attribute_values(
        logger, organelle, tracked_attributes, "Final", debug
    )

    validation_results = _log_validation_results(
        logger, organelle, initial_values, final_values, validations
    )

    # Prepare and return results
    return CommandExecutionResult(
        result=result,
        initial_values=initial_values,
        final_values=final_values,
        validation_results=validation_results,
    )


def _log_attribute_values(
    logger: Reporter,
    organelle: "Organelle",
    tracked_attributes: List[str],
    stage: str,
    debug: bool = True,
) -> Dict[str, Any]:
    """
    Log the values of the tracked attributes.

    Parameters
    ----------
    logger : Reporter
        The logger object to use for logging.
    organelle : "Organelle"
        The organelle to log the attribute values of.
    tracked_attributes : List[str]
        The attributes to log.
    stage : str
        The stage of the simulation to log the attribute values for.
    debug : bool, optional
        Whether to enable debug logging (default is True).

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the attribute values.
    """
    values = {}
    for attr in tracked_attributes:
        try:
            quantity = organelle.get_metabolite_quantity(attr)
            values[attr] = quantity
        except AttributeError:
            logger.error(
                f"Object does not have 'get_metabolite_quantity' method. Skipping '{attr}'."
            )
        except ValueError as e:
            logger.warning(
                f"Error getting quantity for metabolite '{attr}': {str(e)}. Skipping."
            )
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while getting quantity for metabolite '{attr}': {str(e)}. Skipping."
            )

    if debug:
        logger.debug(f"{stage} values: {values}")

    return values


def _log_validation_results(
    logger: Reporter,
    organelle: "Organelle",
    initial_values: Dict[str, Any],
    final_values: Dict[str, Any],
    validations: List[Callable[[Any, Dict[str, Any], Dict[str, Any]], bool]],
) -> Dict[str, Any]:
    """
    Log the validation results.

    #! Need to validate this process

    Parameters
    ----------
    logger : Reporter
        The logger object to use for logging.
    organelle : "Organelle"
        The organelle to validate.
    initial_values : Dict[str, Any]
        The initial values of the tracked attributes.
    final_values : Dict[str, Any]
        The final values of the tracked attributes.
    validations : List[Callable[[Any, Dict[str, Any], Dict[str, Any]], bool]]
        The validations to perform. Each validation should take three arguments:
        the object, the initial values, and the final values.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the validation results.
    """
    # Perform validations
    validation_results = {}
    for idx, validation in enumerate(validations, start=1):
        try:
            validation_result = validation(organelle, initial_values, final_values)
            validation_results[f"validation_{idx}"] = validation_result
            if not validation_result:
                logger.warning(f"Validation {idx} failed: {validation.__name__}")
        except Exception as e:
            logger.error(f"Error during validation {validation.__name__}: {str(e)}")
            validation_results[f"validation_{idx}"] = f"error: {str(e)}"

    return validation_results
