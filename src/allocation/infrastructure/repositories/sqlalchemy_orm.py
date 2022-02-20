from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship

from allocation.domain.models import Batch
from allocation.domain.models import OrderLine
from allocation.domain.models import Product

mapper_registry = registry()

order_lines = Table(
    "order_lines",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_id", String(255)),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
)

products = Table(
    "products",
    mapper_registry.metadata,
    Column("sku", String(255), primary_key=True),
    Column("version", Integer, nullable=False, server_default="0"),
)

batches = Table(
    "batches",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ref", String(255)),
    Column("sku", ForeignKey("products.sku")),
    Column("eta", Date, nullable=True),
    Column("purchased_qty", Integer, nullable=False),
)

allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_line_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(OrderLine, order_lines)
    batches_mapper = mapper_registry.map_imperatively(
        Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
    mapper_registry.map_imperatively(
        Product,
        products,
        properties={"batches": relationship(batches_mapper)},
    )
