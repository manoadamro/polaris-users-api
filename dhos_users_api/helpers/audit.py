from typing import Any, Dict

from she_logging import logger

from dhos_users_api.helpers import publish


def record_authentication_failure(reason: str, event_data: Dict[str, Any]) -> None:
    logger.debug(f"Recording authentication failure: {reason}")
    if "reason" not in event_data:
        event_data["reason"] = reason
    publish.audit_message(event_type="Login Failure", event_data=event_data)


def record_authentication_success(clinician_uuid: str) -> None:
    logger.debug(f"Recording authentication success for clinician {clinician_uuid}")
    publish.audit_message(
        event_type="Login Success", event_data={"clinician_id": clinician_uuid}
    )
