import pytest

from allocation.application.exceptions import InvalidSku
from allocation.application.services import add_batch
from allocation.application.services import allocate
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

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([Batch(ref, sku, qty, eta)])


class FakeSession:
    is_committed: bool = False

    def commit(self):
        self.is_committed = True


def test_returns_allocation():
    repository = FakeRepository.for_batch(ref="b1", sku="COMPLICATED-LAMP", qty=100)
    result = allocate("o1", "COMPLICATED-LAMP", 10, repository, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    repository = FakeRepository.for_batch("b1", "AREALSKU", 100)

    with pytest.raises(InvalidSku, match="Invalid SKU NONEXISTENTSKU"):
        allocate("o1", "NONEXISTENTSKU", 10, repository, FakeSession())


def test_commit():
    repository = FakeRepository.for_batch("b1", "OMINOUS-MIRROR", 100)
    session = FakeSession()

    allocate("o1", "OMINOUS-MIRROR", 10, repository, session)
    assert session.is_committed


def test_add_batch():
    repository, session = FakeRepository([]), FakeSession()
    add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repository, session)

    assert repository.get("b1") is not None
    assert session.is_committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(InvalidSku, match="Invalid SKU NONEXISTENTSKU"):
        allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())
