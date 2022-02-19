import time
from pathlib import Path

import pytest
import requests
from psycopg2 import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers
from sqlalchemy.orm import sessionmaker

from allocation import configuration
from allocation.infrastructure.repositories.sqlalchemy_orm import mapper_registry
from allocation.infrastructure.repositories.sqlalchemy_orm import start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(configuration.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/allocation/interfaces/rest/api.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = configuration.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def add_stock(postgres_session):
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            postgres_session.execute(
                "INSERT INTO batches (ref, sku, purchased_qty, eta)" "VALUES (:ref, :sku, :qty, :eta)",
                dict(ref=ref, sku=sku, qty=qty, eta=eta),
            )
            [[batch_id]] = postgres_session.execute(
                "SELECT id FROM batches WHERE ref = :ref AND sku = :sku",
                dict(ref=ref, sku=sku),
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        postgres_session.commit()

    yield _add_stock

    for batch_id in batches_added:
        postgres_session.execute(
            "DELETE FROM allocations WHERE batch_id = :batch_id",
            dict(batch_id=batch_id),
        )
        postgres_session.execute(
            "DELETE FROM batches WHERE id = :batch_id",
            dict(batch_id=batch_id),
        )
    for sku in skus_added:
        postgres_session.execute(
            "DELETE FROM order_lines WHERE sku = :sku",
            dict(sku=sku),
        )
        postgres_session.commit()
