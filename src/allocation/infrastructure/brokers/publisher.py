import json
import logging

import redis

from allocation import configuration
from allocation.domain import events

logger = logging.getLogger("__name__")

r = redis.Redis(**configuration.get_redis_host_and_port())


def publish(channel, event: events.Event):
    logger.debug("publishing: channel=%s, event=%s", channel, event)
    r.publish(channel, json.dumps(asdict(event)))
