from typing import Callable
from typing import Type

from allocation.application import services
from allocation.application.unit_of_work import ProductUnitOfWork
from allocation.domain import events
from allocation.infrastructure.services import email


def handle(event: events.Event, uow: ProductUnitOfWork):
    results = []
    queue = [event]

    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow))
            queue.extend(uow.collect_new_events())

    return results


def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
        "stock@made.com",
        f"Out of stock for SKU {event.sku}"
    )


def add_batch(event: events.BatchCreated, uow: ProductUnitOfWork):
    services.add_batch(
        ref=event.ref,
        sku=event.sku,
        qty=event.qty,
        eta=event.eta,
        uow=uow,
    )


def allocate(event: events.AllocationRequired, uow: ProductUnitOfWork):
    return services.allocate(
        order_id=event.order_id,
        sku=event.sku,
        qty=event.qty,
        uow=uow,
    )


def change_batch_quantity(event: events.BatchQuantityChanged, uow: ProductUnitOfWork):
    services.change_batch_quantity(
        ref=event.ref,
        qty=event.qty,
        uow=uow,
    )


HANDLERS: dict[Type[events.Event], list[Callable]] = {
    events.OutOfStock: [send_out_of_stock_notification],
    events.BatchCreated: [add_batch],
    events.AllocationRequired: [allocate],
    events.BatchQuantityChanged: [change_batch_quantity],
}
