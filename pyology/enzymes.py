"""
Signal Transduction Pathways
    Modeling Cascades:
        Implement sequences where one activated molecule activates others.
    Feedback Loops:
        Incorporate positive and negative feedback mechanisms.
"""


class Enzyme:
    """
    Represents an enzyme that catalyzes a biochemical reaction.

    Parameters
    ----------
    name : str
        The name of the enzyme.
    vmax : float
        The maximum rate of the enzyme.
    km : float
        The Michaelis-Menten constant.

    Methods
    -------
    catalyze : function
        Catalyzes a biochemical reaction.
    """

    def __init__(self, name: str, vmax: float, km: float):
        self.name = name
        self.vmax = vmax
        self.km = km

    def calculate_rate(self, substrate_conc: float) -> float:
        """
        Calculates the reaction rate based on substrate concentration.

        Parameters
        ----------
        substrate_conc : float
            The concentration of the substrate.

        Returns
        -------
        float
            The rate of the reaction.
        """
        rate = (self.vmax * substrate_conc) / (self.km + substrate_conc)
        return rate
