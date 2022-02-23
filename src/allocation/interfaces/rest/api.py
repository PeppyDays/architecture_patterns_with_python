from datetime import datetime

from flask import Flask
from flask import request

from allocation.application import message_bus
from allocation.application.exceptions import InvalidSku
from allocation.application.unit_of_work import ProductSqlAlchemyUnitOfWork
from allocation.domain import commands
from allocation.infrastructure.repositories import orm

orm.start_mappers()
app = Flask(__name__)


@app.route("/add_batch", methods=["POST"])
def add_batch():
    eta = request.json["eta"]
    if eta:
        eta = datetime.fromisoformat(eta).date()

    command = commands.CreateBatch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
    )
    message_bus.handle(command, ProductSqlAlchemyUnitOfWork())
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate():
    try:
        command = commands.Allocate(
            request.json["order_id"],
            request.json["sku"],
            request.json["qty"],
        )
        results = message_bus.handle(command, ProductSqlAlchemyUnitOfWork())
        batch_ref = results[0]
    except InvalidSku as e:
        return {"message": str(e)}, 400

    return {"batch_ref": batch_ref}, 201

# cd src
# export FLASK_APP=allocation/interfaces/rest/api.py
# export FLASK_DEBUG=1
# flask run --host=0.0.0.0 --port=5005
