from flask import Flask
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import configuration
from allocation.application.exceptions import InvalidSku
from allocation.application.services import allocate
from allocation.domain.exceptions import OutOfStock
from allocation.domain.model.value_objects import OrderLine
from allocation.infrastructure.repositories import sqlalchemy_orm
from allocation.infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository

sqlalchemy_orm.start_mappers()
get_session = sessionmaker(bind=create_engine(configuration.get_postgres_uri()))

app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repository = SqlAlchemyRepository(session)
    line = OrderLine(
        order_id=request.json["order_id"],
        sku=request.json["sku"],
        qty=request.json["qty"],
    )

    try:
        batch_ref = allocate(line=line, repository=repository, session=session)
    except (OutOfStock, InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batch_ref": batch_ref}, 201
