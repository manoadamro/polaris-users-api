import logging
from typing import Dict, Generator

from behave import fixture
from behave.runner import Context
from environs import Env
from kombu import Connection, Exchange, Message, Queue
from kombu.simple import SimpleQueue
from kombu.utils import json

logger = logging.getLogger("Tests")


@fixture
def create_rabbitmq_connection(context: Context) -> Connection:
    env = Env()
    host: str = env.str("RABBITMQ_HOST")
    port: int = env.int("RABBITMQ_PORT", 5672)
    username: str = env.str("RABBITMQ_USERNAME")
    password: str = env.str("RABBITMQ_PASSWORD")
    conn_string: str = f"amqp://{username}:{password}@{host}:{port}//"
    connection: Connection = Connection(conn_string)
    exchange: Exchange = Exchange("dhos", "topic", channel=connection)
    context.rabbit_connection = connection
    context.rabbit_exchange = exchange
    yield connection
    connection.release()
    del context.rabbit_exchange
    del context.rabbit_connection


@fixture
def create_rabbitmq_queues(
    context: Context, routing_keys: Dict[str, str]
) -> Generator[Dict[str, SimpleQueue], None, None]:
    # Declare normal exchange, linked to DLX
    exchange = context.rabbit_exchange
    connection = context.rabbit_connection
    context.rabbit_queues = {}
    for name, routing_key in routing_keys.items():
        queue = Queue(
            routing_key, exchange=exchange, routing_key=routing_key, channel=connection
        )
        queue.declare()
        context.rabbit_queues[routing_key] = SimpleQueue(connection, queue)
    yield context.rabbit_queues

    messages = []
    for routing_key, queue in context.rabbit_queues.items():
        if len(queue) != 0:
            messages.append(routing_key)
            logger.warning(f"Queue not empty {routing_key} length {len(queue)}")
        queue.clear()
        queue.close()
    del context.rabbit_queues

    if messages:
        logger.warning(
            "Unprocessed rabbit messages: "
            + ", ".join(k for k in routing_keys if routing_keys[k] in messages)
        )


def get_rabbitmq_message(
    context: Context, message_name: str, timeout: int = 20
) -> Dict:
    queue: SimpleQueue = context.rabbit_queues[message_name]
    message: Message = queue.get(block=True, timeout=timeout)
    message.ack()
    return json.loads(message.body)


def assert_rabbitmq_message_queues_are_empty(context: Context) -> None:
    for routing_key, queue in context.rabbit_queues.items():
        assert len(queue) == 0, f"Queue not empty {routing_key} length {len(queue)}"
