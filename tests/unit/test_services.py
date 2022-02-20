import pytest

from allocation.application.exceptions import InvalidSku
from allocation.application.services import add_batch
from allocation.application.services import allocate
from allocation.application.unit_of_work import ProductUnitOfWork
from allocation.domain.models import Product
from allocation.domain.repositories import ProductRepository


class ProductFakeRepository(ProductRepository):
    _products: set[Product]

    def __init__(self, products):
        self._products = set(products)

    def add(self, product):
        self._products.add(product)

    def get(self, sku):
        try:
            return next(p for p in self._products if p.sku == sku)
        except StopIteration:
            return None


class ProductFakeUnitOfWork(ProductUnitOfWork):
    products: ProductFakeRepository
    is_committed: bool

    def __init__(self):
        self.products = ProductFakeRepository([])
        self.is_committed = False

    def commit(self):
        self.is_committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = ProductFakeUnitOfWork()
    add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.is_committed


def test_allocate_returns_allocation():
    uow = ProductFakeUnitOfWork()
    add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = ProductFakeUnitOfWork()
    add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(InvalidSku, match="Invalid SKU NONEXISTENTSKU"):
        allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_allocate_commits():
    uow = ProductFakeUnitOfWork()
    add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.is_committed
