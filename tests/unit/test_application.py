from allocation.application.services import allocate
from allocation.domain.model.aggregates import Batch
from allocation.domain.model.aggregates import OrderLine
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
