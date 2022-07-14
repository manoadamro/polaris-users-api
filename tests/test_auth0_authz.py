import pytest
from auth0_api_client import authz as auth0_authz
from pytest_mock import MockerFixture

from dhos_users_api.helpers.auth0_authz import (
    add_user_to_authz_groups,
    remove_user_from_authz_groups,
)


@pytest.mark.usefixtures(
    "app", "mock_retrieve_jwt_claims", "mock_bearer_validation", "jwt_clinician_login"
)
class TestAuth0Authz:
    def test_remove_user_from_authz_groups(self, mocker: MockerFixture) -> None:
        remove_user_from_authz_groups(
            user_id="UUID_1", groups_to_remove_from=["GROUP_1"]
        )
        mock_method = mocker.patch.object(
            auth0_authz, "remove_user_from_authz_groups", return_value=None
        )
        assert mock_method.call_count == 0

    def test_add_user_from_authz_groups(self, mocker: MockerFixture) -> None:
        add_user_to_authz_groups(user_id="UUID_1", groups_to_add_to=["GROUP_1"])
        mock_method = mocker.patch.object(
            auth0_authz, "add_user_to_authz_groups", return_value=None
        )
        assert mock_method.call_count == 0
