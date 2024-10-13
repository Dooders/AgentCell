from dataclasses import dataclass, field


@dataclass
class Enzyme:
    name: str
    activity: float = field(default=1.0)
    vmax: float = field(default=1.0)
    km: float = field(default=0.1)


@dataclass
class Metabolite:
    name: str = field(default="")
    quantity: int = field(default=0)
    max_quantity: int = field(default=1000)


@dataclass
class Effector:
    name: str = field(default="")
    concentration: float = field(default=0)
    Ki: float = field(default=0.1)  # Inhibition constant
    Ka: float = field(default=0.1)  # Activation constant
