"""
Cell Membrane

Biological Background
Structure: 
    Composed of a phospholipid bilayer with embedded proteins 
    (transporters, channels, receptors).

Function:
    Selective Permeability: Regulates the entry and exit of substances.
    Signal Transduction: Contains receptors for signaling molecules.
    Cell Recognition: Glycoproteins and glycolipids serve as identification tags.

Modeling Considerations
Transport Mechanisms:
    Passive Transport: Simple diffusion, facilitated diffusion via channels.
    Active Transport: Requires energy (ATP) to move substances against 
    concentration gradients.
Receptors and Signaling:
    Model ligand-receptor interactions.
    Implement signal transduction pathways initiated at the membrane.
"""


class CellMembrane:
    """
    Represents the cell membrane of a cell.

    Methods
    -------
    add_channel : function
        Adds a channel to the cell membrane.
    add_transporter : function
        Adds a transporter to the cell membrane.
    add_receptor : function
        Adds a receptor to the cell membrane.
    transport_substance : function
        Handles the movement of substances across the membrane.
    receive_signal : function
        Processes external signals via receptors.
    """

    def __init__(self) -> None:
        self.channels = []
        self.transporters = []
        self.receptors = []

    def add_channel(self, channel: Channel) -> None:
        self.channels.append(channel)

    def add_transporter(self, transporter: Transporter) -> None:
        self.transporters.append(transporter)

    def add_receptor(self, receptor: Receptor) -> None:
        self.receptors.append(receptor)

    def transport_substance(self, substance: str, direction: str) -> None:
        """
        Handle the movement of substances across the membrane.
        Parameters:
        - substance (str): The substance to transport.
        - direction (str): 'in' or 'out'.
        """
        # Logic for passive and active transport
        pass

    def receive_signal(self, ligand_type: str) -> None:
        """
        Process external signals via receptors.
        """
        for receptor in self.receptors:
            if receptor.ligand_type == ligand_type:
                receptor.receive_signal(ligand_type)
