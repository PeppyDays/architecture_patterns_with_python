from allocation.application.unit_of_work import ProductUnitOfWork
from allocation.domain import events
from allocation.infrastructure.brokers import publisher
from allocation.infrastructure.services import email


def send_out_of_stock_notification(event: events.OutOfStock, uow: ProductUnitOfWork):
    email.send(
        "stock@made.com",
        f"Out of stock for SKU {event.sku}"
    )


def publish_allocated_event(event: events.Allocated, uow: ProductUnitOfWork):
    publisher.publish("line_allocated", event)
