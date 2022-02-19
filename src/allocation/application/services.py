from datetime import date
from typing import Optional

from allocation.application.exceptions import InvalidSku
from allocation.domain import services as domain_services
from allocation.domain.models import Batch
from allocation.domain.models import OrderLine
from allocation.domain.repositories import Repository


def is_valid_sku(sku: str, batches: list[Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int, repository: Repository, session) -> str:
    batches = repository.list()

    if not is_valid_sku(sku, batches):
        raise InvalidSku(f"Invalid SKU {sku}")

    line = OrderLine(order_id, sku, qty)
    batch_ref = domain_services.allocate(line, batches)
    session.commit()

    return batch_ref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], repository: Repository, session) -> None:
    repository.add(Batch(ref, sku, qty, eta))
    session.commit()
