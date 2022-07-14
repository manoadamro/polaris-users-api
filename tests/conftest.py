import os
import signal
import socket
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Generator, List, NoReturn, Tuple
from unittest.mock import Mock
from urllib.parse import urlparse

import kombu_batteries_included
import pytest
from flask import Flask, g
from flask_batteries_included.config import RealSqlDbConfig
from pytest_mock import MockerFixture, MockFixture


#####################################################
# Configuration to use postgres started by tox-docker
#####################################################
def pytest_configure(config: Any) -> None:
    for env_var, tox_var in [
        ("DATABASE_HOST", "POSTGRES_HOST"),
        ("DATABASE_PORT", "POSTGRES_5432_TCP_PORT"),
    ]:
        if tox_var in os.environ:
            os.environ[env_var] = os.environ[tox_var]

    import logging

    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if os.environ.get("SQLALCHEMY_ECHO") else logging.WARNING
    )


def pytest_report_header(config: Any) -> str:
    db_config = (
        f"{os.environ['DATABASE_HOST']}:{os.environ['DATABASE_PORT']}"
        if os.environ.get("DATABASE_PORT")
        else "Sqlite"
    )
    return f"SQL database: {db_config}"


def _wait_for_it(service: str, timeout: int = 30) -> None:
    url = urlparse(service, scheme="http")

    host = url.hostname
    port = url.port or (443 if url.scheme == "https" else 80)

    friendly_name = f"{host}:{port}"

    def _handle_timeout(signum: Any, frame: Any) -> NoReturn:
        print(f"timeout occurred after waiting {timeout} seconds for {friendly_name}")
        sys.exit(1)

    if timeout > 0:
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(timeout)
        print(f"waiting {timeout} seconds for {friendly_name}")
    else:
        print(f"waiting for {friendly_name} without a timeout")

    t1 = time.time()

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s = sock.connect_ex((host, port))
            if s == 0:
                seconds = round(time.time() - t1)
                print(f"{friendly_name} is available after {seconds} seconds")
                break
        except socket.gaierror:
            pass
        finally:
            time.sleep(1)

    signal.alarm(0)


#####################################################
# End Configuration to use postgresql started by tox-docker
#####################################################


@pytest.fixture(scope="session")
def session_app() -> Flask:
    import dhos_users_api.app

    app = dhos_users_api.app.create_app(testing=True)
    if os.environ.get("DATABASE_PORT"):
        # Override fbi use of sqlite to run tests with Postgres
        app.config.from_object(RealSqlDbConfig())
    return app


@pytest.fixture
def app(mocker: MockFixture, session_app: Flask) -> Flask:
    from flask_batteries_included.helpers.security import _ProtectedRoute

    def mock_claims(self: Any, verify: bool = True) -> Tuple:
        return g.jwt_claims, g.jwt_scopes

    mocker.patch.object(_ProtectedRoute, "_retrieve_jwt_claims", mock_claims)
    session_app.config["IGNORE_JWT_VALIDATION"] = False
    session_app.config["DISABLE_CREATE_USER_IN_AUTH0"] = True
    session_app.config["UNITTESTING"] = True
    session_app.config["ENVIRONMENT"] = "DEVELOPMENT"
    return session_app


@pytest.fixture
def app_context(app: Flask) -> Generator[None, None, None]:
    with app.app_context():
        yield


@pytest.fixture
def mock_publish(mocker: MockFixture) -> Mock:
    return mocker.patch.object(kombu_batteries_included, "publish_message")


@pytest.fixture(autouse=True)
def uses_sql_database() -> None:
    from flask_batteries_included.sqldb import db

    db.drop_all()
    db.create_all()


@pytest.fixture
def mock_retrieve_jwt_claims(app: Flask, mocker: MockerFixture) -> Mock:
    from flask_batteries_included.helpers.security import _ProtectedRoute

    def mock_claims(self: Any, verify: bool = True) -> Tuple:
        return g.jwt_claims, g.jwt_scopes

    app.config["IGNORE_JWT_VALIDATION"] = False

    return mocker.patch.object(_ProtectedRoute, "_retrieve_jwt_claims", mock_claims)


@pytest.fixture
def mock_bearer_validation(mocker: MockerFixture) -> Mock:
    from jose import jwt

    mocked = mocker.patch.object(jwt, "get_unverified_claims")
    mocked.return_value = {
        "sub": "1234567890",
        "name": "John Doe",
        "iat": 1_516_239_022,
        "iss": "http://localhost/",
    }
    return mocked


@pytest.fixture
def clinician() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def jwt_user_uuid(
    app_context: None,
    clinician: str,
    jwt_user_type: str,
    jwt_scopes: List[str],
    mocker: MockerFixture,
) -> str:
    """Use this fixture for parametrized tests setting the jwt_user_type fixture to select different
    account types for requests."""

    if jwt_user_type == "clinician":
        mocker.patch.object(g, "jwt_claims", {"clinician_id": clinician})
        return clinician

    else:
        mocker.patch.object(g, "jwt_claims", {})
        if isinstance(jwt_scopes, str):
            jwt_scopes = jwt_scopes.split(",")
        mocker.patch.object(g, "jwt_scopes", jwt_scopes)

        return "dummy"


@pytest.fixture
def jwt_clinician_login() -> None:
    g.jwt_claims = {"clinician_id": "JWT_USER_ID"}
    g.jwt_scopes = [
        "write:gdm_clinician_all",
        "write:send_clinician_all",
        "read:gdm_clinician_auth_all",
        "read:gdm_clinician_all",
        "read:send_clinician_all",
        "read:send_clinician",
        "read:send_location",
        "write:send_terms_agreement",
        "write:send_patient",
    ]


@pytest.fixture
def bulk_create_clinician_request() -> list[dict]:
    time_now = datetime.now(tz=timezone.utc).isoformat(timespec="milliseconds")
    return [
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
            "locations": [],
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
        for i in range(5)
    ]


@pytest.fixture
def jwt_clinician_migration() -> None:
    g.jwt_claims = {"system_id": "dhos-robot"}
    g.jwt_scopes = [
        "write:read:gdm_clinician_all",
        "read:send_clinician_all",
        "write:clinician_migration",
    ]
