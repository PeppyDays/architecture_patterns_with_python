from typing import Optional

from sqlalchemy.orm import Session

from allocation.domain.models import Batch
from allocation.domain.models import Product
from allocation.domain.repositories import ProductRepository
from allocation.infrastructure.repositories import orm


class ProductSqlAlchemyRepository(ProductRepository):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def _add(self, product: Product):
        self.session.add(product)

    def _get(self, sku: str) -> Optional[Product]:
        return self.session.query(Product).filter_by(sku=sku).first()
        # return self.session.query(Product).filter_by(sku=sku).with_for_update().first()

    def _get_by_batch_ref(self, batch_ref: str) -> Product:
        return (
            self.session
                .query(Product)
                .join(Batch)
                .filter(orm.batches.c.ref == batch_ref)
                .first()
        )


class ProductFakeRepository(ProductRepository):
    _products: set[Product]

    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku) -> Optional[Product]:
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batch_ref(self, batch_ref: str) -> Product:
        return next((p for p in self._products for b in p.batches if b.ref == batch_ref), None)
