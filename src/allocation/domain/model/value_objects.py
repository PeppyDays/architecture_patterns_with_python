from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int
