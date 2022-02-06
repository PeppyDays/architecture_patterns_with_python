from sqlalchemy.orm import Session

from src.domain.model.aggregates import Batch
from src.domain.repositories import AbstractRepository


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, batch: Batch) -> str:
        self.session.add(batch)
        return Batch.ref

    def get(self, ref: str) -> Batch:
        return self.session.query(Batch).filter_by(ref=ref).one()

    def list(self) -> list[Batch]:
        return self.session.query(Batch).all()
