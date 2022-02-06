from datetime import date

from src.domain.model.aggregates import Batch
from src.domain.model.aggregates import OrderLine


def make_batch_and_line(*, sku, batch_qty, line_qty):
    return (
        Batch(ref="batch-001", sku=sku, qty=batch_qty, eta=date.today()),
        OrderLine(order_id="order-123", sku=sku, qty=line_qty),
    )


def test_allocation_should_reduce_available_quantity():
    batch, line = make_batch_and_line(sku="SMALL-TABLE", batch_qty=20, line_qty=2)
    batch.allocate(line)
    assert batch.available_qty == 18


def test_can_allocate_when_available_quantity_greater_than_line_quantity():
    batch, line = make_batch_and_line(sku="BLUE-CUSION", batch_qty=100, line_qty=2)
    assert batch.can_allocate(line)


def test_cannot_allocate_when_available_quantity_less_than_line_quantity():
    batch, line = make_batch_and_line(sku="BLUE-CUSION", batch_qty=1, line_qty=2)
    assert not batch.can_allocate(line)


def test_can_allocate_when_available_quantity_equal_to_line_quantity():
    batch, order_line = make_batch_and_line(sku="BLUE-CUSION", batch_qty=2, line_qty=2)
    assert batch.can_allocate(order_line)


def test_cannot_allocate_if_sku_do_not_match():
    batch = Batch(ref="batch-001", sku="UNCOMFORTABLE-CHAIR", qty=20)
    line = OrderLine(order_id="order-ref", sku="COMFORTABLE-CHAIR", qty=2)
    assert not batch.can_allocate(line)


def test_can_only_deallocate_allocated_lines():
    batch, line = make_batch_and_line(sku="DECORATIVE-TRINKET", batch_qty=20, line_qty=2)
    batch.deallocate(line)
    assert batch.available_qty == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line(sku="ANGULAR-DESK", batch_qty=20, line_qty=2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_qty == 18
