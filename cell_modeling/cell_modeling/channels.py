"""
A channel is a protein that forms a pore in the cell membrane through which
ions can pass.
"""


class Channel:
    """
    Represents a channel that forms a pore in the cell membrane through which
    ions can pass.

    Parameters
    ----------
    ion_type : str
        The type of ion that the channel transports.

    Methods
    -------
    open : function
        Opens the channel.
    close : function
        Closes the channel.
    """

    def __init__(self, ion_type: str) -> None:
        self.ion_type = ion_type  # e.g., Na+, K+

    def open(self) -> None:
        """
        Opens the channel.
        """
        print(f"{self.ion_type} channel opened.")

    def close(self) -> None:
        """
        Closes the channel.
        """
        print(f"{self.ion_type} channel closed.")
