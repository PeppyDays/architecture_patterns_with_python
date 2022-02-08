from abc import ABC
from abc import abstractmethod

from allocation.domain.model.aggregates import Batch


class Repository(ABC):
    @abstractmethod
    def add(self, batch: Batch) -> str:
        raise NotImplementedError

    @abstractmethod
    def get(self, ref: str) -> Batch:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Batch]:
        raise NotImplementedError
