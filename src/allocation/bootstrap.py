from typing import Callable

from allocation.application import message_bus
from allocation.application.unit_of_work import UnitOfWork
from allocation.infrastructure.brokers import publisher
from allocation.infrastructure.services import email
