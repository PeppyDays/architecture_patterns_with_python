import json
import logging
from typing import Callable

import redis

from allocation import configuration
from allocation.application import message_bus
from allocation.application.unit_of_work import AllocationViewSqlAlchemyUnitOfWork
from allocation.application.unit_of_work import ProductSqlAlchemyUnitOfWork
from allocation.domain import commands
from allocation.infrastructure.repositories import orm

logger = logging.getLogger(__name__)
r = redis.Redis(**configuration.get_redis_host_and_port())


def main():
    orm.start_mappers()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity", "line_allocated")

    for message in pubsub.listen():
        print(message)
        try:
            channel = message["channel"].decode()
            handler = CHANNEL_HANDLERS[channel]
            handler(message)
        except Exception as e:
            print(e)


def handle_change_batch_quantity(message):
    logger.debug(f"handling {message}")
    data = json.loads(message["data"])
    command = commands.ChangeBatchQuantity(ref=data["batch_ref"], qty=data["qty"])
    message_bus.handle(command, uow=ProductSqlAlchemyUnitOfWork())


def handle_allocated(message):
    logger.debug(f"handling {message}")
    data = json.loads(message["data"])
    command = commands.AddAllocationView(order_id=data["order_id"], sku=data["sku"], batch_ref=data["batch_ref"])
    message_bus.handle(command, uow=AllocationViewSqlAlchemyUnitOfWork())


CHANNEL_HANDLERS: dict[str, Callable] = {
    "line_allocated": handle_allocated,
    "change_batch_quantity": handle_change_batch_quantity,
}


if __name__ == "__main__":
    main()
