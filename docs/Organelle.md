# **Class Overview**

The `Organelle` class represents a cellular compartment that contains metabolites and enzymes. It is designed with the following key features:

- **Attributes**:
  - `name`: A string representing the name of the organelle (class attribute).
  - `metabolites`: A `Metabolites` object containing all metabolites in the organelle.
  - `_glycolysis_rate`: A float representing the rate of glycolysis in the organelle.

- **Methods**:
  - `validate_initial_state()`: Validates the initial state of the organelle.
  - `add_metabolite(name, type, quantity, max_quantity)`: Adds a metabolite to the organelle.
  - `change_metabolite_quantity(metabolite_name, amount)`: Changes the quantity of a metabolite.
  - `is_metabolite_available(metabolite, amount)`: Checks if a metabolite is available in sufficient quantity.
  - `consume_metabolites(**metabolites)`: Consumes specified metabolites.
  - `produce_metabolites(**metabolites)`: Produces specified metabolites.
  - `get_metabolite_quantity(metabolite)`: Returns the quantity of a metabolite.
  - `set_metabolite_quantity(metabolite, quantity)`: Sets the quantity of a metabolite.
  - `get_metabolite(metabolite_name)`: Retrieves a metabolite object.

- **Metaclass**:
  - Uses `OrganelleMeta` as its metaclass for automatic registration of organelle classes.

- **Error Handling**:
  - Raises custom exceptions for various error conditions.

---

## **Detailed Breakdown**

### **Imports and Setup**

```python
import json
import os
from dataclasses import dataclass, field
from .exceptions import (
    GlycolysisRateError,
    InsufficientMetaboliteError,
    QuantityError,
    UnknownMetaboliteError,
)
from .metabolite import Metabolite, Metabolites
```

- **Standard Library Imports**: `json`, `os`, and `dataclasses` for file operations and data structures.
- **Custom Exceptions**: Imports custom exceptions for specific error handling.
- **Metabolite Classes**: Imports `Metabolite` and `Metabolites` classes.

---

### **CellMetabolites Data Class**

```python
@dataclass
class CellMetabolites:
    metabolites: Metabolites = field(default_factory=Metabolites)

    def __post_init__(self):
        # Load metabolites from JSON file
        # Add each metabolite to the Metabolites instance
```

- **Purpose**: Initializes a `Metabolites` instance with basic cell metabolites.
- **Functionality**: Loads metabolite data from a JSON file and registers each metabolite.

---

### **OrganelleMeta Metaclass**

```python
class OrganelleMeta(type):
    _registry = {}

    def __new__(cls, name: str, bases: tuple, namespace: dict) -> type:
        new_class = super().__new__(cls, name, bases, namespace)
        cls._registry[new_class.name] = new_class
        return new_class

    @classmethod
    def get_registry(cls: type) -> dict:
        return dict(cls._registry)
```

- **Purpose**: Serves as a metaclass for `Organelle`, automatically registering organelle classes.
- **Key Features**:
  - Maintains a registry of organelle classes.
  - Provides a method to retrieve the registry.

---

### **Organelle Class Initialization**

```python
class Organelle(metaclass=OrganelleMeta):
    name = "Organelle"

    def __init__(self):
        self.metabolites = CellMetabolites().metabolites
        self._glycolysis_rate = 1.0
        self.validate_initial_state()
```

- **Attributes**:
  - `name`: Class attribute for the organelle name.
  - `metabolites`: Initialized with `CellMetabolites`.
  - `_glycolysis_rate`: Initial glycolysis rate set to 1.0.
- **Initialization**: Calls `validate_initial_state()` to ensure proper setup.

---

### **Glycolysis Rate Property**

```python
@property
def glycolysis_rate(self):
    return self._glycolysis_rate

@glycolysis_rate.setter
def glycolysis_rate(self, value):
    if value <= 0:
        raise GlycolysisRateError(f"Invalid glycolysis rate: {value}")
    self._glycolysis_rate = value
```

- **Purpose**: Provides controlled access to the glycolysis rate.
- **Validation**: Ensures the rate is positive, raising an error if not.

---

### **State Validation**

```python
def validate_initial_state(self) -> None:
    # Validate metabolite quantities
    # Validate glycolysis rate
```

- **Purpose**: Ensures the initial state of the organelle is valid.
- **Checks**:
  - Metabolite quantities are within valid ranges.
  - Glycolysis rate is positive.

---

### **Metabolite Management**

```python
def add_metabolite(self, name: str, type: str, quantity: float, max_quantity: float) -> None:
    # Add or update metabolite in the organelle

def change_metabolite_quantity(self, metabolite_name: str, amount: float) -> None:
    # Change the quantity of a metabolite

def is_metabolite_available(self, metabolite: str, amount: float) -> bool:
    # Check if a metabolite is available in sufficient quantity

def consume_metabolites(self, **metabolites: float) -> None:
    # Consume specified metabolites

def produce_metabolites(self, **metabolites: float) -> None:
    # Produce specified metabolites

def get_metabolite_quantity(self, metabolite: str) -> float:
    # Get the quantity of a metabolite

def set_metabolite_quantity(self, metabolite: str, quantity: float) -> None:
    # Set the quantity of a metabolite

def get_metabolite(self, metabolite_name: str) -> Metabolite:
    # Get a metabolite object
```

- **Purpose**: Provides methods for managing metabolites within the organelle.
- **Key Features**:
  - Adding and updating metabolites.
  - Changing metabolite quantities.
  - Checking metabolite availability.
  - Consuming and producing metabolites.
  - Retrieving and setting metabolite quantities.
  - Getting metabolite objects.

---

### **Error Handling**

- **Custom Exceptions**:
  - `GlycolysisRateError`: For invalid glycolysis rates.
  - `InsufficientMetaboliteError`: When there's not enough of a metabolite.
  - `QuantityError`: For invalid metabolite quantities.
  - `UnknownMetaboliteError`: When a metabolite is not found in the organelle.

- **Usage**: These exceptions are raised in various methods to handle specific error conditions.

---

## **How the Class Models Organelles**

- **Metabolite Management**: 
  - Uses a `Metabolites` object to store and manage individual metabolites.
  - Provides methods for adding, updating, and querying metabolite quantities.

- **Glycolysis Rate**:
  - Maintains a glycolysis rate, which can be used to model metabolic processes.

- **Validation**:
  - Ensures that the organelle's state remains valid through various checks.

- **Flexibility**:
  - The class is designed to be subclassed for specific types of organelles.
  - The metaclass allows for automatic registration of different organelle types.

---

## **Usage Example**

```python
# Create an organelle
organelle = Organelle()

# Add a new metabolite
organelle.add_metabolite("Glucose", "sugar", 10.0, 100.0)

# Change metabolite quantity
organelle.change_metabolite_quantity("Glucose", -5.0)

# Check metabolite availability
if organelle.is_metabolite_available("Glucose", 3.0):
    organelle.consume_metabolites(Glucose=3.0)

# Produce metabolites
organelle.produce_metabolites(ATP=2.0)

# Get metabolite quantity
glucose_quantity = organelle.get_metabolite_quantity("Glucose")

# Set glycolysis rate
organelle.glycolysis_rate = 1.5

# Get a metabolite object
glucose = organelle.get_metabolite("Glucose")
```

This example demonstrates the basic usage of the `Organelle` class, including metabolite management, quantity changes, and glycolysis rate adjustment.
