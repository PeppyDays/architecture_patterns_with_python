import pytest
import requests

from allocation import configuration
from api_client import post_to_add_batch
from random_refs import random_batch_ref
from random_refs import random_order_id
from random_refs import random_sku


@pytest.mark.usefixtures("postgres_db")
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


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_order_id()
    data = {"order_id": order_id, "sku": unknown_sku, "qty": 20}
    url = configuration.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid SKU {unknown_sku}"
