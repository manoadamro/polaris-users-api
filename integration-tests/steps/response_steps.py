from typing import Any, Dict, Set

from behave import then
from behave.runner import Context
from clients import users_api_client
from helpers.json import load_json_test
from helpers.jwt import get_system_token
from requests import Response


@then("the clinician (?P<email>\S+) can be found by email")
def clinician_with_email_exists(context: Context, email: str) -> None:
    response: Response = users_api_client.get_clinician_by_email(
        email=email, jwt=get_system_token()
    )
    context.response = response
    assert response.status_code == 200
    assert response.json()["email_address"] == email


def recursively_remove(obj: Any, keys: Set[str]) -> Any:
    if isinstance(obj, list):
        return [recursively_remove(item, keys) for item in obj]
    if isinstance(obj, dict):
        return {k: recursively_remove(obj[k], keys) for k in obj if k not in keys}
    return obj


@then("the response matches (?P<output_filename>\S+)")
def the_response_matches(context: Context, output_filename: str) -> None:
    """Output filename should be in json patch format and may modify and test the output as
    required."""
    json_test = load_json_test(output_filename)
    output = recursively_remove(
        context.output, {"created", "created_by", "modified", "modified_by", "uuid"}
    )
    assert json_test == output, f"Expected: {json_test}\nActual: {output}"


@then("the response includes a location bookmark")
def the_response_includes_location_bookmark(context: Context) -> None:
    """Output filename should be in json patch format and may modify and test the output as
    required."""
    expected_location_bookmark = "B2"
    output = context.response.json()["bookmarks"][0]
    assert (
        expected_location_bookmark == output
    ), f"Expected: {expected_location_bookmark}\nActual: {output}"


@then("the response does not include a location bookmark")
def the_response_excludes_location_bookmark(context: Context) -> None:
    """Output filename should be in json patch format and may modify and test the output as
    required."""
    expected_location_bookmark: list = []
    output = context.response.json()["bookmarks"]
    assert (
        expected_location_bookmark == output
    ), f"Expected: {expected_location_bookmark}\nActual: {output}"


@then("the response is the expected list of clinicians")
def the_clinicians_response(context: Context) -> None:
    """Output filename should be in json patch format and may modify and test the output as
    required."""
    test_length = context.client_number
    output_length = len(context.output)
    assert test_length == len(
        context.output
    ), f"Expected: {test_length}\nActual: {output_length}"


@then("the locations response matches (?P<output_filename>\S+)")
def the_locations_response_matches(context: Context, output_filename: str) -> None:
    """Output filename should be in json patch format and may modify and test the output as
    required."""
    json_locations_test = ["A1"]
    output = recursively_remove(
        context.output, {"created", "created_by", "modified", "modified_by", "uuid"}
    )
    output_locations = output["locations"]
    assert (
        json_locations_test == output_locations
    ), f"Expected: {json_locations_test}\nActual: {output_locations}"


@then("the clinician is not active")
def the_clinicin_is_not_active(context: Context) -> None:
    assert context.response.json()["login_active"] is False


@then("(?P<email>\S+) has a terms agreement that matches (?P<output_filename>\S+)")
def clinician_has_a_terms_agreement(
    context: Context, email: str, output_filename: str
) -> None:
    response: Response = users_api_client.get_clinician_by_email(
        email=email, jwt=get_system_token()
    )
    context.response = response
    json_test = load_json_test(output_filename)
    output = recursively_remove(
        context.output, {"created", "created_by", "modified", "modified_by", "uuid"}
    )
    assert json_test == output, f"Expected: {json_test}\nActual: {output}"


@then("clinician with email (?P<email>\S+) can login with password (?P<password>\S+)")
def clinician_can_login(context: Context, email: str, password: str) -> None:
    response: Response = users_api_client.clinician_login(
        email=email, password=password, jwt=context.login_jwt
    )
    assert response.status_code == 200


@then("clinician with email (?P<email>\S+) can login using password (?P<password>\S+)")
def clinician_can_login_using_password(
    context: Context, email: str, password: str
) -> None:
    response: Response = users_api_client.clinician_login(
        email=email, password=password, jwt=get_system_token()
    )
    assert response.status_code == 200


@then("I see that the clinicians have been created")
def check_clinicians_created_bulk(context: Context) -> None:
    expected_clinician_uuids = [c["uuid"] for c in context.bulk_clinicians]
    response = users_api_client.retrieve_clinicians_by_uuids(
        clinician_uuids=expected_clinician_uuids, jwt=get_system_token()
    )
    actual_clinicians_map: Dict[str, Dict] = response.json()
    assert set(expected_clinician_uuids) == actual_clinicians_map.keys()


@then("I can see the expected clinicians \(v1\)")
def check_clinicians_response_v1(context: Context) -> None:
    actual_clinician_uuids = {c["uuid"] for c in context.clinicians_response.json()}
    assert actual_clinician_uuids == set(context.clinician_uuids)


@then("I can see the expected clinicians \(v2\)")
def check_clinicians_response_v2(context: Context) -> None:
    assert context.clinicians_response.json()["total"] == len(context.clinician_uuids)
    actual_clinician_uuids = {
        c["uuid"] for c in context.clinicians_response.json()["results"]
    }
    assert actual_clinician_uuids == set(context.clinician_uuids)


@then("I can see the clinician with email (?P<email>\S+)")
def check_search_results(context: Context, email: str) -> None:
    assert context.clinicians_response.json()["total"] == 1
    assert context.clinicians_response.json()["results"][0]["email_address"] == email
