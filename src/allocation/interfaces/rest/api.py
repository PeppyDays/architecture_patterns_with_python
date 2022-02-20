from datetime import datetime

from flask import Flask
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import configuration
from allocation.application import services
from allocation.application.exceptions import InvalidSku
from allocation.application.unit_of_work import ProductSqlAlchemyUnitOfWork
from allocation.domain import events
from allocation.domain.exceptions import OutOfStock
from allocation.infrastructure.repositories import orm
from allocation.interfaces.events import message_bus

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(configuration.get_postgres_uri()))

app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        event = events.AllocationRequired(
            request.json["order_id"],
            request.json["sku"],
            request.json["qty"],
        )
        results = message_bus.handle(event, ProductSqlAlchemyUnitOfWork())
    except (OutOfStock, InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batch_ref": results[0]}, 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]

    if eta:
        eta = datetime.fromisoformat(eta).date()

    event = events.BatchCreated(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
    )
    message_bus.handle(event, ProductSqlAlchemyUnitOfWork())

    return "OK", 201
