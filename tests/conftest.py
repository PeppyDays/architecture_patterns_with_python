import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers
from sqlalchemy.orm import sessionmaker

from src.infrastructure.repositories.sqlalchemy_orm import mapper_registry
from src.infrastructure.repositories.sqlalchemy_orm import start_mappers


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
