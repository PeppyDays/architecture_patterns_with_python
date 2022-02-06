from abc import ABC
from abc import abstractmethod

from src.domain.model.aggregates import Batch


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, batch: Batch) -> str:
        raise NotImplementedError

    @abstractmethod
    def get(self, ref: str) -> Batch:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Batch]:
        raise NotImplementedError
