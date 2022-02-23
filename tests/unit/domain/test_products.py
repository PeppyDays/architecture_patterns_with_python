from datetime import date

from allocation.domain import events
from allocation.domain.models import Batch
from allocation.domain.models import OrderLine
from allocation.domain.models import Product


def test_records_out_of_stock_event_if_cannot_allocate():
    batch = Batch("batch-1", "SMALL-FORK", 10, eta=date.today())
    product = Product("SMALL-FORK", [batch])
    product.allocate(OrderLine("order-1", "SMALL-FORK", 10))

    allocation = product.allocate(OrderLine("order-2", "SMALL-FORK", 1))

    assert product.messages[-1] == events.OutOfStock("SMALL-FORK")
    assert allocation is None
