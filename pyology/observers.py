from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cell import Cell
    from .simulation import Reporter


class Observer(ABC):
    @abstractmethod
    def observe(self, cell: "Cell", reporter: "Reporter"):
        pass


class NegativeMetaboliteObserver(Observer):
    def observe(self, cell: "Cell", reporter: "Reporter"):
        for compartment in [cell.cytoplasm, cell.mitochondrion]:
            for metabolite, quantity in compartment.metabolites.items():
                if quantity.quantity < 0:
                    reporter.log_warning(
                        f"Negative {metabolite} quantity detected in {compartment.__class__.__name__}: {quantity.quantity}"
                    )
                    quantity.quantity = 0


class AdenineNucleotideBalanceObserver(Observer):
    def __init__(self):
        self.initial_balance = None

    def observe(self, cell: "Cell", reporter: "Reporter"):
        current_balance = self._calculate_total_adenine_nucleotides(cell)

        if self.initial_balance is None:
            self.initial_balance = current_balance

        if abs(current_balance - self.initial_balance) > 1e-6:
            reporter.log_warning(
                f"Adenine nucleotide imbalance detected. "
                f"Current: {current_balance:.6f}, "
                f"Initial: {self.initial_balance:.6f}, "
                f"Difference: {current_balance - self.initial_balance:.6f}"
            )

    def _calculate_total_adenine_nucleotides(self, cell: "Cell") -> float:
        total = 0
        for compartment in [cell.cytoplasm, cell.mitochondrion]:
            total += sum(
                compartment.metabolites[m].quantity for m in ["ATP", "ADP", "AMP"]
            )
        return total
