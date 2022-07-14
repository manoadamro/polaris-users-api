from typing import List

from auth0_api_client import authz as auth0_authz
from auth0_api_client.errors import Auth0ConnectionError, Auth0OperationError
from flask import current_app
from flask_batteries_included.config import is_production_environment
from flask_batteries_included.helpers.error_handler import ServiceUnavailableException
from she_logging import logger


def add_user_to_authz_groups(user_id: str, groups_to_add_to: List[str]) -> None:
    """
    Adds clinician to groups on Auth0 authorization extension.
    """
    if (
        not is_production_environment()
        and current_app.config["IGNORE_JWT_VALIDATION"] is True
    ):
        logger.info("No JWT validation, skipping Auth0 task")
        return
    if current_app.config["DISABLE_CREATE_USER_IN_AUTH0"]:
        logger.info("Auth0 authz extension user update disabled")
        return

    try:
        logger.debug("Adding user to group(s)", extra={"group_ids": groups_to_add_to})
        auth0_authz.add_user_to_authz_groups(user_id, groups_to_add_to)
    except (Auth0ConnectionError, Auth0OperationError) as e:
        logger.exception("Could not communicate with Auth0")
        raise ServiceUnavailableException(e)


def remove_user_from_authz_groups(
    user_id: str, groups_to_remove_from: List[str]
) -> None:
    """
    Removes clinician from groups on Auth0 authorization extension.
    """
    if (
        not is_production_environment()
        and current_app.config["IGNORE_JWT_VALIDATION"] is True
    ):
        logger.info("No JWT validation, skipping Auth0 task")
        return
    if current_app.config["DISABLE_CREATE_USER_IN_AUTH0"]:
        logger.info("Auth0 authz extension user update disabled")
        return

    try:
        logger.debug(
            "Removing user from group(s)", extra={"group_ids": groups_to_remove_from}
        )
        auth0_authz.remove_user_from_authz_groups(user_id, groups_to_remove_from)
    except (Auth0ConnectionError, Auth0OperationError) as e:
        logger.exception("Could not communicate with Auth0")
        raise ServiceUnavailableException(e)
