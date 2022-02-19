import pytest

from allocation.application.exceptions import InvalidSku
from allocation.application.services import add_batch
from allocation.application.services import allocate
from allocation.application.unit_of_work import UnitOfWork
from allocation.domain.models import Batch
from allocation.domain.repositories import Repository


class FakeRepository(Repository):
    _batches: set[Batch]

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, ref):
        return next(b for b in self._batches if b.ref == ref)

    def list(self):
        return list(self._batches)


class FakeUnitOfWork(UnitOfWork):
    batches: FakeRepository
    is_committed: bool

    def __init__(self):
        self.batches = FakeRepository([])
        self.is_committed = False

    def commit(self):
        self.is_committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()
    add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("b1") is not None
    assert uow.is_committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(InvalidSku, match="Invalid SKU NONEXISTENTSKU"):
        allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.is_committed
