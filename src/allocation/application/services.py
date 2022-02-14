from allocation.application.exceptions import InvalidSku
from allocation.domain import services as domain_services
from allocation.domain.model.aggregates import Batch
from allocation.domain.model.value_objects import OrderLine
from allocation.domain.repositories import Repository


def is_valid_sku(sku: str, batches: list[Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repository: Repository, session) -> str:
    batches = repository.list()

    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid SKU {line.sku}")

    batch_ref = domain_services.allocate(line, batches)
    session.commit()

    return batch_ref
