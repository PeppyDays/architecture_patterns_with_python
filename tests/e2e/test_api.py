import uuid

import pytest
import requests

from allocation import configuration


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, other_sku = random_sku(), random_sku("other")
    early_batch = random_batch_ref("1")
    later_batch = random_batch_ref("2")
    other_batch = random_batch_ref("3")
    post_to_add_batch(later_batch, sku, 100, "2011-01-02")
    post_to_add_batch(early_batch, sku, 100, "2011-01-01")
    post_to_add_batch(other_batch, other_sku, 100, None)
    data = {"order_id": random_order_id(), "sku": sku, "qty": 3}

    url = configuration.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batch_ref"] == early_batch


@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_order_id()
    data = {"order_id": order_id, "sku": unknown_sku, "qty": 20}
    url = configuration.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid SKU {unknown_sku}"


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batch_ref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_order_id(name=""):
    return f"order-{name}-{random_suffix()}"


def post_to_add_batch(ref, sku, qty, eta):
    url = configuration.get_api_url()
    r = requests.post(f"{url}/add_batch", json={"ref": ref, "sku": sku, "qty": qty, "eta": eta})
    assert r.status_code == 201
