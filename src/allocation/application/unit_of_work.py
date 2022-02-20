from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from allocation import configuration
from allocation.domain.repositories import ProductRepository
from allocation.infrastructure.repositories.sqlalchemy_repository import ProductSqlAlchemyRepository


class ProductUnitOfWork(ABC):
    products: ProductRepository

    def __enter__(self) -> ProductUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        configuration.get_postgres_uri(),
        isolation_level="REPEATABLE READ",
    )
)


class ProductSqlAlchemyUnitOfWork(ProductUnitOfWork):
    session: Session
    products: ProductSqlAlchemyRepository

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self) -> ProductSqlAlchemyUnitOfWork:
        self.session = self.session_factory()
        self.products = ProductSqlAlchemyRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
