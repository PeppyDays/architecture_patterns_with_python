import threading
import time
import traceback
import uuid

import pytest
from allocation.application.unit_of_work import ProductSqlAlchemyUnitOfWork
from allocation.domain.models import OrderLine


def insert_batch(session, ref, sku, qty, eta):
    session.execute("INSERT INTO products (sku) VALUES (:sku)", dict(sku=sku))
    session.execute(
        "INSERT INTO batches (ref, sku, purchased_qty, eta) VALUES (:ref, :sku, :qty, :eta)",
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batch_ref(session, order_id, sku):
    [[order_line_id]] = session.execute(
        "SELECT id FROM order_lines WHERE order_id=:order_id AND sku=:sku",
        dict(order_id=order_id, sku=sku),
    )
    [[batch_ref]] = session.execute(
        "SELECT b.ref FROM allocations JOIN batches AS b ON batch_id = b.id WHERE order_line_id=:order_line_id",
        dict(order_line_id=order_line_id),
    )
    return batch_ref


def try_to_allocate(order_id, sku, exceptions):
    line = OrderLine(order_id, sku, 10)
    try:
        with ProductSqlAlchemyUnitOfWork() as uow:
            product = uow.products.get(sku=sku)
            product.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        print(traceback.format_exc())
        exceptions.append(e)


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batch_ref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_order_id(name=""):
    return f"order-{name}-{random_suffix()}"


def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory):
    sku, batch = random_sku(), random_batch_ref()
    session = postgres_session_factory()
    insert_batch(session, batch, sku, 100, eta=None)
    session.commit()

    order_1, order_2 = random_order_id("1"), random_order_id("2")
    exceptions = []
    thread1 = threading.Thread(target=lambda: try_to_allocate(order_1, sku, exceptions))
    thread2 = threading.Thread(target=lambda: try_to_allocate(order_2, sku, exceptions))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    [[version]] = session.execute(
        "SELECT version FROM products WHERE sku=:sku",
        dict(sku=sku),
    )
    assert version == 1
    [exception] = exceptions
    assert "could not serialize access due to concurrent update" in str(exception)

    orders = session.execute(
        "SELECT order_id FROM allocations"
        " JOIN batches ON allocations.batch_id = batches.id"
        " JOIN order_lines ON allocations.order_line_id = order_lines.id"
        " WHERE order_lines.sku=:sku",
        dict(sku=sku),
    )
    assert orders.rowcount == 1
    with ProductSqlAlchemyUnitOfWork() as uow:
        uow.session.execute("select 1")


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    session.commit()

    uow = ProductSqlAlchemyUnitOfWork(session_factory)
    with uow:
        product = uow.products.get(sku="HIPSTER-WORKBENCH")
        line = OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        product.allocate(line)
        uow.commit()

    batch_ref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
    assert batch_ref == "batch1"


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = ProductSqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = ProductSqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []
