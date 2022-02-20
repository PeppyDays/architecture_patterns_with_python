from datetime import date
from typing import Optional

from allocation.application.exceptions import InvalidSku
from allocation.application.unit_of_work import ProductUnitOfWork
from allocation.domain.models import Batch
from allocation.domain.models import OrderLine
from allocation.domain.models import Product


def is_valid_sku(sku: str, batches: list[Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int, uow: ProductUnitOfWork) -> str:
    line = OrderLine(order_id, sku, qty)

    with uow:
        product = uow.products.get(sku=line.sku)

        if product is None:
            raise InvalidSku(f"Invalid SKU {sku}")

        batch_ref = product.allocate(line)
        uow.commit()

    return batch_ref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], uow: ProductUnitOfWork):
    with uow:
        product = uow.products.get(sku)
        if product is None:
            product = Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(Batch(ref, sku, qty, eta))
        uow.commit()


def change_batch_quantity(ref: str, qty: int, uow: ProductUnitOfWork):
    with uow:
        product = uow.products.get_by_batch_ref(batch_ref=ref)
        product.change_batch_quantity(ref=ref, qty=qty)
        uow.commit()
