from allocation.application.unit_of_work import ProductUnitOfWork
from allocation.domain import events
from allocation.infrastructure.services import email


def send_out_of_stock_notification(event: events.OutOfStock, uow: ProductUnitOfWork):
    email.send(
        "stock@made.com",
        f"Out of stock for SKU {event.sku}"
    )
