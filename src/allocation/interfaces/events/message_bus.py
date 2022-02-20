from typing import Callable
from typing import Type

from allocation.domain import events
from allocation.infrastructure.services import email


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
        "stock@made.com",
        f"Out of stock for SKU {event.sku}"
    )


HANDLERS: dict[Type[events.Event], list[Callable]] = {
    events.OutOfStock: [send_out_of_stock_notification],
}
