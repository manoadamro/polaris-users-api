from behave import given, step, use_fixture
from behave.runner import Context
from clients.rabbitmq_client import (
    create_rabbitmq_connection,
    create_rabbitmq_queues,
    get_rabbitmq_message,
)
from helpers.jwt import get_system_token

RABBITMQ_MESSAGES = {
    "AUDIT_MESSAGE": "dhos.34837004",
    "CLINICIAN_CREATED_MESSAGE": "dhos.D9000001",
    "CLINICIAN_UPDATED_MESSAGE": "dhos.D9000002",
    "EMAIL_NOTIFICATION_MESSAGE": "dhos.DM000017",
}
MESSAGE_NAMES = "|".join(RABBITMQ_MESSAGES)


@given("RabbitMQ is running")
def rabbitmq_is_running(context: Context) -> None:
    if not hasattr(context, "rabbit_connection"):
        context.rabbit_connection = use_fixture(create_rabbitmq_connection, context)
        use_fixture(create_rabbitmq_queues, context, routing_keys=RABBITMQ_MESSAGES)


@given("a valid JWT")
def get_system_jwt(context: Context) -> None:
    if not hasattr(context, "system_jwt"):
        context.system_jwt = get_system_token()


@step(f"a (?P<message_name>\w+) message is published to RabbitMQ")
def message_published_to_rabbitmq(context: Context, message_name: str) -> None:
    get_rabbitmq_message(context, RABBITMQ_MESSAGES[message_name])
