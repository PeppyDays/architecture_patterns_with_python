import json
import logging
from dataclasses import asdict

import redis

from allocation import configuration
from allocation.domain import events

logger = logging.getLogger("__name__")

r = redis.Redis(**configuration.get_redis_host_and_port())


def publish(channel, event: events.Event):
    logger.debug(f"publishing: channel={channel}, event={event}")
    print(f"publishing: channel={channel}, event={event}")
    r.publish(channel, json.dumps(asdict(event)))
