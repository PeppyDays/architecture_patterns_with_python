from datetime import datetime

from flask import Flask
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import configuration
from allocation.application import services
from allocation.application.exceptions import InvalidSku
from allocation.domain.exceptions import OutOfStock
from allocation.infrastructure.repositories import sqlalchemy_orm
from allocation.infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository

sqlalchemy_orm.start_mappers()
get_session = sessionmaker(bind=create_engine(configuration.get_postgres_uri()))

app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repository = SqlAlchemyRepository(session)

    order_id = request.json["order_id"]
    sku = request.json["sku"]
    qty = request.json["qty"]

    try:
        batch_ref = services.allocate(order_id, sku, qty, repository=repository, session=session)
    except (OutOfStock, InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batch_ref": batch_ref}, 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    session = get_session()
    repository = SqlAlchemyRepository(session)
    eta = request.json["eta"]

    if eta:
        eta = datetime.fromisoformat(eta).date()

    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        repository, session
    )

    return "OK", 201
