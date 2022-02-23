import json
import logging

import redis

from allocation import configuration
from allocation.application import message_bus
from allocation.application.unit_of_work import ProductSqlAlchemyUnitOfWork
from allocation.domain import commands
from allocation.infrastructure.repositories import orm

logger = logging.getLogger(__name__)
r = redis.Redis(**configuration.get_redis_host_and_port())


def main():
    orm.start_mappers()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("change_batch_quantity")

    for m in pubsub.listen():
        handle_change_batch_quantity(m)


def handle_change_batch_quantity(m):
    logger.debug("handling %s", m)
    data = json.loads(m["data"])
    cmd = commands.ChangeBatchQuantity(ref=data["batch_ref"], qty=data["qty"])
    message_bus.handle(cmd, uow=ProductSqlAlchemyUnitOfWork())


if __name__ == "__main__":
    main()
