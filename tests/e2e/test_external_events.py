import json

from tenacity import Retrying
from tenacity import stop_after_delay

import api_client
import redis_client
from random_refs import random_batch_ref
from random_refs import random_order_id
from random_refs import random_sku


def test_change_batch_quantity_leading_to_reallocation():
    # start with two batches and an order allocated to one of them
    order_id, sku = random_order_id(), random_sku()
    earlier_batch, later_batch = (
        random_batch_ref("old"),
        random_batch_ref("new"),
    )
    api_client.post_to_add_batch(earlier_batch, sku, qty=10, eta="2011-01-01")
    api_client.post_to_add_batch(later_batch, sku, qty=10, eta="2011-01-02")
    response = api_client.post_to_allocate(order_id, sku, 10)
    assert response.json()["batch_ref"] == earlier_batch

    subscription = redis_client.subscribe_to("line_allocated")

    # change quantity on allocated batch, so it's less than our order
    redis_client.publish_message("change_batch_quantity", {"batch_ref": earlier_batch, "qty": 5})

    # wait until we see a message saying the order has been reallocated
    messages = []
    for attempt in Retrying(stop=stop_after_delay(3), reraise=True):
        with attempt:
            message = subscription.get_message(timeout=1)
            if message:
                messages.append(message)
                print(message)
            data = json.loads(messages[-1]["data"])
            assert data["order_id"] == order_id
            assert data["batch_ref"] == later_batch
