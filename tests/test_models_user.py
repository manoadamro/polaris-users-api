import pytest
from helper import create_clinician

from dhos_users_api.models.user import User


@pytest.mark.usefixtures(
    "app", "mock_retrieve_jwt_claims", "mock_bearer_validation", "jwt_clinician_login"
)
class TestModelsUser:
    def make_user(self) -> User:
        clinician_uuid: str = create_clinician(
            first_name="A",
            last_name="A",
            nhs_smartcard_number="123456",
            product_name="SEND",
            expiry=None,
            login_active=True,
            send_entry_identifier="321",
        )["uuid"]
        return User.query.get(clinician_uuid)

    def test_schema(self) -> None:
        assert User.schema()["optional"] == {
            "login_active": bool,
            "contract_expiry_eod_date": str,
            "send_entry_identifier": str,
            "bookmarks": [str],
            "bookmarked_patients": [str],
            "can_edit_encounter": bool,
            "can_edit_ews": bool,
            "professional_registration_number": str,
            "agency_name": str,
            "agency_staff_employee_number": str,
            "email_address": str,
            "booking_reference": str,
            "analytics_consent": bool,
        }

    def test_update(self) -> None:
        clinician: User = self.make_user()
        clinician.update(
            groups=["GDM Clinician"],
            bookmarks=["LOCATION_UUID_2"],
            bookmarked_patients=["PATIENT_UUID_1"],
            locations=["LOCATION_UUID_1"],
            products=[
                {
                    "uuid": clinician.products[0].uuid,
                    "product_name": "SEND",
                    "opened_date": "2021-07-01",
                    "closed_date": "2021-07-02",
                }
            ],
        )
        assert str(clinician.products[0].opened_date) == "2021-07-01"
        assert clinician.locations[0] == "LOCATION_UUID_1"
        assert clinician.bookmarks[0] == "LOCATION_UUID_2"
        assert clinician.bookmarked_patients[0] == "PATIENT_UUID_1"

    def test_duplicate_product_update(self) -> None:
        clinician: User = self.make_user()
        with pytest.raises(ValueError):
            clinician.update(
                products=[
                    {
                        "uuid": clinician.products[0].uuid,
                        "product_name": "SEND",
                        "opened_date": "2021-07-01",
                    },
                    {
                        "product_name": "SEND",
                        "opened_date": "2021-07-01",
                    },
                ],
            )

    def test_generate_secure_random_string_fail(self) -> None:
        clinician: User = self.make_user()
        with pytest.raises(ValueError):
            clinician.generate_secure_random_string(2)

    def test_generate_password_hash_fail(self) -> None:
        clinician: User = self.make_user()
        with pytest.raises(RuntimeError):
            clinician.generate_password_hash("1234")

    def test_validate_password_fail(self) -> None:
        clinician: User = self.make_user()
        clinician.set_password("inconceivable")
        assert clinician.validate_password("1234") == False

    def test_analytics_consent(self) -> None:
        clinician: User = self.make_user()
        assert "analytics_consent" not in clinician.to_dict()

        clinician.analytics_consent = True
        assert clinician.to_dict()["analytics_consent"] == True

    def test_update_bookmarks(self) -> None:
        clinician: User = self.make_user()
        clinician.update(bookmarks=["LOC1"])
        assert clinician.to_dict()["bookmarks"] == ["LOC1"]
        clinician.update(bookmarks=["LOC2"])
        assert clinician.to_dict()["bookmarks"] == ["LOC2"]

    def test_update_bookmarked_patients(self) -> None:
        clinician: User = self.make_user()
        clinician.update(bookmarked_patients=["P1"])
        assert clinician.to_dict()["bookmarked_patients"] == ["P1"]
        clinician.update(bookmarked_patients=["P2"])
        assert clinician.to_dict()["bookmarked_patients"] == ["P2"]

    def test_update_products(self) -> None:
        clinician: User = self.make_user()
        clinician.update(
            products=[{"product_name": "DBM", "opened_date": "2021-08-01"}]
        )
        assert clinician.to_dict()["products"][1]["product_name"] == "DBM"
