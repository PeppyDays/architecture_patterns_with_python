from datetime import date

from allocation.application.unit_of_work import ProductFakeUnitOfWork
from allocation.domain import events
from allocation.interfaces.events import message_bus


class TestAddBatch:
    def test_for_new_product(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(
            events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None),
            uow
        )
        assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert uow.is_committed


class TestAllocate:
    def test_returns_allocation(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(
            events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None),
            uow
        )
        results = message_bus.handle(
            events.AllocationRequired("o1", "COMPLICATED-LAMP", 10),
            uow
        )
        assert results.pop(0) == "batch1"


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(
            events.BatchCreated("batch-1", "ADORABLE-SETTEE", 100),
            uow
        )
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_qty == 100

        message_bus.handle(
            events.BatchQuantityChanged("batch-1", 50),
            uow
        )
        assert batch.available_qty == 50

    def test_reallocates_if_needed(self):
        uow = ProductFakeUnitOfWork()
        event_history = [
            events.BatchCreated("batch-1", "INDIFFERENT-TABLE", 50, None),
            events.BatchCreated("batch-2", "INDIFFERENT-TABLE", 50, date.today()),
            events.AllocationRequired("order-1", "INDIFFERENT-TABLE", 20),
            events.AllocationRequired("order-2", "INDIFFERENT-TABLE", 20),
        ]
        for event in event_history:
            message_bus.handle(event, uow)

        [batch_1, batch_2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch_1.available_qty == 10
        assert batch_2.available_qty == 50

        message_bus.handle(
            events.BatchQuantityChanged("batch-1", 25),
            uow
        )
        assert batch_1.available_qty == 5
        assert batch_2.available_qty == 30
