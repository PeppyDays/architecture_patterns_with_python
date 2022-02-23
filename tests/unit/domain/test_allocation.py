from datetime import date
from datetime import timedelta

from allocation.domain import events
from allocation.domain.models import Batch
from allocation.domain.models import OrderLine
from allocation.domain.models import Product


def test_prefers_current_stock_to_shipment():
    product = Product(
        "RETRO-CLOCK",
        [
            Batch(ref="in-stock-batch", sku="RETRO-CLOCK", qty=100),
            Batch(
                ref="in-stock-batch",
                sku="RETRO-CLOCK",
                qty=100,
                eta=date.today() + timedelta(days=1),
            )
        ]
    )
    line = OrderLine(order_id="order-1", sku="RETRO-CLOCK", qty=10)

    allocated_batch_ref = product.allocate(line)

    assert allocated_batch_ref == "in-stock-batch"
    assert product.batches[0].available_qty == 90
    assert product.batches[1].available_qty == 100


def test_prefer_earlier_batch():
    earliest_batch = Batch(ref="earliest-batch", sku="MINIMALIST_SPOON", qty=100, eta=date.today())
    earlier_batch = Batch(
        ref="earlier-batch",
        sku="MINIMALIST_SPOON",
        qty=100,
        eta=date.today() + timedelta(days=1),
    )
    later_batch = Batch(
        ref="later-batch",
        sku="MINIMALIST_SPOON",
        qty=100,
        eta=date.today() + timedelta(days=7),
    )
    product = Product(
        "MINIMALIST_SPOON",
        [earliest_batch, earlier_batch, later_batch]
    )
    line = OrderLine(order_id="order-1", sku="MINIMALIST_SPOON", qty=10)

    allocated_batch_ref = product.allocate(line)

    assert allocated_batch_ref == earliest_batch.ref
    assert earliest_batch.available_qty == 90
    assert earlier_batch.available_qty == 100
    assert later_batch.available_qty == 100


def test_emits_out_of_stock_event_if_cannot_allocate():
    product = Product("SMALL-FORK", [Batch(ref="batch-1", sku="SMALL-FORK", qty=10)])
    line_1 = OrderLine(order_id="order-1", sku="SMALL-FORK", qty=10)
    product.allocate(line_1)

    line_2 = OrderLine(order_id="order-2", sku="SMALL-FORK", qty=1)
    product.allocate(line_2)

    assert events.OutOfStock(sku="SMALL-FORK") in product.messages
