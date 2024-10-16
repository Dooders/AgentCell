from .enzymes import Enzyme

def create_default_enzymes():
    return {
        "hexokinase": Enzyme(
            name="Hexokinase",
            k_cat=200.0,
            k_m={"glucose": 0.1, "ATP": 0.3}
        ),
        "phosphofructokinase": Enzyme(
            name="Phosphofructokinase",
            k_cat=150.0,
            k_m={"fructose-6-phosphate": 0.08, "ATP": 0.25}
        ),
        # ... other enzymes ...
    }
