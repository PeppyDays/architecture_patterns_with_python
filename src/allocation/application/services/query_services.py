import copy

from allocation.application.unit_of_work import AllocationViewUnitOfWork


def get_allocations(order_id: str, uow: AllocationViewUnitOfWork):
    with uow:
        results = copy.deepcopy(uow.allocations_view.get_by_order_id(order_id))

    return results
