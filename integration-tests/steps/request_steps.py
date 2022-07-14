import uuid
from datetime import datetime, timezone
from random import randint
from typing import Callable, Dict

from behave import given, step, when
from behave.runner import Context
from clients import users_api_client
from faker import Faker
from helpers import security
from helpers.jwt import get_system_token
from requests import Response

fake = Faker()

TOKEN_GENERATORS: Dict[str, Callable[[Context], str]] = {
    "system": security.generate_system_token,
    "login": security.generate_login_token,
    "clinician": security.generate_clinician_token,
    "superclinician": security.generate_superclinician_token,
    "patient": security.generate_patient_token,
}


@given("a SEND clinician with email (?P<email>\S+) exists")
def create_send_clinician_with_email(context: Context, email: str) -> None:
    first_name = email.split("@")[0].split(".")[0]
    last_name = email.split("@")[0].split(".")[1]
    clinician = {
        "first_name": first_name.capitalize(),
        "last_name": last_name.capitalize(),
        "job_title": "doctor",
        "phone_number": "",
        "groups": ["SEND Clinician"],
        "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
        "locations": ["A1", "B2"],
        "send_entry_identifier": str(randint(100000, 999999)),
        "nhs_smartcard_number": str(randint(100000, 999999)),
        "email_address": email,
        "contract_expiry_eod_date": None,
        "login_active": True,
    }
    response: Response = users_api_client.post_clinician(
        clinician, jwt=get_system_token()
    )
    context.response = response
    context.output = response.json()
    assert response.status_code == 200


@given(
    "a SEND clinician with email (?P<email>\S+) exists with location (?P<location>\S+)"
)
def create_send_clinician_with_email_and_location(
    context: Context, email: str, location: str
) -> None:
    first_name = email.split("@")[0].split(".")[0]
    last_name = email.split("@")[0].split(".")[1]
    clinician = {
        "first_name": first_name.capitalize(),
        "last_name": last_name.capitalize(),
        "job_title": "doctor",
        "phone_number": "",
        "groups": ["SEND Clinician"],
        "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
        "locations": [location],
        "send_entry_identifier": str(randint(100000, 999999)),
        "nhs_smartcard_number": str(randint(100000, 999999)),
        "email_address": email,
        "contract_expiry_eod_date": None,
        "login_active": True,
    }
    response: Response = users_api_client.post_clinician(
        clinician, jwt=get_system_token()
    )
    context.response = response
    context.output = response.json()
    assert response.status_code == 200


@given("I create (?P<num_clinicians>\S+) SEND clinicians")
def create_multiple_send_clinicians(context: Context, num_clinicians: str) -> None:
    clinician_uuids = []
    for i in range(int(num_clinicians)):
        clinician = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "job_title": "doctor",
            "phone_number": "",
            "groups": ["SEND Clinician"],
            "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
            "locations": [],
            "send_entry_identifier": str(randint(100000, 999999)),
            "nhs_smartcard_number": str(randint(100000, 999999)),
            "email_address": fake.email(),
            "contract_expiry_eod_date": None,
            "login_active": True,
        }
        response: Response = users_api_client.post_clinician(
            clinician, jwt=get_system_token()
        )
        assert response.status_code == 200
        clinician_uuids.append(response.json()["uuid"])
    context.clinician_uuids = clinician_uuids


@when("we patch the clinician (?P<email>\S+)")
def patch_send_clinician(context: Context, email: str) -> None:
    if context.response.json()["email_address"] == email:
        clinician_uuid = context.response.json()["uuid"]
    else:
        clinician_uuid = users_api_client.get_clinician_by_email(
            email=email, jwt=get_system_token()
        ).json()["uuid"]
    patch = {
        "job_title": "Ultimate Doctor",
        "send_entry_identifier": "499846",
        "nhs_smartcard_number": "720490",
    }

    response: Response = users_api_client.patch_clinician(
        uuid=clinician_uuid, data=patch, jwt=get_system_token()
    )
    context.response = response
    context.output = response.json()
    assert response.status_code == 200


@when("we delete a location on the clinician (?P<email>\S+)")
def delete_on_send_clinician(context: Context, email: str) -> None:
    if context.response.json()["email_address"] == email:
        clinician_uuid = context.response.json()["uuid"]
    else:
        clinician_uuid = users_api_client.get_clinician_by_email(
            email=email, jwt=get_system_token()
        ).json()["uuid"]
    delete = {
        "locations": ["B2"],
    }

    response: Response = users_api_client.remove_from_clinician(
        uuid=clinician_uuid, data=delete, jwt=get_system_token()
    )
    context.response = response
    context.output = response.json()
    assert response.status_code == 200


@when("we add a clinician location bookmark for (?P<email>\S+)")
def create_clinician_location_bookmark(context: Context, email: str) -> None:
    if context.response.json()["email_address"] == email:
        clinician_uuid = context.response.json()["uuid"]
    else:
        clinician_uuid = users_api_client.get_clinician_by_email(
            email=email, jwt=get_system_token()
        ).json()["uuid"]
    bookmark = "B2"

    response: Response = users_api_client.post_clinician_location_bookmark(
        clinician_id=clinician_uuid, location_id=bookmark, jwt=get_system_token()
    )
    context.response = response
    assert response.status_code == 201


@when("we delete a clinician location bookmark for (?P<email>\S+)")
def delete_clinician_location_bookmark(context: Context, email: str) -> None:
    if context.response.json()["email_address"] == email:
        clinician_uuid = context.response.json()["uuid"]
    else:
        clinician_uuid = users_api_client.get_clinician_by_email(
            email=email, jwt=get_system_token()
        ).json()["uuid"]
    bookmark = "B2"

    response: Response = users_api_client.delete_clinician_location_bookmark(
        clinician_id=clinician_uuid, location_id=bookmark, jwt=get_system_token()
    )
    assert response.status_code == 204


@when("we deactivate the clinician (?P<email>\S+)")
def deactivate_clinician(context: Context, email: str) -> None:
    if context.response.json()["email_address"] == email:
        clinician_uuid = context.response.json()["uuid"]
    else:
        clinician_uuid = users_api_client.get_clinician_by_email(
            email=email, jwt=get_system_token()
        ).json()["uuid"]
    patch = {
        "login_active": False,
        "send_entry_identifier": "499846",
        "nhs_smartcard_number": "720490",
    }

    response: Response = users_api_client.patch_clinician(
        uuid=clinician_uuid, data=patch, jwt=get_system_token()
    )
    context.response = response
    context.output = response.json()
    assert response.status_code == 200


@when("we get the clinician by UUID")
def get_clinician_by_id(context: Context) -> None:
    uuid = context.response.json()["uuid"]
    response: Response = users_api_client.get_clinician_by_id(
        uuid=uuid, jwt=get_system_token()
    )
    context.output = response.json()
    assert response.status_code == 200


@when("we get the clinicians for location (?P<location>\S+)")
def get_clinicians_by_location(context: Context, location: str) -> None:
    response: Response = users_api_client.get_clinicians_by_location(
        location_id=location, jwt=get_system_token()
    )
    context.output = response.json()
    assert response.status_code == 200


@when("(?P<email>\S+) accepts the terms agreement")
def clinician_accepts_the_terms_agreement(context: Context, email: str) -> None:
    if context.response.json()["email_address"] == email:
        clinician_uuid = context.response.json()["uuid"]
    else:
        clinician_uuid = users_api_client.get_clinician_by_email(
            email=email, jwt=get_system_token()
        ).json()["uuid"]

    data = {
        "product_name": "SEND",
        "version": 101,
        "accepted_timestamp": "2019-01-01T12:01:01.000",
    }

    response: Response = users_api_client.post_clinician_terms(
        uuid=clinician_uuid, data=data, jwt=get_system_token()
    )
    context.response = response
    context.output = response.json()
    assert response.status_code == 200
    assert context.output["product_name"] == data["product_name"]


@when("clinician with email (?P<email>\S+) changes password to (?P<password>\S+)")
def clinician_changes_password(context: Context, email: str, password: str) -> None:
    response: Response = users_api_client.update_clinician_password_by_email(
        email=email, password=password, jwt=get_system_token()
    )
    context.response = response
    context.output = response.json()
    assert response.status_code == 200


@step("acting as a (?P<user_type>system|login|superclinician|clinician|patient) user")
def set_current_jwt(context: Context, user_type: str) -> None:
    if user_type in TOKEN_GENERATORS:
        TOKEN_GENERATORS[user_type](context)
    else:
        raise RuntimeError("Unknown user type")


@when(
    "I create (?P<num_clinicians>\d+) clinicians in bulk with location (?P<location>\S+)"
)
def create_clinicians_bulk(
    context: Context, num_clinicians: str, location: str
) -> None:
    time_now = datetime.now(tz=timezone.utc).isoformat(timespec="milliseconds")
    clinician_details = [
        {
            "uuid": str(uuid.uuid4()),
            "created_by": str(uuid.uuid4()),
            "created": time_now,
            "modified_by": str(uuid.uuid4()),
            "modified": time_now,
            "first_name": f"clinician-{i}",
            "last_name": f"surname-{i}",
            "job_title": "dummy",
            "phone_number": "",
            "groups": ["SEND Clinician"],
            "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
            "locations": [location],
            "nhs_smartcard_number": "654987",
            "send_entry_identifier": "1323456",
            "email_address": f"clinician-bulk-{i}@test.com",
            "can_edit_ews": False,
            "contract_expiry_eod_date": None,
            "login_active": True,
            "terms_agreements": [
                {
                    "uuid": str(uuid.uuid4()),
                    "created_by": str(uuid.uuid4()),
                    "created": time_now,
                    "modified_by": str(uuid.uuid4()),
                    "modified": time_now,
                    "product_name": "SEND",
                    "version": 1,
                    "accepted_timestamp": time_now,
                }
            ],
        }
        for i in range(int(num_clinicians))
    ]
    context.bulk_clinicians = clinician_details
    response = users_api_client.post_clinicians_bulk(
        clinician_details=clinician_details, jwt=get_system_token()
    )
    context.response = response
    context.client_number = int(num_clinicians)
    assert response.status_code == 200
    assert response.json()["created"] == int(num_clinicians)


@when("I get a list of all clinicians \(v1\)")
def get_clinician_list_v1(context: Context) -> None:
    response = users_api_client.get_clinicians_v1(jwt=get_system_token())
    context.clinicians_response = response


@when("I get a list of all clinicians \(v2\)")
def get_clinician_list_v2(context: Context) -> None:
    response = users_api_client.get_clinicians_v2(jwt=get_system_token())
    context.clinicians_response = response


@when("I search clinicians using the term '(?P<query>\S+)'")
def search_clinicians(context: Context, query: str) -> None:
    response = users_api_client.get_clinicians_v2(jwt=get_system_token(), q=query)
    context.clinicians_response = response
