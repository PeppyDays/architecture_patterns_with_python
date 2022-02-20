from abc import ABC
from abc import abstractmethod
from typing import Optional

from allocation.domain.models import Product


class ProductRepository(ABC):
    seen: set[Product]

    def __init__(self):
        self.seen = set()

    def add(self, product: Product):
        self._add(product)
        self.seen.add(product)

    def get(self, sku: str) -> Product:
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    def get_by_batch_ref(self, batch_ref: str) -> Product:
        product = self._get_by_batch_ref(batch_ref)
        if product:
            self.seen.add(product)
        return product

    @abstractmethod
    def _add(self, product: Product):
        raise NotImplementedError

    @abstractmethod
    def _get(self, sku: str) -> Optional[Product]:
        raise NotImplementedError

    @abstractmethod
    def _get_by_batch_ref(self, batch_ref: str) -> Product:
        raise NotImplementedError
