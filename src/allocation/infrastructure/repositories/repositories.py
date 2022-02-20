from sqlalchemy.orm import Session

from allocation.domain.models import Product
from allocation.domain.repositories import ProductRepository


class ProductSqlAlchemyRepository(ProductRepository):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def _add(self, product: Product):
        self.session.add(product)

    def _get(self, sku: str) -> Product:
        return self.session.query(Product).filter_by(sku=sku).first()
        # return self.session.query(Product).filter_by(sku=sku).with_for_update().first()


class ProductFakeRepository(ProductRepository):
    _products: set[Product]

    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        try:
            return next(p for p in self._products if p.sku == sku)
        except StopIteration:
            return None
