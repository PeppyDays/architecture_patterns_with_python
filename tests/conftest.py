import time
from pathlib import Path

import pytest
import redis
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers
from sqlalchemy.orm import sessionmaker
from tenacity import retry
from tenacity import stop_after_delay

from allocation import configuration
from allocation.infrastructure.repositories.orm import mapper_registry
from allocation.infrastructure.repositories.orm import start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session_factory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def sqlite_session(sqlite_session_factory):
    return sqlite_session_factory()


@pytest.fixture
def session_factory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def session(session_factory):
    return session_factory()


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(configuration.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    mapper_registry.metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)
    clear_mappers()


@pytest.fixture
def postgres_session(postgres_session_factory):
    return postgres_session_factory()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/allocation/interfaces/rest/api.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@retry(stop=stop_after_delay(10))
def wait_for_postgres_to_come_up(engine):
    return engine.connect()


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
    return requests.get(configuration.get_api_url())


@retry(stop=stop_after_delay(10))
def wait_for_redis_to_come_up():
    r = redis.Redis(**configuration.get_redis_host_and_port())
    return r.ping()
