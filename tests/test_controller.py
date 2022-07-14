import base64
from datetime import date, timedelta
from typing import Dict, List, Optional

import flask
import pytest
from _pytest.logging import LogCaptureFixture
from flask_batteries_included.helpers.error_handler import (
    DuplicateResourceException,
    EntityNotFoundException,
)
from helper import create_clinician
from marshmallow.exceptions import ValidationError
from mock import Mock
from pytest_mock import MockerFixture, MockFixture

from dhos_users_api import roles
from dhos_users_api.blueprint_api import controller
from dhos_users_api.helpers import audit, auth0_authz, publish
from dhos_users_api.models.user import User


@pytest.mark.usefixtures(
    "app", "mock_retrieve_jwt_claims", "mock_bearer_validation", "jwt_clinician_login"
)
class TestClinicianController:
    def test_get_clinicians_by_uuids_success(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )["uuid"]
        clinician_uuid_2 = create_clinician(
            first_name="B",
            last_name="B",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="654",
        )["uuid"]
        clinician_uuid_3 = create_clinician(
            first_name="C",
            last_name="C",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987",
        )["uuid"]

        uuids = [clinician_uuid_1, clinician_uuid_2, clinician_uuid_3]
        results1: Dict = controller.get_clinicians_by_uuids(uuids, compact=True)
        assert len(results1) == 3
        assert "phone_number" not in results1[clinician_uuid_1]
        assert set([k for k, v in results1.items()]) == set(uuids)
        results2: Dict = controller.get_clinicians_by_uuids(uuids, compact=False)
        assert len(results2) == 3
        assert "phone_number" in results2[clinician_uuid_1]
        assert set([k for k, v in results2.items()]) == set(uuids)

    def test_get_clinicians_by_uuids_not_found(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987",
        )["uuid"]

        uuids: List[str] = [clinician_uuid_1, "made_up"]
        results = controller.get_clinicians_by_uuids(uuids, compact=True)
        assert len(results) == 2
        result_clinician_uuid_1 = results[clinician_uuid_1]
        assert (
            result_clinician_uuid_1 is not None
            and result_clinician_uuid_1["uuid"] == clinician_uuid_1
        )
        assert results["made_up"] is None

    def test_get_clinicians_by_uuids_duplicates(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            send_entry_identifier="987",
            login_active=True,
        )["uuid"]

        uuids = [clinician_uuid_1, clinician_uuid_1, clinician_uuid_1]
        results = controller.get_clinicians_by_uuids(uuids, compact=True)
        assert len(results) == 1
        result_clinician_uuid_1 = results[clinician_uuid_1]

        assert (
            result_clinician_uuid_1 is not None
            and result_clinician_uuid_1["uuid"] == clinician_uuid_1
        )

    def test_get_clinicians_by_uuid(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987",
        )["uuid"]
        results = controller.get_clinician_by_id(clinician_uuid_1, get_temp_only=False)
        assert results["first_name"] == "Adam"

    def test_get_clinicians_by_uuid_fail(self) -> None:
        with pytest.raises(EntityNotFoundException):
            controller.get_clinician_by_id("1111", get_temp_only=False)

    def test_get_clinicians_by_uuid_temp_fail(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987",
        )["uuid"]
        with pytest.raises(PermissionError):
            controller.get_clinician_by_id(clinician_uuid_1, get_temp_only=True)

    def test_get_clinicians_by_email(self) -> None:
        clinician = create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            send_entry_identifier="987",
            login_active=True,
        )["uuid"]
        results = controller.get_clinician_by_email("adam.ant@test.com")
        assert results["email_address"] == "adam.ant@test.com"
        assert results["uuid"] == clinician

    def test_get_clinicians_by_email_fail(self) -> None:
        with pytest.raises(EntityNotFoundException):
            controller.get_clinician_by_email("adam.dog@test.com")

    @pytest.mark.parametrize(
        "email",
        ["test.com", "test", "wolrab@test", "@test", "@test.", "test@", "test@."],
    )
    def test_get_clinicians_by_email_invalid_fail(self, email: str) -> None:
        with pytest.raises(ValueError) as e:
            controller.get_clinician_by_email(email=email)
        assert str(e.value) == f"Email {email} is not valid"

    @pytest.mark.parametrize(
        ("auth_string", "username", "password"),
        [
            ("OTQ3MzYyOnBhc3N3b3Jk", "947362", "password"),
            (
                "d29scmFiQG1haWwuY29tOlBhc3NAd29yZDEyMyE=",
                "wolrab@mail.com",
                "Pass@word123!",
            ),
            ("QDk5OTEyMzQ1NjoyMzg3cls2XXc3OA==", "@999123456", "2387r[6]w78"),
        ],
    )
    def test_clinician_credentials(
        self, auth_string: str, username: str, password: str
    ) -> None:
        (
            actual_username,
            actual_password,
        ) = controller.get_clinician_credentials(auth_string)
        assert username == actual_username
        assert password == actual_password

    @pytest.mark.parametrize("username", ["adam.ant@test.com", "321"])
    def test_get_clinician_by_username(self, username: str) -> None:
        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )
        results: Optional[User] = controller.get_clinician_by_username(username)
        assert results is not None and results.last_name == "Ant"

    @pytest.mark.parametrize("username", ["adam.vest@test.com", "333"])
    def test_get_clinician_by_username_fail(
        self, username: str, caplog: LogCaptureFixture
    ) -> None:
        results = controller.get_clinician_by_username(username)
        assert results is None
        assert "Clinician not found" in caplog.text

    def test_validate_clinician_login_fail(self) -> None:
        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )

        clinician = controller.get_clinician_by_username("321")
        results = controller.validate_clinician_login(clinician, "321", "password")
        assert results is False

    def test_validate_clinician_login_none_clinician(
        self, mocker: MockerFixture
    ) -> None:

        mock_method = mocker.patch.object(publish, "audit_message", return_value=None)
        results = controller.validate_clinician_login(
            clinician=None, username="321", password="password"
        )
        assert results is False
        assert mock_method.call_count == 1

    def test_validate_clinician_login_not_login_active(
        self, mocker: MockerFixture
    ) -> None:

        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=False,
            send_entry_identifier="321",
        )

        clinician: Optional[User] = controller.get_clinician_by_username("321")
        mock_method = mocker.patch.object(publish, "audit_message", return_value=None)
        results = controller.validate_clinician_login(
            clinician, username="321", password="password"
        )
        assert results is False
        assert mock_method.call_count == 1

    def test_clinician_login_success(self, mocker: MockerFixture) -> None:
        auth_string: str = "321:password"
        auth: bytes = base64.b64encode(bytes(auth_string, "utf-8"))
        base64_auth_string: str = auth.decode("utf-8")

        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
            groups=["SEND Clinician"],
        )

        mock_method = mocker.patch.object(User, "validate_password", return_value=True)
        login_dict: Optional[Dict] = controller.clinician_login(base64_auth_string)
        assert (
            login_dict is not None
            and login_dict["email_address"] == "adam.ant@test.com"
        )
        assert mock_method.call_count == 1
        assert set(login_dict["permissions"]) == {
            "read:send_clinician",
            "read:send_encounter",
            "read:send_location",
            "read:send_observation",
            "read:send_patient",
            "read:send_pdf",
            "read:send_rule",
            "read:send_trustomer",
            "read:ward_report",
            "write:send_encounter",
            "write:send_observation",
            "write:send_patient",
            "write:send_terms_agreement",
        }

    def test_clinician_login_failed(self, mocker: MockerFixture) -> None:
        auth_string: str = "321:password"
        auth: bytes = base64.b64encode(bytes(auth_string, "utf-8"))
        base64_auth_string: str = auth.decode("utf-8")

        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )

        mocker.patch.object(User, "validate_password", return_value=False)

        with pytest.raises(PermissionError):
            login_dict: Optional[Dict] = controller.clinician_login(base64_auth_string)

    def test_clinician_login_no_password_failed(self, mocker: MockerFixture) -> None:
        auth_string: str = "321:"
        auth: bytes = base64.b64encode(bytes(auth_string, "utf-8"))
        base64_auth_string: str = auth.decode("utf-8")

        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )

        with pytest.raises(PermissionError):
            controller.clinician_login(base64_auth_string)

    def test_validate_clinician_login(self, mocker: MockerFixture) -> None:
        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )

        mock_method = mocker.patch.object(User, "validate_password", return_value=True)
        clinician: Optional[User] = controller.get_clinician_by_username("321")
        results = controller.validate_clinician_login(clinician, "321", "password")
        assert results is True
        assert mock_method.call_count == 1

    @pytest.mark.parametrize("send_welcome_email", [True, False])
    def test_create_and_publish_clinician(
        self, mocker: MockerFixture, send_welcome_email: bool
    ) -> None:
        dummy_clinician = {
            "first_name": "Crash",
            "last_name": "Test",
            "job_title": "dummy",
            "phone_number": "",
            "groups": ["SEND Clinician"],
            "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
            "locations": [],
            "nhs_smartcard_number": "654987",
            "send_entry_identifier": "1323456",
            "email_address": "crash.dummy@test.com",
            "can_edit_ews": False,
            "contract_expiry_eod_date": None,
            "login_active": True,
        }

        mock_methods: List[Mock] = [
            mocker.patch.object(
                auth0_authz, "add_user_to_authz_groups", return_value=None
            ),
            mocker.patch.object(publish, "clinician_creation_event", return_value=None),
        ]
        mock_email_notification = mocker.patch.object(
            publish, "welcome_email_notification", return_value=None
        )

        clinician: User = controller._create_and_publish_clinician(
            dummy_clinician, send_welcome_email=send_welcome_email
        )

        for mock_method in mock_methods:
            assert mock_method.call_count == 1

        assert mock_email_notification.call_count == (1 if send_welcome_email else 0)

        assert isinstance(clinician, User)
        assert hasattr(clinician, "login_active")

    def test_create_clinician_no_product_fail(
        self,
    ) -> None:
        dummy_clinician = {
            "first_name": "hilary",
            "last_name": "jones",
            "nhs_smartcard_number": "123",
            "products": [],
            "phone_number": "12321312323",
            "job_title": "Doctor",
            "locations": ["L1"],
            "groups": [],
        }
        data = flask.jsonify(dummy_clinician)
        with pytest.raises(ValidationError):
            controller.create_clinician(data.json, send_welcome_email=False)

    def test_clinician_login_before_last_day(self, mocker: MockerFixture) -> None:
        mocker.patch.object(controller, "g", Mock(jwt_claims={"clinician_id": "123"}))
        clinician = User()
        clinician.uuid = "some-uuid"
        clinician.login_active = True
        clinician.contract_expiry_eod_date = date.today() + timedelta(days=1)
        mocker.patch.object(User, "validate_password", return_value=True)
        result = controller.validate_clinician_login(clinician, "username", "password")
        assert result is True

    def test_clinician_login_last_day(self, mocker: MockerFixture) -> None:
        mocker.patch.object(controller, "g", Mock(jwt_claims={"clinician_id": "123"}))
        clinician = User()
        clinician.uuid = "some-uuid"
        clinician.login_active = True
        clinician.contract_expiry_eod_date = date.today()
        mocker.patch.object(User, "validate_password", return_value=True)
        result = controller.validate_clinician_login(clinician, "username", "password")
        assert result is True

    def test_clinician_login_after_last_day(self, mocker: MockerFixture) -> None:
        mocker.patch.object(controller, "g", Mock(jwt_claims={"clinician_id": "123"}))
        mocker.patch.object(audit, "record_authentication_failure", Mock())
        mocker.patch.object(controller, "deactivate_clinician", Mock())
        clinician = User()
        clinician.uuid = "some-uuid"
        clinician.login_active = True
        clinician.contract_expiry_eod_date = date.today() + timedelta(days=-1)
        mocker.patch.object(User, "validate_password", return_value=True)
        result = controller.validate_clinician_login(clinician, "username", "password")
        assert result is False

    @pytest.mark.parametrize(
        "password", ["Pass@word123", "nonascii£££", "this one has spaces", "ééé", "👌"]
    )
    def test_update_clinician_password_by_email(self, password: str) -> None:
        clinician_uuid: str = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            send_entry_identifier="456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            groups=["SEND Superclinician", "SEND Clinician"],
            email_address="some@mail.com",
        )["uuid"]
        clinician = User.query.get(clinician_uuid)
        clinician.set_password(password)
        controller.update_clinician_password_by_email(clinician.email_address, password)
        result = controller.validate_clinician_login(
            clinician=clinician, username=clinician.email_address, password=password
        )
        assert result is True

    def test_clinician_duplicate_email(self, mocker: MockerFixture) -> None:
        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="654321",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
            email_address="duplicate@mail.com",
        )

        uid2 = create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="132",
            email_address="not.yet.duplicate@mail.com",
        )["uuid"]

        with pytest.raises(DuplicateResourceException):
            controller.update_clinician(
                clinician_id=uid2,
                update_fields={"email_address": "duplicate@mail.com"},
                edit_temp_only=False,
            )

    def test_clinician_duplicate_identifier(self, mocker: MockerFixture) -> None:
        create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="654321",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
            email_address="duplicate@mail.com",
        )

        uid2 = create_clinician(
            first_name="Adam",
            last_name="Ant",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
            email_address="not.yet.duplicate@mail.com",
        )["uuid"]

        with pytest.raises(DuplicateResourceException):
            controller.update_clinician(
                clinician_id=uid2,
                update_fields={"email_address": "duplicate@mail.com"},
                edit_temp_only=False,
            )

    def test_create_clinician_tos(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )["uuid"]
        clinician_tos = {"product_name": "SEND", "version": 1}
        tos = controller.create_clinician_tos(clinician_uuid_1, clinician_tos)
        assert tos["product_name"] == "SEND"

    def test_update_clinician_products(
        self,
    ) -> None:
        clinician_uuid_1: str = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="GDM",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )["uuid"]
        updates = {"products": [{"product_name": "DBM", "opened_date": "2020-12-11"}]}
        updated_clinician = controller.update_clinician(
            clinician_id=clinician_uuid_1, update_fields=updates, edit_temp_only=False
        )
        assert {prod["product_name"] for prod in updated_clinician["products"]} == {
            "GDM",
            "DBM",
        }

    def test_update_clinician_bookmarked_patients(
        self,
    ) -> None:
        clinician_uuid_1: str = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="GDM",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )["uuid"]
        updates = {"bookmarked_patients": ["P1"]}
        updated_clinician = controller.update_clinician(
            clinician_id=clinician_uuid_1, update_fields=updates, edit_temp_only=False
        )
        assert updated_clinician["bookmarked_patients"] == ["P1"]

    def test_update_clinician_groups(
        self,
    ) -> None:
        clinician_uuid_1: str = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="GDM",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )["uuid"]
        updates = {"groups": ["DBM Clinician"]}
        updated_clinician = controller.update_clinician(
            clinician_id=clinician_uuid_1, update_fields=updates, edit_temp_only=False
        )
        assert updated_clinician["groups"] == ["DBM Clinician", "SEND Clinician"]

    def test_update_clinician_locs(
        self,
    ) -> None:
        clinician_uuid_1: str = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="GDM",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )["uuid"]
        updates = {"bookmarks": ["L1"], "locations": ["L2", "L3"]}
        updated_clinician = controller.update_clinician(
            clinician_id=clinician_uuid_1, update_fields=updates, edit_temp_only=False
        )
        assert updated_clinician["bookmarks"] == ["L1"]
        assert updated_clinician["locations"] == ["L2", "L3"]

    def test_update_clinician_ews(
        self,
    ) -> None:
        clinician_uuid_1: str = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
            groups=["SEND Superclinician"],
        )["uuid"]
        create_clinician(
            first_name="J",
            last_name="T",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="AAA",
            groups=["SEND Administrator"],
            uuid="JWT_USER_ID",
        )
        updates = {"can_edit_ews": True}
        updated_clinician = controller.update_clinician(
            clinician_id=clinician_uuid_1, update_fields=updates, edit_temp_only=False
        )
        assert updated_clinician["can_edit_ews"] == True

    def test_update_clinician_inactive(self) -> None:
        clinician_uuid_1: str = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="GDM",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )["uuid"]
        updates = {"login_active": False}
        updated_clinician = controller.update_clinician(
            clinician_uuid_1,
            update_fields=updates,
            edit_temp_only=False,
        )
        assert updated_clinician["login_active"] == False

    def test_update_clinician_product_closed(self) -> None:
        clinician: Dict = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="GDM",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )

        updates = {
            "products": [
                {
                    "uuid": clinician["products"][0]["uuid"],
                    "product_name": "GDM",
                    "closed_date": "2020-12-11",
                }
            ]
        }
        updated_clinician = controller.update_clinician(
            clinician["uuid"],
            update_fields=updates,
            edit_temp_only=False,
        )
        assert str(updated_clinician["products"][0]["closed_date"]) == "2020-12-11"

    def test_update_clinician_duplicate_product_update(self) -> None:
        clinician: Dict = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="GDM",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )

        updates = {"products": [{"product_name": "DBM"}]}
        controller.update_clinician(
            clinician["uuid"],
            update_fields=updates,
            edit_temp_only=False,
        )
        with pytest.raises(ValueError):
            controller.update_clinician(
                clinician_id=clinician["uuid"],
                update_fields={
                    "products": [
                        {
                            "uuid": clinician["products"][0]["uuid"],
                            "product_name": "DBM",
                        }
                    ]
                },
                edit_temp_only=False,
            )

    def test_create_temp_clinician(self) -> None:
        details: Dict = {
            "first_name": "Temp",
            "last_name": "Test",
            "job_title": "Transitory",
            "phone_number": "",
            "groups": ["SEND Clinician"],
            "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
            "locations": [],
            "nhs_smartcard_number": "654987",
            "send_entry_identifier": "1323456",
            "email_address": "crash.dummy@test.com",
            "can_edit_ews": False,
            "contract_expiry_eod_date": str(date.today() + timedelta(days=1)),
            "login_active": True,
        }
        clinician: Dict = controller.create_clinician(clinician_details=details)
        assert (
            str(clinician["contract_expiry_eod_date"])
            == details["contract_expiry_eod_date"]
        )

    def test_create_temp_clinician_no_id(self) -> None:
        details: Dict = {
            "first_name": "Temp",
            "last_name": "Test",
            "job_title": "Transitory",
            "phone_number": "",
            "groups": ["SEND Clinician"],
            "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
            "locations": [],
            "nhs_smartcard_number": "654987",
            "email_address": "crash.dummy@test.com",
            "can_edit_ews": False,
            "contract_expiry_eod_date": str(date.today() + timedelta(days=1)),
            "login_active": True,
        }
        clinician: Dict = controller.create_clinician(clinician_details=details)
        assert clinician["send_entry_identifier"] != None

    def test_create_temp_clinician_failed(self) -> None:
        details: Dict = {
            "first_name": "Temp",
            "last_name": "Test",
            "job_title": "Transitory",
            "phone_number": "",
            "groups": ["SEND Clinician"],
            "products": [{"product_name": "SEND", "opened_date": "2021-7-19"}],
            "locations": [],
            "nhs_smartcard_number": "654987",
            "send_entry_identifier": "1323456",
            "email_address": "crash.dummy@test.com",
            "can_edit_ews": True,
            "contract_expiry_eod_date": str(date.today() + timedelta(days=1)),
            "login_active": True,
        }
        with pytest.raises(ValueError):
            controller.create_clinician(clinician_details=details)

    def test_update_clinician_fail_duplicate_email(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            send_entry_identifier="A321",
            login_active=True,
            groups=["SEND Superclinician"],
        )["uuid"]
        create_clinician(
            first_name="A",
            last_name="B",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="B321",
            groups=["SEND Superclinician"],
        )
        with pytest.raises(DuplicateResourceException):
            updates = {"first_name": "Geoff", "email_address": "a.b@test.com"}
            controller.update_clinician(clinician_uuid_1, updates, False)

    def test_update_clinician_fail_duplicate_user(self) -> None:
        create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            email_address="a.a@test.com",
            product_name="SEND",
            expiry=None,
            send_entry_identifier="A321",
            login_active=True,
            groups=["SEND Superclinician"],
        )
        uuid_2 = create_clinician(
            first_name="A",
            last_name="B",
            nhs_smartcard_number="123456",
            email_address="a.b@test.com",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="a.a@test.com",
            groups=["SEND Superclinician"],
        )["uuid"]
        assert None == controller.get_clinician_by_username("a.a@test.com")
        c2 = controller.get_clinician_by_username("a.b@test.com")
        if c2:
            assert uuid_2 == c2.uuid
        else:
            assert False

    def test_remove_from_clinician(self, mocker: MockerFixture) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
            locations=["LOC1", "LOC2"],
            groups=["SEND Superclinician", "SEND Clinician"],
        )["uuid"]
        updates = {"groups": ["SEND Superclinician"], "locations": ["LOC1"]}
        mock_update = mocker.patch.object(
            publish, "clinician_update_event", return_value=None
        )
        mock_authz = mocker.patch.object(
            auth0_authz, "remove_user_from_authz_groups", return_value=None
        )
        clinician_data = controller.remove_from_clinician(clinician_uuid_1, updates)
        assert clinician_data["groups"] == ["SEND Clinician"]
        assert clinician_data["locations"] == ["LOC2"]
        assert mock_update.call_count == 1
        assert mock_authz.call_count == 1

    def test_remove_from_clinician_after_update(self, mocker: MockerFixture) -> None:
        clinician = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
            locations=["LOC1", "LOC2"],
            groups=["SEND Superclinician", "SEND Clinician"],
        )
        clinician_uuid = clinician["uuid"]
        product_uuid = clinician["products"][0]["uuid"]
        add = {
            "bookmarks": ["L1", "L2"],
            "bookmarked_patients": ["P1", "P2"],
            "products": [{"product_name": "DBM", "opened_date": "2021-01-01"}],
        }
        remove = {
            "bookmarks": ["L2"],
            "bookmarked_patients": ["P1"],
            "products": [{"uuid": product_uuid}],
        }
        mock_update = mocker.patch.object(
            publish, "clinician_update_event", return_value=None
        )

        controller.update_clinician(clinician_uuid, add, False)
        clinician_data = controller.remove_from_clinician(clinician_uuid, remove)
        assert clinician_data["bookmarks"] == ["L1"]
        assert clinician_data["bookmarked_patients"] == ["P2"]
        assert len(clinician_data["products"]) == 1
        assert clinician_data["products"][0]["product_name"] == "DBM"
        assert mock_update.call_count == 2

    def test_generate_send_entry_identifier(self) -> None:
        clinician_data = controller._generate_send_entry_identifier()
        assert len(clinician_data) == 10

    def test_clinician_can_not_set_sp02_scale_when_not_send_clinician(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(controller, "g", Mock(jwt_claims={"clinician_id": "123"}))
        with pytest.raises(ValueError):
            controller.ensure_current_user_can_allow_ews_change_permissions(
                clinician_groups=[], contract_expiry_eod_date=None
            )

    def test_clinician_can_not_set_sp02_scale_when_temp(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(controller, "g", Mock(jwt_claims={"clinician_id": "123"}))
        with pytest.raises(ValueError):
            controller.ensure_current_user_can_allow_ews_change_permissions(
                clinician_groups=["SEND Clinician"],
                contract_expiry_eod_date=date.today() + timedelta(days=1),
            )

    def test_get_clinicians_at_location(self) -> None:
        create_clinician(
            first_name="A",
            last_name="AA",
            nhs_smartcard_number="123456",
            send_entry_identifier="@123456789",
            product_name="GDM",
            expiry=None,
            login_active=True,
            groups=["GDM Clinician"],
            locations=["LOCATION_UUID"],
        )
        result = controller.get_clinicians_at_location("LOCATION_UUID")
        assert len(result) == 1

    def test_deactivate_clinician(self, mocker: MockFixture) -> None:
        clinician = create_clinician(
            first_name="A",
            last_name="AA",
            nhs_smartcard_number="123456",
            send_entry_identifier="@123456789",
            product_name="GDM",
            expiry=None,
            login_active=True,
            groups=["GDM Clinician"],
            locations=["LOCATION_UUID"],
        )
        mock_method = mocker.patch.object(
            publish, "clinician_update_event", return_value=None
        )
        controller.deactivate_clinician(clinician["uuid"])

        assert mock_method.call_count == 1

    def test_ensure_current_user_can_allow_ews_change_permissions_fails_with_no_admin(
        self,
    ) -> None:
        clinician_groups = ["SEND Clinician"]
        with pytest.raises(PermissionError):
            controller.ensure_current_user_can_allow_ews_change_permissions(
                clinician_groups, None
            )

    def test_create_clinician_can_edit_ews_fail(
        self,
    ) -> None:
        dummy_clinician = {
            "first_name": "hilary",
            "last_name": "jones",
            "nhs_smartcard_number": "123456",
            "products": [{"product_name": "SEND", "opened_date": "2021-01-01"}],
            "phone_number": "12321312323",
            "job_title": "Doctor",
            "locations": ["L1"],
            "groups": ["SEND Clinician"],
            "can_edit_ews": True,
        }
        data = flask.jsonify(dummy_clinician)
        with pytest.raises(PermissionError):
            controller.create_clinician(data.json, False)

    def test_get_clinicians_not_compact(self) -> None:
        create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987654",
            groups=["SEND Superclinician", "SEND Clinician"],
        )

        clinician_data, _ = controller.get_clinicians(
            login_active=True, product_name="SEND", temp_only=False, compact=False
        )
        assert "locations" in clinician_data[0]
        assert "phone_number" not in clinician_data[0]

    def test_get_clinicians_empty(self) -> None:
        create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987654",
            groups=["SEND Superclinician", "SEND Clinician"],
        )

        clinician_data, _ = controller.get_clinicians(
            login_active=True,
            product_name="FAKE",
            temp_only=True,
            compact=False,
            expanded=True,
            modified_since="2020-01-01",
        )
        assert clinician_data == []

    def test_get_clinicians_expanded(self) -> None:
        create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987654",
            groups=["SEND Superclinician", "SEND Clinician"],
        )

        clinician_data, _ = controller.get_clinicians(
            login_active=True,
            product_name="SEND",
            temp_only=False,
            compact=False,
            expanded=True,
        )
        assert "phone_number" in clinician_data[0]

    @pytest.mark.parametrize(
        "q",
        (
            None,
            "Mich",
            "Michael",
            "Michelle",
            "SEND",
            "SEND Clinician",
            "SEND Superclinician",
            "666666",
            "666",
        ),
    )
    def test_get_clinicians_filter(self, q: Optional[str]) -> None:
        clinician1_uuid = create_clinician(
            first_name="Michael",
            last_name="Gibson",
            nhs_smartcard_number="123",
            product_name="SEND",
            expiry=None,
            login_active=True,
            groups=["SEND Clinician"],
            email_address="michael@gibson.com",
            send_entry_identifier="666666",
        )["uuid"]
        clinician2_uuid = create_clinician(
            first_name="Michelle",
            last_name="Gibson",
            nhs_smartcard_number="321",
            product_name="SEND",
            expiry=None,
            login_active=True,
            groups=["SEND Superclinician"],
            email_address="michelle@gibson.com",
            send_entry_identifier="666",
        )["uuid"]

        clinicians, total = controller.get_clinicians(
            login_active=True, product_name="SEND", q=q
        )

        clinician_uuids = [x["uuid"] for x in clinicians]

        if q in (None, "Mich", "SEND"):
            assert len(clinicians) == 2
            assert total == 2
            assert (
                clinician1_uuid in clinician_uuids
                and clinician2_uuid in clinician_uuids
            )

        if q in ("Michael", "SEND Clinician", "666666"):
            assert len(clinicians) == 1
            assert total == 1
            assert (
                clinician1_uuid in clinician_uuids
                and clinician2_uuid not in clinician_uuids
            )

        if q in ("Michelle", "SEND Superclinician", "666"):
            assert len(clinicians) == 1
            assert total == 1
            assert (
                clinician2_uuid in clinician_uuids
                and clinician1_uuid not in clinician_uuids
            )

    @pytest.mark.parametrize("offset", (0, 25))
    @pytest.mark.parametrize("limit", (25, 50))
    @pytest.mark.parametrize("order", ("asc", "desc"))
    def test_get_clinicians_pagination(
        self, offset: int, limit: int, order: str
    ) -> None:
        clinicians_data: List[Dict] = [
            {
                "first_name": f"First Name {i}",
                "last_name": f"Last Name {i}",
                "nhs_smartcard_number": str(i),
                "product_name": "SEND",
                "expiry": None,
                "login_active": True,
                "groups": ["SEND Clinician"],
                "email_address": f"some_address_{i}@email.com",
                "send_entry_identifier": str(i),
            }
            for i in range(100)
        ]

        for data in clinicians_data:
            create_clinician(**data)

        clinicians_expected = list(
            sorted(
                clinicians_data,
                key=lambda c: c["send_entry_identifier"],  # type: ignore
                reverse=(order == "desc"),
            )
        )[offset : offset + limit]

        clinicians, total = controller.get_clinicians(
            login_active=True,
            product_name="SEND",
            offset=offset,
            limit=limit,
            sort=["send_entry_identifier"],
            order=order,
        )

        assert total == 100
        assert len(clinicians) == limit
        for i in range(len(clinicians)):
            assert (
                clinicians_expected[i]["send_entry_identifier"]
                == clinicians[i]["send_entry_identifier"]
            )

    def test_add_clinician_location_bookmark(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987654",
            groups=["SEND Superclinician", "SEND Clinician"],
        )["uuid"]
        controller.add_clinician_location_bookmark(clinician_uuid_1, "LOC1")
        clinician = controller.get_clinician_by_id(
            clinician_uuid_1, get_temp_only=False
        )
        assert clinician["bookmarks"] == ["LOC1"]
        controller.add_clinician_location_bookmark(clinician_uuid_1, "LOC2")
        clinician = controller.get_clinician_by_id(
            clinician_uuid_1, get_temp_only=False
        )
        assert clinician["bookmarks"] == ["LOC1", "LOC2"]

    def test_rem_clinician_location_bookmark(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987654",
            groups=["SEND Superclinician", "SEND Clinician"],
        )["uuid"]
        controller.add_clinician_location_bookmark(clinician_uuid_1, "LOC1")
        controller.add_clinician_location_bookmark(clinician_uuid_1, "LOC2")
        controller.remove_clinician_location_bookmark(clinician_uuid_1, "LOC1")
        clinician = controller.get_clinician_by_id(
            clinician_uuid_1, get_temp_only=False
        )
        assert clinician["bookmarks"] == ["LOC2"]

    def test_sys_user(self, mocker: MockerFixture) -> None:
        mocker.patch.object(controller, "g", Mock(jwt_claims={"system_id": "123"}))
        controller.ensure_current_user_can_allow_ews_change_permissions(
            clinician_groups=[], contract_expiry_eod_date=None
        )

    def test_add_clinician_patient_bookmark(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987654",
            groups=["SEND Superclinician", "SEND Clinician"],
        )["uuid"]
        controller.add_clinician_patient_bookmark(clinician_uuid_1, "PAT1")
        clinician = controller.get_clinician_by_id(
            clinician_uuid_1, get_temp_only=False
        )
        assert clinician["bookmarked_patients"] == ["PAT1"]
        controller.add_clinician_patient_bookmark(clinician_uuid_1, "PAT2")
        clinician = controller.get_clinician_by_id(
            clinician_uuid_1, get_temp_only=False
        )
        assert clinician["bookmarked_patients"] == ["PAT1", "PAT2"]

    def test_rem_clinician_patient_bookmark(self) -> None:
        clinician_uuid_1 = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="987654",
            groups=["SEND Superclinician", "SEND Clinician"],
        )["uuid"]
        controller.add_clinician_patient_bookmark(clinician_uuid_1, "PAT1")
        controller.add_clinician_patient_bookmark(clinician_uuid_1, "PAT2")
        controller.remove_clinician_patient_bookmark(clinician_uuid_1, "PAT1")
        clinician = controller.get_clinician_by_id(
            clinician_uuid_1, get_temp_only=False
        )
        assert clinician["bookmarked_patients"] == ["PAT2"]

    @pytest.mark.parametrize(
        "edit_temp_only,is_permanent_clinician,update_fields",
        [
            (True, True, {}),
            (True, False, {"groups": ["NEW FAKE GROUP"]}),
        ],
    )
    def test_check_temp_edit_permissions(
        self, edit_temp_only: bool, is_permanent_clinician: bool, update_fields: Dict
    ) -> None:
        with pytest.raises(PermissionError):
            controller._check_temp_edit_permissions(
                edit_temp_only, is_permanent_clinician, update_fields
            )

    def test_create_clinician_bulk(
        self, mocker: MockerFixture, bulk_create_clinician_request: list[dict]
    ) -> None:
        # Arrange
        mock_add_auth0 = mocker.patch.object(auth0_authz, "add_user_to_authz_groups")
        mock_publish = mocker.patch.object(publish, "clinician_creation_event")
        mock_email = mocker.patch.object(publish, "welcome_email_notification")

        # Act
        result: Dict = controller.create_clinicians_bulk(
            clinician_details=[
                c.copy() for c in bulk_create_clinician_request  # original gets mutated
            ]
        )

        # Assert
        assert result["created"] == 5
        db_users: List[User] = User.query.all()
        assert len(db_users) == 5
        assert {u.uuid for u in db_users} == {
            c["uuid"] for c in bulk_create_clinician_request
        }
        # Creating clinicians in bulk shouldn't trigger all the usual stuff we do when a clinician is created.
        assert mock_add_auth0.call_count == 0
        assert mock_publish.call_count == 0
        assert mock_email.call_count == 0

    def test_get_roles(self, mocker: MockerFixture) -> None:
        mocker.patch.object(
            roles,
            "get_role_map",
            return_value={"role1": ["permission1", "permission2"]},
        )
        role_map = controller.get_roles()
        assert role_map["role1"] == ["permission1", "permission2"]
