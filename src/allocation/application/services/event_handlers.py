from allocation.domain import events
from allocation.infrastructure.brokers import publisher
from allocation.infrastructure.services import email


def send_out_of_stock_notification(event: events.OutOfStock, _):
    email.send("stock@made.com", f"Out of stock for SKU {event.sku}")


def publish_allocated_event(event: events.Allocated, _):
    publisher.publish("line_allocated", event)
