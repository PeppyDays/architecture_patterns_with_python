from datetime import date
from typing import Optional

from allocation.application.exceptions import InvalidSku
from allocation.application.unit_of_work import UnitOfWork
from allocation.domain import services as domain_services
from allocation.domain.models import Batch
from allocation.domain.models import OrderLine


def is_valid_sku(sku: str, batches: list[Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int, uow: UnitOfWork) -> str:
    line = OrderLine(order_id, sku, qty)

    with uow:
        batches = uow.batches.list()

        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f"Invalid SKU {sku}")

        batch_ref = domain_services.allocate(line, batches)
        uow.commit()

    return batch_ref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], uow: UnitOfWork):
    with uow:
        uow.batches.add(Batch(ref, sku, qty, eta))
        uow.commit()
