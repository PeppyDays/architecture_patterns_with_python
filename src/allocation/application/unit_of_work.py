from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from allocation import configuration
from allocation.domain.repositories import ProductRepository
from allocation.infrastructure.repositories.repositories import ProductFakeRepository
from allocation.infrastructure.repositories.repositories import ProductSqlAlchemyRepository


class ProductUnitOfWork(ABC):
    products: ProductRepository

    def __enter__(self) -> ProductUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    def commit(self):
        self._commit_data()

    def rollback(self):
        self._rollback_data()

    @abstractmethod
    def _commit_data(self):
        raise NotImplementedError

    @abstractmethod
    def _rollback_data(self):
        raise NotImplementedError

    def collect_new_messages(self):
        for product in self.products.seen:
            while product.messages:
                yield product.messages.pop(0)


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

    def _commit_data(self):
        self.session.commit()

    def _rollback_data(self):
        self.session.rollback()


class ProductFakeUnitOfWork(ProductUnitOfWork):
    products: ProductFakeRepository
    is_committed: bool

    def __init__(self):
        self.products = ProductFakeRepository([])
        self.is_committed = False

    def _commit_data(self):
        self.is_committed = True

    def _rollback_data(self):
        pass
