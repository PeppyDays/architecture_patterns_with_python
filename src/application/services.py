from src.domain.exceptions import OutOfStock
from src.domain.model.aggregates import Batch
from src.domain.model.aggregates import OrderLine


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f"The SKU ${line.sku} in order ${line.order_id} cannot be allocated due to out of stock")

    batch.allocate(line)
    return batch.ref
