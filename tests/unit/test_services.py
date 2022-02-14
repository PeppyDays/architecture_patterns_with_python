import pytest

from allocation.application.exceptions import InvalidSku
from allocation.application.services import allocate
from allocation.domain.model.aggregates import Batch
from allocation.domain.model.value_objects import OrderLine
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


class FakeSession:
    is_committed: bool = False

    def commit(self):
        self.is_committed = True


def test_returns_allocation():
    line = OrderLine(order_id="o1", sku="COMPLICATED-LAMP", qty=10)
    batch = Batch(ref="b1", sku="COMPLICATED-LAMP", qty=100)
    repository = FakeRepository([batch])
    result = allocate(line, repository, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = Batch("b1", "AREALSKU", 100)
    repository = FakeRepository([batch])

    with pytest.raises(InvalidSku, match="Invalid SKU NONEXISTENTSKU"):
        allocate(line, repository, FakeSession())


def test_commit():
    line = OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = Batch("b1", "OMINOUS-MIRROR", 100)
    repository = FakeRepository([batch])
    session = FakeSession()

    allocate(line, repository, session)
    assert session.is_committed
