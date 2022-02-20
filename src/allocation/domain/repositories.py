from abc import ABC
from abc import abstractmethod

from allocation.domain.models import Product


class ProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product):
        raise NotImplementedError

    @abstractmethod
    def get(self, sku: str) -> Product:
        raise NotImplementedError
