from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from allocation.domain.exceptions import OutOfStock


class Product:
    sku: str
    batches: list[Batch]
    version: int

    def __init__(self, sku: str, batches: list[Batch], version: int = 0):
        self.sku = sku
        self.batches = batches
        self.version = version

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version += 1
            return batch.ref
        except StopIteration:
            raise OutOfStock(f"Out of stack for SKU {line.sku}")


class Batch:
    ref: str
    sku: str
    eta: Optional[date]
    purchased_qty: int
    available_qty: int
    allocated_qty: int
    _allocations: set[OrderLine]

    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self.ref = ref
        self.sku = sku
        self.eta = eta
        self.purchased_qty = qty
        self._allocations = set()

    @property
    def allocated_qty(self) -> int:
        return sum([line.qty for line in self._allocations])

    @property
    def available_qty(self) -> int:
        return self.purchased_qty - self.allocated_qty

    def allocate(self, line: OrderLine) -> None:
        if not self.can_allocate(line):
            return

        self._allocations.add(line)

    def can_allocate(self, line: OrderLine) -> bool:
        if self.sku != line.sku:
            return False

        if self.available_qty < line.qty:
            return False

        return True

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False

        return other.ref == self.ref

    def __gt__(self, other):
        if self.eta is None:
            return False

        if other.eta is None:
            return True

        return self.eta > other.eta

    def __hash__(self):
        return hash(self.ref)


@dataclass(unsafe_hash=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int
