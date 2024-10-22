# **Class Overview**

The `Enzyme` class represents an enzyme that catalyzes biochemical reactions, with the following key features:

- **Attributes**:
  - `name`: A string representing the name of the enzyme.
  - `k_cat`: The catalytic constant (turnover number) of the enzyme.
  - `k_m`: A dictionary mapping substrate names to their Michaelis constants.
  - `inhibitors`: A dictionary of inhibitors and their properties.
  - `activators`: A dictionary of activators and their constants.
  - `active`: A boolean indicating whether the enzyme is active.
  - `downstream_enzymes`: A list of enzymes regulated by this enzyme.
  - `hill_coefficients`: A dictionary mapping substrates to their Hill coefficients.

- **Methods**:
  - `calculate_rate(metabolites)`: Calculates the rate of the enzyme's reaction.
  - `activate()`: Activates the enzyme and its downstream enzymes.
  - `deactivate()`: Deactivates the enzyme.
  - `regulate_enzyme(target_enzyme, action)`: Regulates another enzyme.
  - `catalyze(metabolites, dt)`: Simulates the catalysis over a time step.

- **Helper Methods**:
  - `_calculate_kinetics(metabolites)`: Calculates Michaelis-Menten kinetics with cooperative binding.
  - `_calculate_inhibition_effects(metabolites)`: Calculates inhibition effects on reaction rate.
  - `_calculate_activation_effects(metabolites)`: Calculates activation effects on reaction rate.

---

## **Detailed Breakdown**

### **Imports and Setup**

```python
from typing import Dict, List
from .metabolite import Metabolite
```

- **Type Hinting**: Uses `Dict` and `List` for type annotations.
- **Metabolite Import**: Imports the `Metabolite` class for handling metabolite quantities.

---

### **Class Initialization**

```python
class Enzyme:
    def __init__(
        self,
        name: str,
        k_cat: float,
        k_m: Dict[str, float],
        inhibitors: Dict[str, Dict[str, float]] = None,
        activators: Dict[str, float] = None,
        active: bool = True,
        downstream_enzymes: List["Enzyme"] = None,
        hill_coefficients: Dict[str, float] = None,
    ):
        # Initialize attributes
```

- **Parameters**:
  - `name`: The name of the enzyme.
  - `k_cat`: The catalytic constant of the enzyme.
  - `k_m`: A dictionary of Michaelis constants for multiple substrates.
  - `inhibitors`: A dictionary of inhibitors and their properties (optional).
  - `activators`: A dictionary of activators and their constants (optional).
  - `active`: Whether the enzyme is active (default is True).
  - `downstream_enzymes`: A list of enzymes regulated by this enzyme (optional).
  - `hill_coefficients`: A dictionary of Hill coefficients for substrates (optional).

- **Initialization**: Stores the provided parameters as instance attributes, with default values for optional parameters.

---

### **Calculating Reaction Rate**

```python
def calculate_rate(self, metabolites: Dict[str, Metabolite]) -> float:
    if not self.active:
        return 0.0

    rate = self.k_cat
    rate *= self._calculate_kinetics(metabolites)
    rate *= self._calculate_inhibition_effects(metabolites)
    rate *= self._calculate_activation_effects(metabolites)

    return rate
```

- **Purpose**: Calculates the overall reaction rate considering enzyme kinetics, inhibition, and activation.
- **Process**:
  1. Checks if the enzyme is active.
  2. Starts with the base rate (`k_cat`).
  3. Applies kinetics, inhibition, and activation effects.
  4. Returns the final calculated rate.

---

### **Helper Methods for Rate Calculation**

```python
def _calculate_kinetics(self, metabolites: Dict[str, Metabolite]) -> float:
    # Calculate Michaelis-Menten kinetics with cooperative binding

def _calculate_inhibition_effects(self, metabolites: Dict[str, Metabolite]) -> float:
    # Calculate inhibition effects on reaction rate

def _calculate_activation_effects(self, metabolites: Dict[str, Metabolite]) -> float:
    # Calculate activation effects on reaction rate
```

- **Kinetics Calculation**: 
  - Implements Michaelis-Menten kinetics with cooperative binding (Hill equation).
  - Handles multiple substrates and their respective Hill coefficients.

- **Inhibition Effects**: 
  - Supports multiple types of inhibition (competitive, non-competitive, uncompetitive).
  - Calculates inhibition factor based on inhibitor concentrations and constants.

- **Activation Effects**:
  - Calculates activation factor based on activator concentrations and constants.

---

### **Enzyme Regulation**

```python
def activate(self) -> None:
    self.active = True
    for enzyme in self.downstream_enzymes:
        enzyme.activate()

def deactivate(self) -> None:
    self.active = False

def regulate_enzyme(self, target_enzyme: "Enzyme", action: str) -> None:
    if action == "activate":
        target_enzyme.activate()
    elif action == "deactivate":
        target_enzyme.deactivate()
    else:
        raise ValueError("Invalid action. Use 'activate' or 'deactivate'.")
```

- **Activation**: Activates the enzyme and recursively activates downstream enzymes.
- **Deactivation**: Deactivates the enzyme.
- **Regulation**: Allows the enzyme to regulate other enzymes by activating or deactivating them.

---

### **Catalysis Simulation**

```python
def catalyze(self, metabolites: Dict[str, Metabolite], dt: float):
    rate = self.calculate_rate(metabolites)
    if rate == 0.0:
        return

    # Define reaction stoichiometry
    stoichiometry = {substrate: -1 for substrate in self.k_m.keys()}
    stoichiometry.update({f"product{i+1}": 1 for i in range(len(self.k_m))})

    # Calculate and apply changes to metabolite quantities
    delta = rate * dt
    for metabolite_name, coefficient in stoichiometry.items():
        metabolite = metabolites.get(metabolite_name)
        if metabolite is None:
            if coefficient > 0:
                metabolites[metabolite_name] = Metabolite(
                    name=metabolite_name,
                    quantity=coefficient * delta,
                    max_quantity=100.0,
                )
            else:
                return
        else:
            new_quantity = metabolite.quantity + coefficient * delta
            metabolite.quantity = max(new_quantity, 0.0)

    # Trigger downstream enzymes
    for enzyme in self.downstream_enzymes:
        self.regulate_enzyme(enzyme, "activate")
```

- **Purpose**: Simulates the catalysis process over a given time step.
- **Process**:
  1. Calculates the reaction rate.
  2. Defines the reaction stoichiometry.
  3. Updates metabolite quantities based on the calculated rate and time step.
  4. Creates new product metabolites if they don't exist.
  5. Activates downstream enzymes in the cascade.

---

## **How the Class Models Enzyme Behavior**

- **Complex Kinetics**: 
  - Supports Michaelis-Menten kinetics with cooperative binding (Hill equation).
  - Handles multiple substrates with individual Michaelis constants and Hill coefficients.

- **Regulation Mechanisms**:
  - Models enzyme inhibition with different types (competitive, non-competitive, uncompetitive).
  - Incorporates enzyme activation through activator molecules.
  - Supports enzyme cascades through downstream enzyme regulation.

- **Dynamic Activity**:
  - Enzymes can be activated or deactivated, affecting their catalytic activity.
  - Activation can propagate through enzyme cascades.

- **Realistic Catalysis Simulation**:
  - Simulates catalysis over time, considering reaction rates and stoichiometry.
  - Handles creation of new product metabolites and depletion of substrates.

---

## **Usage Example**

```python
from pyology.enzymes import Enzyme
from pyology.metabolite import Metabolite

# Create an enzyme instance
complex_enzyme = Enzyme(
    name="Complex Enzyme",
    k_cat=100,
    k_m={"substrate1": 10, "substrate2": 5},
    inhibitors={
        "inhibitor1": {"type": "competitive", "ki": 1},
        "inhibitor2": {"type": "noncompetitive", "ki": 2},
    },
    activators={"activator1": 0.5},
    hill_coefficients={"substrate1": 2, "substrate2": 1},
)

# Create metabolites
metabolites = {
    "substrate1": Metabolite(name="substrate1", quantity=20),
    "substrate2": Metabolite(name="substrate2", quantity=15),
    "inhibitor1": Metabolite(name="inhibitor1", quantity=0.5),
    "activator1": Metabolite(name="activator1", quantity=1),
    "product1": Metabolite(name="product1", quantity=0),
}

# Calculate reaction rate
rate = complex_enzyme.calculate_rate(metabolites)
print(f"Reaction rate: {rate}")

# Simulate catalysis
time_step = 0.1
complex_enzyme.catalyze(metabolites, time_step)

# Check updated metabolite quantities
for name, metabolite in metabolites.items():
    print(f"{name}: {metabolite.quantity}")
```

This example demonstrates how to create an `Enzyme` instance with complex kinetics, calculate its reaction rate, and simulate catalysis over a time step.
