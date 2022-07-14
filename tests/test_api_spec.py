import pytest
from marshmallow import ValidationError

from dhos_users_api.models.api_spec import validate_identifier


@pytest.mark.usefixtures(
    "app", "mock_retrieve_jwt_claims", "mock_bearer_validation", "jwt_clinician_login"
)
class TestModelsUser:
    def test_validate_identifier(self) -> None:
        validate_identifier("")
        validate_identifier({"uuid": "123465", "first_name": "A", "last_name": "B"})
        with pytest.raises(ValidationError):
            validate_identifier([])
