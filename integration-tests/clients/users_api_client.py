import base64
from typing import Dict, List, Optional

import requests
from environs import Env
from requests import Response


def _get_base_url() -> str:
    return Env().str("DHOS_USERS_BASE_URL", "http://dhos-users-api:5000")


def post_clinician(data: Dict, jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/clinician",
        headers={"Authorization": f"Bearer {jwt}"},
        json=data,
        timeout=15,
    )


def post_clinician_terms(uuid: str, data: Dict, jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/clinician/{uuid}/terms_agreement",
        headers={"Authorization": f"Bearer {jwt}"},
        json=data,
        timeout=15,
    )


def patch_clinician(uuid: str, data: Dict, jwt: str) -> Response:
    return requests.patch(
        f"{_get_base_url()}/dhos/v1/clinician/{uuid}",
        headers={"Authorization": f"Bearer {jwt}"},
        json=data,
        timeout=15,
    )


def remove_from_clinician(uuid: str, data: Dict, jwt: str) -> Response:
    return requests.patch(
        f"{_get_base_url()}/dhos/v1/clinician/{uuid}/delete",
        headers={"Authorization": f"Bearer {jwt}"},
        json=data,
        timeout=15,
    )


def update_clinician_password_by_email(email: str, password: str, jwt: str) -> Response:
    data = {"password": password}
    return requests.patch(
        f"{_get_base_url()}/dhos/v1/clinician",
        headers={"Authorization": f"Bearer {jwt}"},
        params={"email": email},
        json=data,
        timeout=15,
    )


def get_clinician_by_email(email: str, jwt: str) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/clinician",
        headers={"Authorization": f"Bearer {jwt}"},
        params={"email": email},
        timeout=15,
    )


def get_clinician_by_id(uuid: str, jwt: str) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/clinician/{uuid}",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )


def retrieve_clinicians_by_uuids(clinician_uuids: List[str], jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/clinician_list",
        headers={"Authorization": f"Bearer {jwt}"},
        json=clinician_uuids,
        timeout=15,
    )


def clinician_login(email: str, password: str, jwt: str) -> Response:
    auth_string: str = f"{email}:{password}"
    auth: bytes = base64.b64encode(bytes(auth_string, "utf-8"))
    base64_auth_string: str = auth.decode("utf-8")

    return requests.get(
        f"{_get_base_url()}/dhos/v1/clinician/login",
        timeout=15,
        headers={
            "Authorization": f"Bearer {jwt}",
            "UserAuthorization": f"Bearer {base64_auth_string}",
        },
    )


def post_clinicians_bulk(clinician_details: List[Dict], jwt: str) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/clinician/bulk",
        headers={"Authorization": f"Bearer {jwt}"},
        json=clinician_details,
        timeout=30,
    )


def drop_all_data(jwt: str) -> Response:
    response = requests.post(
        f"{_get_base_url()}/drop_data",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )
    assert response.status_code == 200
    return response


def get_clinicians_v1(jwt: str, q: Optional[str] = None) -> Response:
    response = requests.get(
        f"{_get_base_url()}/dhos/v1/clinicians",
        headers={"Authorization": f"Bearer {jwt}"},
        params={"q": q},
        timeout=15,
    )
    assert response.status_code == 200
    return response


def get_clinicians_v2(jwt: str, q: Optional[str] = None) -> Response:
    response = requests.get(
        f"{_get_base_url()}/dhos/v2/clinicians",
        headers={"Authorization": f"Bearer {jwt}"},
        params={"q": q},
        timeout=15,
    )
    assert response.status_code == 200
    return response


def get_clinicians_by_location(location_id: str, jwt: str) -> Response:
    return requests.get(
        f"{_get_base_url()}/dhos/v1/location/{location_id}/clinician",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )


def post_clinician_location_bookmark(
    clinician_id: str, location_id: str, jwt: str
) -> Response:
    return requests.post(
        f"{_get_base_url()}/dhos/v1/clinician/{clinician_id}/location/{location_id}/bookmark",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )


def delete_clinician_location_bookmark(
    clinician_id: str, location_id: str, jwt: str
) -> Response:
    return requests.delete(
        f"{_get_base_url()}/dhos/v1/clinician/{clinician_id}/location/{location_id}/bookmark",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )
