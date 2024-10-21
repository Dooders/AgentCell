import logging
from typing import TYPE_CHECKING, Dict

from .exceptions import InsufficientSubstrateError, ReactionError

if TYPE_CHECKING:
    from .enzymes import Enzyme
    from .organelle import Organelle


logger = logging.getLogger(__name__)


class Reaction:
    def __init__(
        self,
        name: str,
        enzyme: "Enzyme",
        substrates: Dict[str, float],
        products: Dict[str, float],
        reversible: bool = False,
    ):
        """
        Initialize a Reaction object.

        Parameters
        ----------
        name : str
            The name of the reaction.
        enzyme : Enzyme
            The enzyme catalyzing the reaction.
        substrates : Dict[str, float]
            A dictionary of substrate names and their quantities.
        products : Dict[str, float]
            A dictionary of product names and their quantities.
        reversible : bool, optional
            Whether the reaction is reversible. Defaults to False.
        """
        self.name = name
        self.enzyme = enzyme
        self.substrates = substrates
        self.products = products
        self.reversible = reversible

    def can_react(self, organelle: "Organelle") -> bool:
        """
        Check if the reaction can proceed based on available substrates.

        Parameters
        ----------
        organelle : Organelle
            The organelle containing the metabolites.

        Returns
        -------
        bool: True if all substrates are available in sufficient quantities, False otherwise.
        """
        for substrate, amount in self.substrates.items():
            if organelle.get_metabolite_quantity(substrate) < amount:
                return False
        return True

    def transform(
        self,
        organelle: "Organelle",
        time_step: float = 1.0,
        use_rates: bool = False,
        reverse: bool = False,
    ) -> float:
        """
        Execute the reaction transformation.

        Parameters
        ----------
        organelle : Organelle
            The organelle where the reaction takes place.
        time_step : float, optional
            The duration of the reaction step. Defaults to 1.0.
        use_rates : bool, optional
            Whether to use enzyme kinetics. Defaults to False.
        reverse : bool, optional
            Whether to reverse the reaction direction. Defaults to False.

        Returns
        -------
        float: The rate at which the reaction proceeded.

        Raises
        ------
        ValueError: If the time step is negative or if trying to reverse a non-reversible reaction.
        ReactionError: If the reaction fails to execute.
        """
        if reverse and not self.reversible:
            raise ValueError(f"Cannot reverse non-reversible reaction '{self.name}'")

        if time_step < 0:
            raise ValueError("Time step cannot be negative")

        substrates, products = self._get_reaction_direction(reverse)

        logger.info(f"Executing {self.name} reaction {'(reversed)' if reverse else ''}")
        logger.info(f"Substrates: {substrates}")
        logger.info(f"Products: {products}")
        for substrate, amount in substrates.items():
            available = organelle.get_metabolite_quantity(substrate)
            logger.info(f"{substrate} - Required: {amount}, Available: {available}")

        try:
            if use_rates:
                result = self._execute_with_rates(
                    organelle, time_step, substrates, products
                )
            else:
                result = self._execute_without_rates(
                    organelle, time_step, substrates, products
                )

            if result == 0.0:
                raise InsufficientSubstrateError(
                    f"Reaction '{self.name}' failed to execute due to insufficient substrates"
                )

            logger.info(f"Reaction '{self.name}' executed successfully")
            return result

        except (ReactionError, InsufficientSubstrateError) as e:
            logger.error(f"Error during '{self.name}' execution: {e}")
            raise

    def _get_reaction_direction(
        self, reverse: bool
    ) -> tuple[Dict[str, float], Dict[str, float]]:
        """
        Get the correct substrates and products based on the reaction direction.

        Parameters
        ----------
        reverse : bool
            Whether to reverse the reaction direction.

        Returns
        -------
        tuple: A tuple containing the substrates and products dictionaries.
        """
        if reverse:
            return self.products, self.substrates
        return self.substrates, self.products

    def _execute_with_rates(
        self,
        organelle: "Organelle",
        time_step: float,
        substrates: Dict[str, float],
        products: Dict[str, float],
    ) -> float:
        """
        Execute the reaction using enzyme kinetics.

        Parameters
        ----------
        organelle : Organelle
            The organelle where the reaction takes place.
        time_step : float
            The duration of the reaction step.
        substrates : Dict[str, float]
            A dictionary of substrate names and their quantities.
        products : Dict[str, float]
            A dictionary of product names and their quantities.

        Returns
        -------
        float: The actual rate at which the reaction proceeded.
        """
        # Calculate reaction rate using the updated Enzyme.calculate_rate method
        metabolites = {met: organelle.get_metabolite(met) for met in substrates}

        # Check if k_m is a dictionary or a single value
        if isinstance(self.enzyme.k_m, dict):
            metabolites.update(
                {met: organelle.get_metabolite(met) for met in self.enzyme.k_m.keys()}
            )

        reaction_rate = self.enzyme.calculate_rate(metabolites)

        # Log intermediate values
        logger.debug(
            f"Reaction '{self.name}': Initial reaction rate: {reaction_rate:.6f}"
        )

        # Calculate potential limiting factors
        limiting_factors = {"reaction_rate": reaction_rate * time_step}
        for met, amount in substrates.items():
            if amount > 0:
                limiting_factors[f"{met}_conc"] = (
                    organelle.get_metabolite_quantity(met) / amount
                )

        # Determine actual rate based on available metabolites
        actual_rate = min(limiting_factors.values())

        # Log all limiting factors
        logger.debug(f"Reaction '{self.name}': Potential limiting factors:")
        for factor_name, factor_value in limiting_factors.items():
            logger.debug(f"  - {factor_name}: {factor_value:.6f}")

        # Identify the actual limiting factor(s)
        limiting_factor_names = [
            name for name, value in limiting_factors.items() if value == actual_rate
        ]
        logger.debug(
            f"Reaction '{self.name}': Rate limited by {', '.join(limiting_factor_names)}. "
            f"Actual rate: {actual_rate:.6f}"
        )

        # Consume metabolites
        for metabolite, amount in substrates.items():
            organelle.change_metabolite_quantity(metabolite, -amount * actual_rate)

        # Produce metabolites
        for metabolite, amount in products.items():
            organelle.change_metabolite_quantity(metabolite, amount * actual_rate)

        # Add log entry
        logger.info(
            f"Executed reaction '{self.name}' with rate {actual_rate:.4f}. "
            f"Consumed: {', '.join([f'{m}: {a * actual_rate:.4f}' for m, a in substrates.items()])}. "
            f"Produced: {', '.join([f'{m}: {a * actual_rate:.4f}' for m, a in products.items()])}"
        )

        return actual_rate

    def _execute_without_rates(
        self,
        organelle: "Organelle",
        time_step: float,
        substrates: Dict[str, float],
        products: Dict[str, float],
    ) -> float:
        """
        Execute the reaction without using enzyme kinetics.

        Parameters
        ----------
        organelle : Organelle
            The organelle where the reaction takes place.
        time_step : float
            The duration of the reaction step.
        substrates : Dict[str, float]
            A dictionary of substrate names and their quantities.
        products : Dict[str, float]
            A dictionary of product names and their quantities.

        Returns
        -------
        float: 1.0 if the reaction occurred, 0.0 otherwise.
        """
        for metabolite, amount in substrates.items():
            available = organelle.get_metabolite_quantity(metabolite)
            if available < amount:
                raise InsufficientSubstrateError(
                    f"Insufficient {metabolite} for reaction '{self.name}'. "
                    f"Required: {amount}, Available: {available}"
                )

        # Consume substrates
        for metabolite, amount in substrates.items():
            organelle.change_metabolite_quantity(metabolite, -amount)
            logger.debug(f"Reaction '{self.name}': Consumed {amount} {metabolite}")

        # Produce products
        for metabolite, amount in products.items():
            organelle.change_metabolite_quantity(metabolite, amount)
            logger.debug(f"Reaction '{self.name}': Produced {amount} {metabolite}")

        # Add log entry
        logger.info(
            f"Executed reaction '{self.name}' without rates. "
            f"Consumed: {', '.join([f'{m}: {a:.4f}' for m, a in substrates.items()])}. "
            f"Produced: {', '.join([f'{m}: {a:.4f}' for m, a in products.items()])}"
        )

        return 1.0  # Return 1.0 to indicate the reaction occurred once


def perform_reaction(
    organelle: "Organelle", reaction: Reaction, reverse: bool = False, **kwargs
) -> bool:
    """
    #! Is this even needed? If you have a reaction object, you can just call its transform method directly.
    Executes the specified reaction on the given organelle.

    Parameters
    ----------
    organelle : Organelle
        Object with methods to manage metabolites.
    reaction : Reaction
        The reaction to perform.
    reverse : bool, optional
        Whether to reverse the reaction direction. Defaults to False.
    **kwargs: Additional keyword arguments for reaction execution.

    Returns
    -------
    bool: True if the reaction succeeded, False otherwise.

    Raises
    ------
    ReactionError: If the reaction fails to execute.
    """
    try:
        result = reaction.transform(organelle, reverse=reverse, **kwargs)
        return result > 0
    except ReactionError:
        return False
