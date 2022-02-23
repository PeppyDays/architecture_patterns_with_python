import logging
from typing import Callable
from typing import Type

from tenacity import RetryError
from tenacity import Retrying
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from allocation.application.services import command_services
from allocation.application.services import event_handlers
from allocation.application.unit_of_work import ProductUnitOfWork
from allocation.domain import commands
from allocation.domain import events
from allocation.domain.models import Message

logger = logging.getLogger(__name__)


def handle(message: Message, uow: ProductUnitOfWork):
    results = []
    queue = [message]

    while queue:
        message = queue.pop(0)

        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} was not an Event or Command")

    return results


def handle_event(event: events.Event, queue: list[Message], uow: ProductUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_exponential()):
                with attempt:
                    logger.debug(f"handling event {event} with handler {handler}")
                    handler(event, uow)
                    queue.extend(uow.collect_new_messages())
        except RetryError as e:
            logger.error(f"failed to handle event {e.last_attempt.attempt_number} times, giving up!")
            continue
        except Exception:
            logger.exception(f"exception handling event {event}")
            continue


def handle_command(command: commands.Command, queue: list[Message], uow: ProductUnitOfWork):
    logger.debug(f"handling command {command}")
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow)
        queue.extend(uow.collect_new_messages())
        return result
    except Exception:
        logger.exception(f"exception handling command {command}")
        raise


EVENT_HANDLERS: dict[Type[events.Event], list[Callable]] = {
    events.OutOfStock: [event_handlers.send_out_of_stock_notification],
}

COMMAND_HANDLERS: dict[Type[commands.Command], Callable] = {
    commands.Allocate: command_services.allocate,
    commands.CreateBatch: command_services.add_batch,
    commands.ChangeBatchQuantity: command_services.change_batch_quantity,
}
