from datetime import date
from unittest import mock

import pytest

from allocation.application import message_bus
from allocation.application.exceptions import InvalidSku
from allocation.application.unit_of_work import ProductFakeUnitOfWork
from allocation.domain import commands


class TestAddBatch:
    def test_for_new_product(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("b1", "CRUNCHY-ARMCHAIR", 100, None), uow)
        assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert uow.is_committed

    def test_for_existing_product(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("b1", "GARISH-RUG", 100, None), uow)
        message_bus.handle(commands.CreateBatch("b2", "GARISH-RUG", 99, None), uow)
        assert "b2" in [b.ref for b in uow.products.get("GARISH-RUG").batches]


class TestAllocate:
    def test_allocates(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("batch1", "COMPLICATED-LAMP", 100, None), uow)
        results = message_bus.handle(commands.Allocate("o1", "COMPLICATED-LAMP", 10), uow)
        assert results.pop(0) == "batch1"
        [batch] = uow.products.get("COMPLICATED-LAMP").batches
        assert batch.available_qty == 90

    def test_errors_for_invalid_sku(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("b1", "AREALSKU", 100, None), uow)

        with pytest.raises(InvalidSku, match="Invalid SKU NONEXISTENTSKU"):
            message_bus.handle(commands.Allocate("o1", "NONEXISTENTSKU", 10), uow)

    def test_commits(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("b1", "OMINOUS-MIRROR", 100, None), uow)
        message_bus.handle(commands.Allocate("o1", "OMINOUS-MIRROR", 10), uow)
        assert uow.is_committed

    def test_sends_email_on_out_of_stock_error(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("b1", "POPULAR-CURTAINS", 9, None), uow)

        with mock.patch("allocation.infrastructure.services.email.send") as mock_send_mail:
            message_bus.handle(commands.Allocate("o1", "POPULAR-CURTAINS", 10), uow)
            assert mock_send_mail.call_args == mock.call("stock@made.com", f"Out of stock for SKU POPULAR-CURTAINS")


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        uow = ProductFakeUnitOfWork()
        message_bus.handle(commands.CreateBatch("batch-1", "ADORABLE-SETTEE", 100), uow)
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_qty == 100

        message_bus.handle(commands.ChangeBatchQuantity("batch-1", 50), uow)
        assert batch.available_qty == 50

    def test_reallocates_if_needed(self):
        uow = ProductFakeUnitOfWork()
        event_history = [
            commands.CreateBatch("batch-1", "INDIFFERENT-TABLE", 50, None),
            commands.CreateBatch("batch-2", "INDIFFERENT-TABLE", 50, date.today()),
            commands.Allocate("order-1", "INDIFFERENT-TABLE", 20),
            commands.Allocate("order-2", "INDIFFERENT-TABLE", 20),
        ]
        for event in event_history:
            message_bus.handle(event, uow)

        [batch_1, batch_2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch_1.available_qty == 10
        assert batch_2.available_qty == 50

        message_bus.handle(commands.ChangeBatchQuantity("batch-1", 25), uow)
        assert batch_1.available_qty == 5
        assert batch_2.available_qty == 30
