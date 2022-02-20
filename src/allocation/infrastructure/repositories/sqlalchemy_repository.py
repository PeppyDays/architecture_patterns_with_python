from sqlalchemy.orm import Session

from allocation.domain.models import Product
from allocation.domain.repositories import ProductRepository


class ProductSqlAlchemyRepository(ProductRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, product: Product):
        self.session.add(product)

    def get(self, sku: str) -> Product:
        return self.session.query(Product).filter_by(sku=sku).first()
        # return self.session.query(Product).filter_by(sku=sku).with_for_update().first()
