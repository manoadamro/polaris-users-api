import base64
import uuid
from typing import Dict

import flask
import pytest
from flask import g
from flask.testing import FlaskClient
from flask_batteries_included.helpers import generate_uuid
from mock import Mock
from pytest_mock import MockerFixture

from dhos_users_api.blueprint_api import controller


@pytest.fixture
def gdm_clinician_details() -> Dict:
    """GDM clinician fixture: Kate Bobcat"""
    clinician_details = {
        "first_name": "Kate",
        "last_name": "Bobcat",
        "job_title": "doctor",
        "phone_number": "",
        "groups": ["GDM Clinician"],
        "products": [{"product_name": "GDM", "opened_date": "2021-7-19"}],
        "locations": [],
        "nhs_smartcard_number": "98745613",
        "send_entry_identifier": "98745631",
        "email_address": "kate.bobcat@test.com",
        "can_edit_ews": False,
    }
    return clinician_details


@pytest.fixture
def gdm_clinician_uuid(gdm_clinician_details: Dict) -> Dict:
    """GDM clinician fixture: Kate Bobcat"""
    clinician = controller.create_clinician(
        clinician_details=gdm_clinician_details, send_welcome_email=False
    )
    return clinician["uuid"]


@pytest.fixture
def send_clinician_details() -> Dict:
    """SEND clinician fixture: Kate Wildcat"""
    clinician_details = {
        "first_name": "Kate",
        "last_name": "Wildcat",
        "job_title": "doctor",
        "phone_number": "",
        "groups": ["SEND Clinician"],
        "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
        "locations": [],
        "nhs_smartcard_number": "98745613",
        "send_entry_identifier": "98745631",
        "email_address": "kate.wildcat@test.com",
        "can_edit_ews": False,
    }
    return clinician_details


@pytest.fixture
def send_clinician_uuid(send_clinician_details: Dict) -> Dict:
    """SEND clinician fixture: Kate Wildcat"""
    clinician = controller.create_clinician(
        clinician_details=send_clinician_details, send_welcome_email=False
    )
    return clinician["uuid"]


@pytest.mark.usefixtures(
    "app", "mock_retrieve_jwt_claims", "mock_bearer_validation", "jwt_clinician_login"
)
class TestUsersApi:
    def test_post_user_success(
        self,
        client: FlaskClient,
        mocker: MockerFixture,
        send_clinician_details: Dict,
    ) -> None:
        mock_create: Mock = mocker.patch.object(
            controller,
            "create_clinician",
            return_value={"uuid": generate_uuid()},
        )
        response = client.post(
            "/dhos/v1/clinician",
            json=send_clinician_details,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert "uuid" in response.json
        mock_create.assert_called_with(
            clinician_details=send_clinician_details, send_welcome_email=True
        )

    def test_clinician_login_success(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:

        auth_string: str = "userA:abc*_123"
        auth: bytes = base64.b64encode(bytes(auth_string, "utf-8"))
        base64_auth_string: str = auth.decode("utf-8")

        gdm_clinician_login_response = {
            "user_id": "12345-1234-234",
            "locations": [{"name": "Eastleigh Hospital", "id": "L1"}],
            "nickname": "Jane Smith",
            "email_address": "janesmith@clinic.com",
        }

        mock_method = mocker.patch.object(
            controller,
            "clinician_login",
            return_value=gdm_clinician_login_response,
        )

        response = client.get(
            "/dhos/v1/clinician/login",
            json={},
            headers={
                "Authorization": "Bearer TOKEN",
                "UserAuthorization": f"Bearer {base64_auth_string}",
            },
        )
        assert response.status_code == 200
        assert mock_method.call_count == 1
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.parametrize(
        "new_email,expected_email",
        [
            ("FOO.Bar@mail.com", "foo.bar@mail.com"),
            ("", None),
            (None, None),
            ("***DELETE FROM JSON***", "kate.wildcat@test.com"),
        ],
    )
    def test_clinician_patch(
        self,
        client: FlaskClient,
        send_clinician_uuid: str,
        new_email: str,
        expected_email: str,
    ) -> None:
        response = client.get(
            flask.url_for(
                "clinicians_api.get_clinician_by_uuid",
                clinician_id=send_clinician_uuid,
                product_name="SEND",
            ),
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        clinician_json = response.json
        assert clinician_json is not None
        clinician_json = {
            k: v
            for k, v in clinician_json.items()
            if k in {"email_address", "first_name", "last_name"}
        }
        assert clinician_json["email_address"] == "kate.wildcat@test.com"
        if new_email == "***DELETE FROM JSON***":
            del clinician_json["email_address"]
        else:
            clinician_json["email_address"] = new_email
        response = client.patch(
            flask.url_for(
                "clinicians_api.update_clinician",
                clinician_id=send_clinician_uuid,
                product_name="SEND",
            ),
            json=clinician_json,
            content_type="application/json",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

        response = client.get(
            flask.url_for(
                "clinicians_api.get_clinician_by_uuid",
                clinician_id=send_clinician_uuid,
                product_name="SEND",
            ),
            headers={"Authorization": "Bearer TOKEN"},
        )

        assert response.status_code == 200
        clinician_json = response.json
        assert response.json is not None
        assert clinician_json["email_address"] == expected_email

    def test_get_clinicians_by_uuids_success(
        self, client: FlaskClient, mocker: MockerFixture, jwt_system: Dict
    ) -> None:
        expected = {"A": {"uuid": "A"}}
        mocker.patch.object(
            controller, "get_clinicians_by_uuids", return_value=expected
        )
        response = client.post(
            "/dhos/v1/clinician_list",
            json=["A"],
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json == expected

    @pytest.mark.parametrize("body", [None, {"key": "value"}, [{}, {}]])
    def test_get_clinicians_by_uuids_error(
        self, client: FlaskClient, body: Dict, jwt_system: Dict
    ) -> None:
        response = client.post(
            "/dhos/v1/clinician_list",
            json=body,
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_remove_clinician_group(
        self,
        client: FlaskClient,
        gdm_clinician_uuid: str,
        mocker: MockerFixture,
    ) -> None:
        from auth0_api_client import authz

        remove_user_from_authz_groups = mocker.patch.object(
            authz, "remove_user_from_authz_groups"
        )

        result = controller.remove_from_clinician(
            gdm_clinician_uuid, {"groups": "GDM Clinician"}
        )
        assert "GDM Clinician" not in result["groups"]
        assert remove_user_from_authz_groups.called_once()

    def test_get_clinician_by_uuid(
        self,
        client: FlaskClient,
        mocker: MockerFixture,
        gdm_clinician_details: Dict,
    ) -> None:

        clinician_uuid: str = str(uuid.uuid4())

        mock_method = mocker.patch.object(
            controller, "get_clinician_by_id", return_value=gdm_clinician_details
        )
        product_name: str = "GDM"
        response = client.get(
            f"/dhos/v1/clinician/{clinician_uuid}?product_name={product_name}",
            headers={"Authorization": "Bearer TOKEN"},
        )

        assert response.status_code == 200
        assert mock_method.call_count == 1
        assert response.headers["Content-Type"] == "application/json"

    def test_get_clinician_by_email(
        self,
        client: FlaskClient,
        mocker: MockerFixture,
        gdm_clinician_details: Dict,
    ) -> None:
        mock_method = mocker.patch.object(
            controller, "get_clinician_by_email", return_value=gdm_clinician_details
        )
        email: str = gdm_clinician_details["email_address"]
        response = client.get(
            f"/dhos/v1/clinician?email={email}",
            headers={"Authorization": "Bearer TOKEN"},
        )

        assert response.status_code == 200
        assert response.json is not None
        assert response.json["email_address"] == gdm_clinician_details["email_address"]
        assert mock_method.call_count == 1
        assert response.headers["Content-Type"] == "application/json"

    def test_get_clinicians_v1(
        self,
        client: FlaskClient,
        mocker: MockerFixture,
        gdm_clinician_details: Dict,
    ) -> None:
        mock_method = mocker.patch.object(
            controller,
            "get_clinicians",
            return_value=([gdm_clinician_details], 1),
        )
        product_name = "GDM"
        response = client.get(
            f"/dhos/v1/clinicians?product_name={product_name}&compact=True",
            headers={"Authorization": "Bearer TOKEN"},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        mock_method.assert_called_once_with(
            login_active=None,
            product_name=product_name,
            temp_only=False,
            compact=True,
            expanded=False,
            modified_since=None,
            q=None,
            offset=None,
            limit=None,
            sort=["last_name", "first_name"],
            order="asc",
        )
        assert response.json is not None
        assert response.json == [gdm_clinician_details]

    def test_get_clinicians_v2(
        self,
        client: FlaskClient,
        mocker: MockerFixture,
        gdm_clinician_details: Dict,
    ) -> None:
        mock_method = mocker.patch.object(
            controller,
            "get_clinicians",
            return_value=([gdm_clinician_details], 1),
        )
        product_name = "GDM"
        response = client.get(
            f"/dhos/v2/clinicians?product_name={product_name}&compact=True",
            headers={"Authorization": "Bearer TOKEN"},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        mock_method.assert_called_once_with(
            login_active=None,
            product_name=product_name,
            temp_only=False,
            compact=True,
            expanded=False,
            modified_since=None,
            q=None,
            offset=None,
            limit=None,
            sort=["last_name", "first_name"],
            order="asc",
        )
        assert response.json is not None
        assert response.json == {
            "results": [gdm_clinician_details],
            "total": 1,
        }

    def test_get_clinicians_v2_with_filters(
        self,
        client: FlaskClient,
        mocker: MockerFixture,
        gdm_clinician_details: Dict,
    ) -> None:
        mock_method: Mock = mocker.patch.object(
            controller,
            "get_clinicians",
            return_value=([gdm_clinician_details], 1),
        )
        product_name = "GDM"
        response = client.get(
            "/dhos/v2/clinicians",
            query_string={
                "product_name": product_name,
                "modified_since": "2000-01-01T01:01:01.123+01:00",
                "compact": True,
                "login_active": True,
                "temp_only": True,
                "q": "smith",
                "offset": 25,
                "limit": 25,
                "sort": ["email_address"],
                "order": "desc",
            },
            headers={"Authorization": "Bearer TOKEN"},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        mock_method.assert_called_once_with(
            login_active=True,
            product_name=product_name,
            temp_only=True,
            compact=True,
            expanded=False,
            modified_since="2000-01-01T01:01:01.123+01:00",
            q="smith",
            offset=25,
            limit=25,
            sort=["email_address"],
            order="desc",
        )
        assert response.json is not None
        assert response.json == {
            "results": [gdm_clinician_details],
            "total": 1,
        }

    def test_update_clinician_password_by_email(
        self,
        mocker: MockerFixture,
        client: FlaskClient,
        gdm_clinician_details: Dict,
    ) -> None:
        mock_method = mocker.patch.object(
            controller,
            "update_clinician_password_by_email",
            return_value=gdm_clinician_details,
        )
        email: str = gdm_clinician_details["email_address"]
        response = client.patch(
            f"/dhos/v1/clinician?email={email}",
            data='{"password" : "abc*_123"}',
            content_type="application/json",
            headers={"Authorization": "Bearer TOKEN"},
        )

        assert response.status_code == 200
        assert mock_method.call_count == 1
        assert response.headers["Content-Type"] == "application/json"

    def test_clinician_login_missing_user_auth(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:

        gdm_clinician_login_response = {
            "user_id": "12345-1234-234",
            "locations": [{"name": "Eastleigh Hospital", "id": "L1"}],
            "nickname": "Jane Smith",
            "email_address": "janesmith@clinic.com",
        }

        mock_method = mocker.patch.object(
            controller,
            "clinician_login",
            return_value=gdm_clinician_login_response,
        )

        response = client.get(
            "/dhos/v1/clinician/login",
            json={},
            headers={
                "Authorization": "Bearer TOKEN",
            },
        )
        assert response.status_code == 400
        assert mock_method.call_count == 0

    def test_get_clinicians_by_location(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:
        location_uuid: str = generate_uuid()
        clinician_uuid: str = generate_uuid()
        mock_get: Mock = mocker.patch.object(
            controller,
            "get_clinicians_at_location",
            return_value=[{"uuid": clinician_uuid}],
        )
        response = client.get(
            f"/dhos/v1/location/{location_uuid}/clinician",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.json is not None
        assert response.status_code == 200
        assert response.json[0]["uuid"] == clinician_uuid
        assert mock_get.call_count == 1
        mock_get.assert_called_with(location_uuid=location_uuid)

    def test_create_clinician_location_bookmark(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:
        clinician_uuid: str = g.jwt_claims["clinician_id"]
        location_uuid: str = generate_uuid()
        mock_post: Mock = mocker.patch.object(
            controller,
            "add_clinician_location_bookmark",
            return_value=[{"uuid": clinician_uuid}],
        )

        url: str = flask.url_for(
            "clinicians_api.create_clinician_location_bookmark",
            clinician_id=clinician_uuid,
            location_id=location_uuid,
        )

        response = client.post(url, headers={"Authorization": "Bearer TOKEN"})
        assert mock_post.call_count == 1
        assert response.status_code == 201

    def test_delete_clinician_location_bookmark(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:
        clinician_uuid: str = g.jwt_claims["clinician_id"]
        location_uuid: str = generate_uuid()
        mock_post: Mock = mocker.patch.object(
            controller,
            "remove_clinician_location_bookmark",
            return_value=[{"uuid": clinician_uuid}],
        )

        url: str = flask.url_for(
            "clinicians_api.delete_clinician_location_bookmark",
            clinician_id=clinician_uuid,
            location_id=location_uuid,
        )

        response = client.delete(url, headers={"Authorization": "Bearer TOKEN"})
        assert mock_post.call_count == 1
        assert response.status_code == 204

    def test_create_clinician_patient_bookmark(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:
        clinician_uuid: str = g.jwt_claims["clinician_id"]
        patient_uuid: str = generate_uuid()
        mock_add: Mock = mocker.patch.object(
            controller,
            "add_clinician_patient_bookmark",
            return_value=[{"uuid": clinician_uuid}],
        )

        url: str = flask.url_for(
            "clinicians_api.create_clinician_patient_bookmark",
            clinician_id=clinician_uuid,
            patient_id=patient_uuid,
        )

        response = client.post(url, headers={"Authorization": "Bearer TOKEN"})
        assert response.status_code == 201
        mock_add.assert_called_once_with(
            clinician_id=clinician_uuid, patient_id=patient_uuid
        )

    def test_delete_clinician_patient_bookmark(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:
        clinician_uuid: str = g.jwt_claims["clinician_id"]
        patient_uuid: str = generate_uuid()
        mock_remove: Mock = mocker.patch.object(
            controller,
            "remove_clinician_patient_bookmark",
            return_value=[{"uuid": clinician_uuid}],
        )

        url: str = flask.url_for(
            "clinicians_api.delete_clinician_patient_bookmark",
            clinician_id=clinician_uuid,
            patient_id=patient_uuid,
        )

        response = client.delete(url, headers={"Authorization": "Bearer TOKEN"})
        assert response.status_code == 204
        mock_remove.assert_called_once_with(
            clinician_id=clinician_uuid, patient_id=patient_uuid
        )

    def test_create_clinician_tos(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:
        clinician_uuid: str = g.jwt_claims["clinician_id"]
        mock_post: Mock = mocker.patch.object(
            controller,
            "create_clinician_tos",
            return_value=[{"uuid": clinician_uuid}],
        )

        url: str = flask.url_for(
            "clinicians_api.create_clinician_tos", clinician_id=clinician_uuid
        )

        response = client.post(
            url,
            headers={"Authorization": "Bearer TOKEN"},
            json={"product_name": "SEND", "version": 1},
        )
        assert mock_post.call_count == 1
        assert response.status_code == 200

    def test_remove_from_clinician(
        self, client: FlaskClient, mocker: MockerFixture
    ) -> None:
        clinician_uuid: str = g.jwt_claims["clinician_id"]
        mock_post: Mock = mocker.patch.object(
            controller,
            "remove_from_clinician",
            return_value=[{"uuid": clinician_uuid}],
        )

        url: str = flask.url_for(
            "clinicians_api.remove_from_clinician", clinician_id=clinician_uuid
        )

        response = client.patch(
            url,
            headers={"Authorization": "Bearer TOKEN"},
            json={"bookmarks": ["UUID_1"]},
        )
        assert mock_post.call_count == 1
        assert response.status_code == 200

    def test_create_clinicians_bulk(
        self,
        client: FlaskClient,
        mocker: MockerFixture,
        bulk_create_clinician_request: list[dict],
        jwt_clinician_migration: None,
    ) -> None:
        mock_post: Mock = mocker.patch.object(
            controller,
            "create_clinicians_bulk",
            return_value={"created": 5},
        )

        response = client.post(
            "/dhos/v1/clinician/bulk",
            headers={"Authorization": "Bearer TOKEN"},
            json=bulk_create_clinician_request,
        )
        assert mock_post.call_count == 1
        assert response.status_code == 200

    def test_get_roles(self, client: FlaskClient, mocker: MockerFixture) -> None:
        mock_get: Mock = mocker.patch.object(
            controller,
            "get_roles",
            return_value={"role1": ["permission1", "permission2"]},
        )
        response = client.get(
            "/dhos/v1/roles",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert mock_get.call_count == 1
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["role1"] == ["permission1", "permission2"]

    def test_clinician_product_patch(
        self,
        client: FlaskClient,
        send_clinician_uuid: str,
    ) -> None:
        response = client.get(
            flask.url_for(
                "clinicians_api.get_clinician_by_uuid",
                clinician_id=send_clinician_uuid,
                product_name="SEND",
            ),
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200

        update = {"products": [{"product_name": "DBM", "opened_date": "2020-12-11"}]}

        response = client.patch(
            flask.url_for(
                "clinicians_api.update_clinician",
                clinician_id=send_clinician_uuid,
                product_name="SEND",
            ),
            json=update,
            content_type="application/json",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert response.json is not None
        assert response.json["products"][0]["product_name"] == "SEND"
        assert response.json["products"][1]["product_name"] == "DBM"
