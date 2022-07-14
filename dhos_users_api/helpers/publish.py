from datetime import date
from typing import Any, Dict

import kombu_batteries_included
from she_logging import logger

from dhos_users_api.models.user import User


def fix_dates(data: Dict) -> Dict:
    if isinstance(data, (dict, list)):
        for k, v in data.items() if isinstance(data, dict) else enumerate(data):
            if isinstance(v, date):
                data[k] = v.isoformat()
            fix_dates(v)
    return data


def clinician_creation_event(clinician: User) -> None:
    message_body: Dict = fix_dates(clinician.to_auth_dict())
    logger.info("Publishing dhos.D9000001 clinician creation event")
    kombu_batteries_included.publish_message(
        routing_key="dhos.D9000001", body=message_body
    )


def clinician_update_event(clinician: User) -> None:
    message_body: Dict = clinician.to_auth_dict()
    logger.info("Publishing dhos.D9000002 clinician update event")
    kombu_batteries_included.publish_message(
        routing_key="dhos.D9000002", body=fix_dates(message_body)
    )


def welcome_email_notification(clinician: User) -> None:
    email_details: Dict = {
        "email_address": clinician.email_address,
        "email_type": "WELCOME_EMAIL",
    }

    logger.info("Publishing dhos.DM000017 email notification")
    kombu_batteries_included.publish_message(
        routing_key="dhos.DM000017", body=email_details
    )


def audit_message(event_type: str, event_data: Dict[str, Any]) -> None:
    logger.info(f"Publishing dhos.34837004 audit message of type {event_type}")
    audit = {"event_type": event_type, "event_data": event_data}
    kombu_batteries_included.publish_message(routing_key="dhos.34837004", body=audit)
