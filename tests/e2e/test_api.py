import pytest
import requests

from allocation import configuration
from allocation.application.services.query_services import get_allocations
from api_client import post_to_add_batch
from random_refs import random_batch_ref
from random_refs import random_order_id
from random_refs import random_sku
from tests.e2e.api_client import post_to_allocate


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_order_id()
    data = {"order_id": order_id, "sku": unknown_sku, "qty": 20}
    url = configuration.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid SKU {unknown_sku}"


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_202_and_batch_is_allocated():
    order_id = random_order_id()
    sku, other_sku = random_sku(), random_sku("other")
    early_batch = random_batch_ref("1")
    later_batch = random_batch_ref("2")
    other_batch = random_batch_ref("3")
    post_to_add_batch(later_batch, sku, 100, "2011-01-02")
    post_to_add_batch(early_batch, sku, 100, "2011-01-01")
    post_to_add_batch(other_batch, other_sku, 100, None)

    r = post_to_allocate(order_id, sku, qty=3)
    assert r.status_code == 202

    r = get_allocations(order_id)
    assert r.ok
    assert r.json() == [
        {"sku": sku, "batch_ref": early_batch},
    ]


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_order_id()
    r = api_client.post_to_allocate(orderid, unknown_sku, qty=20, expect_success=False)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"

    r = api_client.get_allocation(orderid)
    assert r.status_code == 404
