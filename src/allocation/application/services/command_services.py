from allocation.application.exceptions import InvalidSku
from allocation.application.unit_of_work import AllocationViewUnitOfWork
from allocation.application.unit_of_work import ProductUnitOfWork
from allocation.domain import commands
from allocation.domain.models import AllocationView
from allocation.domain.models import Batch
from allocation.domain.models import OrderLine
from allocation.domain.models import Product


def is_valid_sku(sku: str, batches: list[Batch]) -> bool:
    return sku in {b.sku for b in batches}


def add_batch(command: commands.CreateBatch, uow: ProductUnitOfWork):
    with uow:
        product = uow.products.get(command.sku)
        if product is None:
            product = Product(command.sku, batches=[])
            uow.products.add(product)
        product.batches.append(Batch(command.ref, command.sku, command.qty, command.eta))
        uow.commit()


def allocate(command: commands.Allocate, uow: ProductUnitOfWork):
    line = OrderLine(command.order_id, command.sku, command.qty)

    with uow:
        product = uow.products.get(sku=line.sku)

        if product is None:
            raise InvalidSku(f"Invalid SKU {line.sku}")

        batch_ref = product.allocate(line)
        uow.commit()

    return batch_ref


def change_batch_quantity(command: commands.ChangeBatchQuantity, uow: ProductUnitOfWork):
    with uow:
        product = uow.products.get_by_batch_ref(batch_ref=command.ref)
        product.change_batch_quantity(ref=command.ref, qty=command.qty)
        uow.commit()


def add_allocation_view(command: commands.AddAllocationView, uow: AllocationViewUnitOfWork):
    with uow:
        uow.allocations_view.add(
            AllocationView(order_id=command.order_id, sku=command.sku, batch_ref=command.batch_ref)
        )
        uow.commit()
