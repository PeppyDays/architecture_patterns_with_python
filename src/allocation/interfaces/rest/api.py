from flask import Flask
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import configuration
from allocation.application.services import allocate
from allocation.domain.exceptions import OutOfStock
from allocation.domain.model.aggregates import Batch
from allocation.domain.model.aggregates import OrderLine
from allocation.infrastructure.repositories import sqlalchemy_orm
from allocation.infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository

sqlalchemy_orm.start_mappers()
get_session = sessionmaker(bind=create_engine(configuration.get_postgres_uri()))
app = Flask(__name__)


def is_valid_sku(sku: str, batches: list[Batch]) -> bool:
    return sku in {b.sku for b in batches}


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    batches = SqlAlchemyRepository(session).list()
    line = OrderLine(
        order_id=request.json["order_id"],
        sku=request.json["sku"],
        qty=request.json["qty"],
    )

    if not is_valid_sku(line.sku, batches):
        return {"message": f"Invalid SKU {line.sku}"}, 400

    try:
        batch_ref = allocate(line=line, batches=batches)
    except OutOfStock as e:
        return {"message": str(e)}, 400

    session.commit()

    return {"batch_ref": batch_ref}, 201
