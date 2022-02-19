from allocation.domain.exceptions import OutOfStock
from allocation.domain.models import Batch
from allocation.domain.models import OrderLine


def allocate(line: OrderLine, batches: list[Batch]):
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
    except StopIteration:
        raise OutOfStock(f"Out of stock for SKU {line.sku}")

    return batch.ref
