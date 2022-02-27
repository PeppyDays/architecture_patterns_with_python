from datetime import date

from allocation.application import message_bus
from allocation.application.services import query_services
from allocation.application.unit_of_work import AllocationViewSqlAlchemyUnitOfWork
from allocation.application.unit_of_work import ProductSqlAlchemyUnitOfWork
from allocation.domain import commands
from allocation.domain.models import AllocationView


def test_allocations_view(sqlite_session_factory):
    # works only when just a single aggregate exists
    # this test fails because event consumer does not know the session factory
    # so the default session factory (postgresql) is used

    uow = ProductSqlAlchemyUnitOfWork(sqlite_session_factory)

    message_bus.handle(commands.CreateBatch("sku1batch", "sku1", 50, None), uow)
    message_bus.handle(commands.CreateBatch("sku2batch", "sku2", 50, date.today()), uow)
    message_bus.handle(commands.Allocate("order1", "sku1", 20), uow)
    message_bus.handle(commands.Allocate("order1", "sku2", 20), uow)
    # add a spurious batch and order to make sure we're getting the right ones
    message_bus.handle(commands.CreateBatch("sku1batch-later", "sku1", 50, date.today()), uow)
    message_bus.handle(commands.Allocate("otherorder", "sku1", 30), uow)
    message_bus.handle(commands.Allocate("otherorder", "sku2", 10), uow)

    uow = AllocationViewSqlAlchemyUnitOfWork(sqlite_session_factory)
    result = query_services.get_allocations("order1", uow)

    assert result == [
        AllocationView("order1", "sku1", "sku1batch"),
        AllocationView("order1", "sku2", "sku2batch"),
    ]
