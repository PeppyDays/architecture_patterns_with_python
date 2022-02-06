from datetime import date
from datetime import timedelta

import pytest

from src.application.services import allocate
from src.domain.exceptions import OutOfStock
from src.domain.model.aggregates import Batch
from src.domain.model.aggregates import OrderLine


def test_prefers_current_stock_to_shipment():
    in_stock_batch = Batch(ref="in-stock-batch", sku="RETRO-CLOCK", qty=100)
    shipment_batch = Batch(
        ref="in-stock-batch",
        sku="RETRO-CLOCK",
        qty=100,
        eta=date.today() + timedelta(days=1),
    )
    line = OrderLine(order_id="order-1", sku="RETRO-CLOCK", qty=10)

    allocated_batch_ref = allocate(line, [in_stock_batch, shipment_batch])

    assert allocated_batch_ref == in_stock_batch.ref
    assert in_stock_batch.available_qty == 90
    assert shipment_batch.available_qty == 100


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
    line = OrderLine(order_id="order-1", sku="MINIMALIST_SPOON", qty=10)

    allocated_batch_ref = allocate(line, [earliest_batch, earlier_batch, later_batch])

    assert allocated_batch_ref == earliest_batch.ref
    assert earliest_batch.available_qty == 90
    assert earlier_batch.available_qty == 100
    assert later_batch.available_qty == 100


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch(ref="batch-1", sku="SMALL-FORK", qty=10)
    line_1 = OrderLine(order_id="order-1", sku="SMALL-FORK", qty=10)
    allocate(line_1, [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        line_2 = OrderLine(order_id="order-2", sku="SMALL-FORK", qty=1)
        allocate(line_2, [batch])
