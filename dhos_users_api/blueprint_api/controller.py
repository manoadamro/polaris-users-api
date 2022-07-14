import base64
import random
import re
from datetime import date
from typing import Any, Dict, List, Optional, Set, Tuple

from flask import g
from flask_batteries_included.helpers import schema
from flask_batteries_included.helpers.error_handler import (
    DuplicateResourceException,
    EntityNotFoundException,
)
from flask_batteries_included.helpers.security.jwt import current_jwt_user
from flask_batteries_included.sqldb import db
from she_logging import logger
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from dhos_users_api import roles
from dhos_users_api.helpers import audit, auth0_authz, publish
from dhos_users_api.models.api_spec import ClinicianCreateRequest
from dhos_users_api.models.terms_agreement import TermsAgreement
from dhos_users_api.models.user import User

FIELDS_NOT_UPDATABLE_BY_SUPER_CLINICIAN = [
    "groups",
    "password_salt",
    "password_hash",
]


def create_clinician(
    clinician_details: Dict,
    send_welcome_email: bool = True,
) -> Dict:
    ClinicianCreateRequest().load(clinician_details)
    # this will validate incoming details and add any missing keys, setting
    # the values of these to `None`.
    schema.post(json_in=clinician_details, **User.schema())
    # if trying to set "can_edit_ews" on a clinician then the key
    # will have a value, else will be `None`, as explained above
    can_edit_ews = clinician_details.get("can_edit_ews", False)
    if can_edit_ews:
        clinician_groups = clinician_details.get("groups", [])
        contract_expiry_eod_date = clinician_details.get(
            "contract_expiry_eod_date", None
        )
        ensure_current_user_can_allow_ews_change_permissions(
            clinician_groups, contract_expiry_eod_date
        )

    email_address: str = clinician_details.pop("email_address", None)
    if email_address:
        email_address = email_address.strip().lower()

    clinician_details["email_address"] = email_address or None

    # For SEND, there are some extra tasks:
    # 1) If the clinician is a temporary user and the badge number wasn't posted, generate one
    # 2) If the clinician is a permanent user:
    #   a) Ensure the correct permissions are present in the JWT
    #   b) Ensure a badge number was posted
    # 3) Ensure the badge number is unique
    product_names: List[str] = [
        p["product_name"] for p in clinician_details.get("products", [])
    ]

    if "SEND" in product_names:
        is_temporary: bool = (
            clinician_details.get("contract_expiry_eod_date") is not None
        )
        send_entry_identifier: str = clinician_details.get(
            "send_entry_identifier", None
        )
        if is_temporary:
            clinician_details["can_edit_ews"] = False

            if send_entry_identifier:
                logger.info(
                    "Using existing badge number '%s' for new temp SEND clinician",
                    send_entry_identifier,
                )
            else:
                send_entry_identifier = _generate_send_entry_identifier()
                clinician_details["send_entry_identifier"] = send_entry_identifier
                logger.info(
                    "Generated badge number '%s' for new temp SEND clinician",
                    send_entry_identifier,
                )
        else:
            if "write:send_clinician_all" not in g.jwt_scopes:
                raise PermissionError(
                    "You do not have permission to create a permanent SEND user"
                )
            if not send_entry_identifier:
                raise ValueError(
                    "Cannot create a permanent SEND user without a badge number"
                )

    clinician: User = _create_and_publish_clinician(
        clinician_details, send_welcome_email=send_welcome_email
    )
    return clinician.to_dict()


def ensure_current_user_can_allow_ews_change_permissions(
    clinician_groups: List[str], contract_expiry_eod_date: Optional[date]
) -> None:
    is_system_user = g.jwt_claims.get("system_id", None) is not None
    if is_system_user:
        return

    new_clinician_is_send_clinician = any(
        group in clinician_groups for group in ("SEND Clinician", "SEND Superclinician")
    )
    if not new_clinician_is_send_clinician:
        raise ValueError("Only SEND clinicians can allow EWS change permission")

    if contract_expiry_eod_date:
        raise ValueError("Temporary clinicians cannot allow EWS change permission")

    jwt_user_uuid = current_jwt_user()
    jwt_user = User.query.get(jwt_user_uuid)
    if jwt_user is None or "SEND Administrator" not in jwt_user.groups:
        raise PermissionError(
            "only admins are allowed to change 'can_edit_ews' on users"
        )


def _generate_send_entry_identifier() -> str:
    """Generate a 9-digit badge number prefixed with a '@', and ensure it is not already taken"""
    while True:
        identifier: str = "@%0.9d" % random.randint(0, 999_999_999)
        if User.query.filter_by(send_entry_identifier=identifier).first() is None:
            return identifier


def _create_and_publish_clinician(
    clinician_details: Dict, send_welcome_email: bool = True
) -> User:
    # Ensure (required) fields that the UI will use to sort on have been stripped of whitespace.
    clinician_details["first_name"] = clinician_details["first_name"].strip()
    clinician_details["last_name"] = clinician_details["last_name"].strip()

    # Create and save the clinician object.
    clinician: User = User.new(**clinician_details)
    try:
        db.session.commit()
    except IntegrityError:
        raise DuplicateResourceException(
            f"Attempted to create user with existing email address '{clinician_details['email_address']}'"
        )

    # Update the clinician's groups in Auth0.
    auth0_authz.add_user_to_authz_groups(
        user_id=clinician.uuid, groups_to_add_to=clinician_details["groups"]
    )

    publish.clinician_creation_event(clinician)
    if send_welcome_email:
        publish.welcome_email_notification(clinician)

    return clinician


def get_clinician_by_id(clinician_id: str, get_temp_only: bool) -> Dict:
    clinician: User = User.query.get(clinician_id)
    if not clinician:
        raise EntityNotFoundException(f"No user found with UUID {clinician_id}")
    if get_temp_only and clinician.contract_expiry_eod_date is None:
        raise PermissionError("Insufficient privileges to access clinician")

    return clinician.to_dict()


def get_clinician_by_email(email: str) -> Dict:
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError(f"Email {email} is not valid")

    clinician: User = User.query.filter_by(email_address=email.strip().lower()).all()
    if not clinician:
        raise EntityNotFoundException(f"No user found with address {email}")

    if len(clinician) > 1:
        raise EntityNotFoundException("Email address associated with multiple users")

    return clinician[0].to_dict()


def clinician_login(user_auth_string_b64: str) -> Dict:
    username, password = get_clinician_credentials(
        user_authorization=user_auth_string_b64
    )
    if not username or not password:
        raise PermissionError("Login failed")

    clinician: Optional[User] = get_clinician_by_username(username=username)

    if (
        not validate_clinician_login(
            clinician=clinician, username=username, password=password
        )
        or not clinician
    ):
        raise PermissionError("Login failed")

    clinician_login_details = clinician.to_login_dict()

    # Add permissions
    permissions = roles.get_permissions_for_roles(clinician.groups)
    logger.debug(
        "Adding permissions for groups: %s",
        clinician.groups,
        extra={"permissions": permissions},
    )
    clinician_login_details["permissions"] = permissions

    return clinician_login_details


def get_clinician_credentials(user_authorization: str) -> Tuple[str, str]:
    """
    Takes a base64 encoded username and password (joined by ':').
    Decodes, splits by ":" to get two strings, "username" (email address or badge number) and a password.

    username and password are returned as a tuple (in that order)

    :param user_authorization: base64 encoded bytes formatted as -> "username:password"
    :type user_authorization: Union[bytes, str]

    :return: a tuple: (username, password)
    :rtype: Tuple[str, str]
    """
    username_and_password: str = base64.b64decode(user_authorization).decode("utf8")
    username, password = username_and_password.split(":", maxsplit=1)
    return username, password


def get_clinician_by_username(username: str) -> Optional[User]:
    """
    Takes either an email address or a badge number (send entry identifier)
    and attempts to find a clinician with matching entries.

    If a clinician is not found, it is returned.
    If not, an appropriate error is raised.

    :param username: this can be EITHER an email address or send entry identifier (badge number)
    :type username: str

    :return: a clinician node if one is found or None.
    :rtype: Clinician
    """

    clinician: User = User.query.filter(
        or_(
            User.email_address == username.strip().lower(),
            User.send_entry_identifier == username,
        )
    ).all()

    if not clinician:
        logger.error("Clinician not found for username '%s'", username)
        return None

    if len(clinician) > 1:
        logger.error("Multiple clinician's found for username '%s'", username)
        return None

    return clinician[0]


def deactivate_clinician(clinician_id: str) -> None:
    clinician = User.query.get(clinician_id)
    logger.debug("Deactivating clinician %s", clinician_id)
    clinician.login_active = False
    db.session.commit()
    publish.clinician_update_event(clinician)


def validate_clinician_login(
    clinician: Optional[User], username: str, password: str
) -> bool:
    if clinician is None:
        audit.record_authentication_failure(
            reason="Authentication failed, invalid username",
            event_data={"username": username},
        )
        return False
    if clinician.login_active is False:
        audit.record_authentication_failure(
            reason="Account is disabled", event_data={"clinician_id": clinician.uuid}
        )
        return False
    if (clinician.contract_expiry_eod_date is not None) and (
        date.today() > clinician.contract_expiry_eod_date
    ):
        deactivate_clinician(clinician_id=clinician.uuid)
        audit.record_authentication_failure(
            reason="Login expired",
            event_data={
                "contract_expiry_eod_date": clinician.contract_expiry_eod_date,
                "clinician_id": clinician.uuid,
            },
        )
        return False
    is_valid_password = clinician.validate_password(password)
    if is_valid_password:
        audit.record_authentication_success(clinician_uuid=clinician.uuid)
    else:
        audit.record_authentication_failure(
            reason="Invalid password", event_data={"clinician_id": clinician.uuid}
        )

    return is_valid_password


def create_clinician_tos(clinician_id: str, clinician_details: Dict) -> Dict:
    clinician: User = User.query.get(clinician_id)
    if not clinician:
        raise EntityNotFoundException(f"No user found with UUID {clinician_id}")

    tos = TermsAgreement.new(**clinician_details)
    clinician.terms_agreement.append(tos)

    db.session.commit()

    return tos.to_dict()


def update_clinician_password_by_email(email: str, password: str) -> Dict:
    clinician: User = User.query.filter_by(
        email_address=email.strip().lower()
    ).first_or_404()
    clinician.set_password(password)
    db.session.commit()
    return clinician.to_dict()


def remove_from_clinician(clinician_id: str, clinician_details: Dict) -> Dict:
    clinician: User = User.query.get(clinician_id)
    if "groups" in clinician_details and current_jwt_user() == clinician.uuid:
        raise PermissionError("clinician is not allowed to change their own groups")

    if "groups" in clinician_details and isinstance(clinician_details["groups"], str):
        clinician_details["groups"] = [clinician_details["groups"]]

    groups: List = clinician_details.get("groups", [])
    clinician.groups = [group for group in clinician.groups if group not in groups]
    locations: List = clinician_details.get("locations", [])
    clinician.locations = [loc for loc in clinician.locations if loc not in locations]
    bookmarks: List = clinician_details.get("bookmarks", [])
    clinician.bookmarks = [b for b in clinician.bookmarks if b not in bookmarks]
    bookmarked_patients: List = clinician_details.get("bookmarked_patients", [])
    clinician.bookmarked_patients = [
        b for b in clinician.bookmarked_patients if b not in bookmarked_patients
    ]

    _remove(clinician, clinician_details)
    db.session.commit()

    # Remove clinician from groups in Auth0.
    if groups:
        auth0_authz.remove_user_from_authz_groups(
            user_id=clinician.uuid, groups_to_remove_from=groups
        )

    publish.clinician_update_event(clinician)
    return clinician.to_dict()


def _remove(clinician: User, clinician_details: Dict) -> None:
    products = clinician_details.pop("products", None)
    if products:
        product_uuids: List[str] = [pr["uuid"] for pr in products]
        for p in clinician.products:
            if p.uuid in product_uuids:
                db.session.delete(p)


def update_clinician(
    clinician_id: str, update_fields: Dict, edit_temp_only: bool
) -> Dict:
    clinician: User = User.query.get(clinician_id)
    # These variables could be populated later by passing through request context info
    # prevent those with "_temp" access updating permanent users
    is_permanent_clinician = clinician.contract_expiry_eod_date is None or (
        "contract_expiry_eod_date" in update_fields
        and update_fields["contract_expiry_eod_date"] is None
    )
    if "groups" in update_fields:
        if isinstance(update_fields["groups"], str):
            update_fields["groups"] = [update_fields["groups"]]
    if "groups" in update_fields and current_jwt_user() == clinician.uuid:
        raise PermissionError("clinician is not allowed to change their own groups")

    # if trying to set "can_edit_ews" on a clinician then the key
    # will have a value, else will be `None`, as explained above

    can_edit_ews = update_fields.get("can_edit_ews", False)
    if can_edit_ews:
        clinician_groups = update_fields.get("groups", [])
        contract_expiry_eod_date = update_fields.get("contract_expiry_eod_date", None)

        ensure_current_user_can_allow_ews_change_permissions(
            clinician_groups + clinician.groups,
            contract_expiry_eod_date,
        )

        # users can not edit their own "can_edit_ews"
        if current_jwt_user() == clinician.uuid:
            raise PermissionError(
                "clinician is not allowed to change their own 'can_edit_ews'"
            )

    # If email address has changed, check the new one doesn't already exist.
    email_address = update_fields.get("email_address", None)
    if email_address == "":
        update_fields["email_address"] = None
    elif email_address:
        email_address = email_address.strip().lower()
        update_fields["email_address"] = email_address

    _check_temp_edit_permissions(
        edit_temp_only=edit_temp_only,
        is_permanent_clinician=is_permanent_clinician,
        update_fields=update_fields,
    )

    # If login_active altered log change
    login_active = update_fields.get("login_active", None)
    if login_active == clinician.login_active:
        login_active = None
    # user has been changed from temporary to permanent
    if (
        "contract_expiry_eod_date" in update_fields
        and update_fields["contract_expiry_eod_date"] is None
        and clinician.contract_expiry_eod_date is not None
        and "write:send_clinician_all" not in g.jwt_scopes
    ):
        raise PermissionError("No authorisation to make user permanent")

    # Ensure (required) fields that the UI will use to sort on have been stripped of whitespace.
    if update_fields.get("first_name"):
        update_fields["first_name"] = update_fields["first_name"].strip()
    if update_fields.get("last_name"):
        update_fields["last_name"] = update_fields["last_name"].strip()

    groups = update_fields.pop("groups", [])
    clinician.groups = sorted(set(clinician.groups + groups))
    locations = update_fields.pop("locations", [])
    clinician.locations = sorted(set(clinician.locations + locations))
    bookmarks = update_fields.pop("bookmarks", [])
    clinician.bookmarks = sorted(set(clinician.bookmarks + bookmarks))
    bookmarked_patients = update_fields.pop("bookmarked_patients", [])
    clinician.bookmarked_patients = sorted(
        set(clinician.bookmarked_patients + bookmarked_patients)
    )

    clinician.update(**update_fields)
    try:
        db.session.commit()
    except IntegrityError:
        raise DuplicateResourceException

    if login_active is not None:
        event_type = "login activated" if login_active else "login deactivated"
        event_data = {
            "clinician_id": clinician.uuid,
            "modified_by": clinician.modified_by_,
        }
        publish.audit_message(event_type=event_type, event_data=event_data)

    # Update clinician's groups in Auth0.
    if groups:
        auth0_authz.add_user_to_authz_groups(
            user_id=clinician.uuid, groups_to_add_to=groups
        )

    publish.clinician_update_event(clinician)

    return clinician.to_dict()


def _check_temp_edit_permissions(
    edit_temp_only: bool, is_permanent_clinician: bool, update_fields: Dict
) -> None:
    if edit_temp_only and is_permanent_clinician:
        raise PermissionError("Insufficient privileges to edit permanent user")

    if edit_temp_only:
        if any(f in FIELDS_NOT_UPDATABLE_BY_SUPER_CLINICIAN for f in update_fields):
            raise PermissionError("Insufficient privileges to edit these fields")


def get_clinicians(
    login_active: Optional[bool] = None,
    product_name: Optional[str] = None,
    temp_only: bool = False,
    compact: bool = False,
    expanded: bool = False,
    modified_since: Optional[str] = None,
    q: Optional[str] = None,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[str]] = None,
    order: Optional[str] = None,
) -> Tuple[List[Dict], int]:
    query = User.query
    if product_name is not None:
        query = query.filter(User.products.any(product_name=product_name))

    if login_active is not None:
        query = query.filter(User.login_active == login_active)

    if temp_only:
        query = query.filter(User.contract_expiry_eod_date.is_not(None))

    if modified_since:
        query = query.filter(User.modified > modified_since)

    if q:
        query = query.filter(
            or_(
                (User.last_name + " " + User.first_name).ilike(f"%{q}%"),
                func.array_to_string(User.groups, " ").ilike(f"%{q}%"),
                User.send_entry_identifier == q,
            )
        )

    total = query.count()

    if sort:
        if order == "desc":
            query = query.order_by(*[getattr(User, s).desc() for s in sort])
        else:
            query = query.order_by(*[getattr(User, s).asc() for s in sort])

    if offset:
        query = query.offset(offset)

    if limit:
        query = query.limit(limit)

    results = query.all()

    clinicians: List[Dict] = []
    for c in results:
        data = {
            "send_entry_identifier": c.send_entry_identifier,
            "contract_expiry_eod_date": c.contract_expiry_eod_date,
            "groups": c.groups,
            "login_active": c.login_active,
        }
        if expanded:
            data.update(c.to_dict())
        else:
            data.update(c.to_compact_dict())
            if not compact:
                data["locations"] = c.locations
        clinicians.append(data)
    return clinicians, total


def get_clinicians_by_uuids(
    uuids: List[str], compact: bool
) -> Dict[str, Optional[Dict]]:
    """Gets a map of clinician UUIDs and clinician objects"""

    logger.debug("Retrieving clinicians: %s", uuids)
    unique_uuids: Set[str] = set(uuids)

    results: List[User] = User.query.filter(User.uuid.in_(uuids)).all()

    logger.info("Retrieved %d clinicians from database", len(results))

    # Create map of clinicians
    clinician_map: Dict[str, Optional[Dict]] = {}
    if compact:
        clinician_map.update({c.uuid: c.to_compact_dict() for c in results})
    else:
        clinician_map.update({c.uuid: c.to_dict() for c in results})

    # If any UUIDs weren't found in the database, add empty values to the map for each.
    missing_uuids: Set[str] = unique_uuids - set([c.uuid for c in results])
    if missing_uuids:
        logger.info(
            "Could not retrieve %d clinicians from database", len(missing_uuids)
        )
        logger.debug("Missing UUIDs: %s", missing_uuids)
        clinician_map.update({m: None for m in missing_uuids})

    return clinician_map


def get_clinicians_at_location(location_uuid: str) -> List[Dict[str, Any]]:
    results: List[User] = User.query.filter(
        User.locations.contains([location_uuid])
    ).all()

    return [clinician.to_dict() for clinician in results]


def add_clinician_location_bookmark(clinician_id: str, location_id: str) -> None:
    clinician: User = User.query.get(clinician_id)
    clinician.bookmarks = sorted(set(clinician.bookmarks + [location_id]))
    db.session.commit()


def remove_clinician_location_bookmark(clinician_id: str, location_id: str) -> None:
    clinician: User = User.query.get(clinician_id)
    clinician.bookmarks = [loc for loc in clinician.bookmarks if loc != location_id]
    db.session.commit()


def add_clinician_patient_bookmark(clinician_id: str, patient_id: str) -> None:
    clinician: User = User.query.get(clinician_id)
    clinician.bookmarked_patients = sorted(
        set(clinician.bookmarked_patients + [patient_id])
    )
    db.session.commit()


def remove_clinician_patient_bookmark(clinician_id: str, patient_id: str) -> None:
    clinician: User = User.query.get(clinician_id)
    clinician.bookmarked_patients = [
        p for p in clinician.bookmarked_patients if p != patient_id
    ]
    db.session.commit()


def create_clinicians_bulk(clinician_details: List[Dict]) -> Dict:
    logger.info("Adding %d clinicians in bulk", len(clinician_details))
    for details in clinician_details:
        logger.info("Adding clinician %s", details["uuid"])
        terms_agreements = details.pop("terms_agreements", [])
        user_uuid = details.pop("uuid")
        products = details.pop("products")
        User.new(uuid=user_uuid, products=products, **details)
        for terms_agreement in terms_agreements:
            TermsAgreement.new(user_id=user_uuid, **terms_agreement)
    db.session.commit()
    return {"created": len(clinician_details)}


def get_roles() -> Dict[str, list[str]]:
    return roles.get_role_map()
