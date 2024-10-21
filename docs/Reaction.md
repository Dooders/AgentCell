## **Class Overview**

The `Reaction` class represents a biochemical reaction with the following key features:

- **Attributes**:
  - `name`: A string representing the name of the reaction.
  - `enzyme`: An `Enzyme` object that catalyzes the reaction.
  - `substrates`: A dictionary mapping substrate names to their stoichiometric coefficients.
  - `products`: A dictionary mapping product names to their stoichiometric coefficients.
  - `reversible`: A boolean indicating whether the reaction is reversible.

- **Methods**:
  - `can_react(organelle)`: Checks if the reaction can proceed based on substrate availability in the given organelle.
  - `execute(organelle, time_step, use_rates)`: Executes the reaction, updating metabolite quantities, and optionally considering reaction rates.
  - `_execute_with_rates(organelle, time_step)`: Executes the reaction using enzyme kinetics to calculate reaction rates.
  - `_execute_without_rates(organelle, time_step)`: Executes the reaction without considering reaction rates (stoichiometric execution).
  
- **Logging and Error Handling**:
  - Uses the `logging` module to log important information and debug messages.
  - Raises a custom `ReactionError` if the reaction fails to execute.

---

## **Detailed Breakdown**

### **Imports and Setup**

```python
import logging
from typing import TYPE_CHECKING, Dict
from .exceptions import ReactionError  # Custom exception for reaction errors

if TYPE_CHECKING:
    from .enzymes import Enzyme  # Type hinting for the Enzyme class

logger = logging.getLogger(__name__)
```

- **Logging**: Sets up a logger specific to this module to handle logging messages.
- **Type Hinting**: Uses `TYPE_CHECKING` to avoid circular imports when type hinting the `Enzyme` class.
- **Custom Exception**: Imports a custom `ReactionError` exception for handling reaction execution errors.

---

### **Class Initialization**

```python
class Reaction:
    def __init__(
        self,
        name: str,
        enzyme: "Enzyme",
        substrates: Dict[str, float],
        products: Dict[str, float],
        reversible: bool = False,
    ):
        self.name = name
        self.enzyme = enzyme
        self.substrates = substrates
        self.products = products
        self.reversible = reversible
```

- **Parameters**:
  - `name`: The name of the reaction.
  - `enzyme`: An instance of the `Enzyme` class associated with this reaction.
  - `substrates`: A dictionary where keys are substrate names and values are their stoichiometric coefficients (amounts required for the reaction).
  - `products`: A dictionary where keys are product names and values are their stoichiometric coefficients (amounts produced by the reaction).
  - `reversible`: Indicates if the reaction can proceed in both directions.

- **Initialization**: Stores the provided parameters as instance attributes for later use.

---

### **Checking Reaction Feasibility**

```python
def can_react(self, organelle) -> bool:
    for substrate, amount in self.substrates.items():
        if organelle.get_metabolite_quantity(substrate) < amount:
            return False
    return True
```

- **Purpose**: Determines if the reaction can proceed based on the availability of substrates in the organelle.
- **Mechanism**:
  - Iterates over each substrate and its required amount.
  - Uses `organelle.get_metabolite_quantity(substrate)` to check the available quantity.
  - Returns `False` if any substrate is insufficient; otherwise, returns `True`.

---

### **Executing the Reaction**

```python
def execute(
    self, organelle, time_step: float = 1.0, use_rates: bool = False
) -> float:
    # Logging and initial checks
    # Decide execution method based on use_rates
    # Handle execution result and exceptions
    return result
```

- **Parameters**:
  - `organelle`: The organelle object where the reaction occurs, which manages metabolite quantities.
  - `time_step`: The duration over which the reaction takes place (default is 1.0).
  - `use_rates`: A boolean flag indicating whether to use enzyme kinetics to calculate reaction rates.

- **Process**:
  1. **Logging**: Logs the execution start, substrates, products, and substrate availability.
  2. **Time Step Validation**: Raises a `ValueError` if `time_step` is negative.
  3. **Execution Path**:
     - If `use_rates` is `True`, calls `_execute_with_rates`.
     - If `False`, calls `_execute_without_rates`.
  4. **Result Handling**:
     - If execution result is `0.0`, logs an error and raises a `ReactionError`.
     - Logs success and returns the execution result (rate or reaction occurrence indicator).

---

### **Executing with Rates**

```python
def _execute_with_rates(self, organelle, time_step: float) -> float:
    # Calculate reaction rate using enzyme kinetics
    # Determine limiting factors
    # Adjust metabolite quantities based on actual rate
    # Log execution details
    return actual_rate
```

- **Purpose**: Executes the reaction considering enzyme kinetics and substrate availability over a given time step.

- **Process**:
  1. **Metabolite Gathering**:
     - Collects metabolite objects required for rate calculation.
     - Checks if the enzyme's `k_m` (Michaelis constant) is a dictionary; if so, includes additional metabolites.
  2. **Rate Calculation**:
     - Calls `self.enzyme.calculate_rate(metabolites)` to compute the initial reaction rate.
     - Logs the initial reaction rate.
  3. **Limiting Factors**:
     - Calculates potential limiting factors, including:
       - `reaction_rate * time_step`: The amount of reaction that can occur in the time step.
       - Substrate availability ratios.
     - Determines the `actual_rate` as the minimum of these factors.
     - Logs potential limiting factors and identifies which factor limits the reaction.
  4. **Metabolite Adjustments**:
     - Consumes substrates by decreasing their quantities in the organelle.
     - Produces products by increasing their quantities in the organelle.
  5. **Logging**:
     - Logs the execution details, including consumed and produced metabolites and the actual rate.
  6. **Return**: Returns the `actual_rate` to indicate the extent of the reaction.

---

### **Executing without Rates**

```python
def _execute_without_rates(self, organelle, time_step: float) -> float:
    # Check substrate availability
    # Adjust metabolite quantities based on stoichiometry
    # Log execution details
    return 1.0  # Indicates the reaction occurred once
```

- **Purpose**: Executes the reaction based purely on stoichiometry, without considering reaction kinetics.

- **Process**:
  1. **Substrate Availability Check**:
     - Ensures all substrates are available in required amounts.
     - Logs an error and returns `0.0` if any substrate is insufficient.
  2. **Metabolite Adjustments**:
     - Consumes substrates by decreasing their quantities.
     - Produces products by increasing their quantities.
     - Logs detailed information about consumed and produced amounts.
  3. **Logging**:
     - Logs the successful execution of the reaction.
  4. **Return**: Returns `1.0` to indicate that the reaction occurred once.

---

### **Error Handling**

- **ReactionError**:
  - A custom exception raised when the reaction fails to execute.
  - Used to signal issues that prevent the reaction from proceeding, such as insufficient substrates even after rate adjustments.

- **ValueError**:
  - Raised if the `time_step` provided is negative.

---

### **Logging**

- **Info-Level Logs**:
  - Execution start and end messages.
  - Substrates and products involved.
  - Successful execution details.

- **Debug-Level Logs**:
  - Intermediate calculations like reaction rates and limiting factors.
  - Detailed metabolite consumption and production amounts.

- **Error-Level Logs**:
  - Insufficient substrate quantities.
  - Failure of the reaction execution.

- **Logger Configuration**:
  - The logger is configured at the module level and uses the module's `__name__` to categorize logs.
  - Adjust the logging level elsewhere in your application to control the verbosity.

---

### **Helper Function: `perform_reaction`**

```python
def perform_reaction(metabolites: Dict[str, float], reaction: Reaction) -> bool:
    return reaction.execute(metabolites)
```

- **Purpose**: Provides a simple interface to execute a reaction given a dictionary of metabolite concentrations.
- **Parameters**:
  - `metabolites`: A dictionary mapping metabolite names to their quantities.
  - `reaction`: The `Reaction` object to be executed.
- **Return Value**: Returns the result of `reaction.execute(metabolites)`.

---

## **How the Class Models Reactions**

- **Enzyme Kinetics**:
  - The `Reaction` class works closely with an `Enzyme` class, leveraging its `calculate_rate` method to determine reaction rates based on enzyme kinetics.
  - Supports Michaelis-Menten kinetics and can handle complex cases where `k_m` is a dictionary of multiple substrates.

- **Substrate and Product Management**:
  - Substrates and products are managed as dictionaries with their stoichiometric coefficients, allowing for flexible and accurate representation of chemical reactions.
  - The methods adjust metabolite quantities in the `organelle` based on the reaction's stoichiometry and kinetics.

- **Organelle Interaction**:
  - The `organelle` parameter represents the environment where the reaction occurs.
  - It is expected to provide methods like `get_metabolite_quantity`, `get_metabolite`, and `change_metabolite_quantity` to interact with metabolite concentrations.

- **Reversible Reactions**:
  - The `reversible` attribute indicates if the reaction can proceed in both directions, although the provided code doesn't explicitly handle the reverse reaction. This attribute can be used to extend functionality for reversible reactions.

- **Rate Limiting Factors**:
  - The reaction considers both the calculated reaction rate and substrate availability to determine the actual rate at which the reaction proceeds.
  - This models real-world biochemical scenarios where substrate depletion can limit reaction rates.

---

## **Usage Example**

```python
# Assuming necessary classes and methods are defined elsewhere
from enzymes import Enzyme
from organelles import Organelle

# Define an enzyme with appropriate kinetics
enzyme = Enzyme(
    name='Hexokinase',
    vmax=0.1,
    k_m={'Glucose': 0.05, 'ATP': 0.05}
)

# Define a reaction
reaction = Reaction(
    name='Glucose Phosphorylation',
    enzyme=enzyme,
    substrates={'Glucose': 1.0, 'ATP': 1.0},
    products={'Glucose-6-Phosphate': 1.0, 'ADP': 1.0},
    reversible=False
)

# Create an organelle with initial metabolite quantities
organelle = Organelle(metabolites={
    'Glucose': 10.0,
    'ATP': 10.0,
    'Glucose-6-Phosphate': 0.0,
    'ADP': 0.0
})

# Execute the reaction
reaction.execute(organelle, time_step=1.0, use_rates=True)
```

- **In this example**:
  - An `Enzyme` and `Reaction` are defined with specific kinetics and stoichiometry.
  - An `Organelle` is initialized with certain metabolite quantities.
  - The `reaction.execute` method is called to perform the reaction, updating the metabolite quantities in the organelle based on the reaction rate
