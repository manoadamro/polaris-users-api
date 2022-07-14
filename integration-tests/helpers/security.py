import os
from datetime import datetime, timedelta

from behave import fixture
from behave.runner import Context
from environs import Env
from jose import jwt as jose_jwt


def generate_clinician_token(context: Context) -> str:
    if not hasattr(context, "clinician_jwt"):
        hs_issuer: str = os.environ["HS_ISSUER"]
        hs_key: str = os.environ["HS_KEY"]
        proxy_url: str = os.environ["PROXY_URL"]
        scope: str = " ".join(
            [
                "read:gdm_patient",
                "write:gdm_patient",
                "read:gdm_clinician",
                "write:gdm_clinician",
                "read:gdm_location",
                "read:gdm_message",
                "write:gdm_message",
                "read:gdm_bg_reading_all",
                "write:gdm_alert",
                "read:gdm_medication",
                "read:gdm_pdf",
                "write:gdm_pdf",
                "read:gdm_csv",
                "read:gdm_question",
                "read:gdm_answer_all",
                "write:gdm_answer_all",
                "read:gdm_activation",
                "write:gdm_activation",
                "read:gdm_trustomer",
                "read:gdm_telemetry_all",
                "write:gdm_telemetry",
                "write:gdm_terms_agreement",
                "read:send_location",
            ]
        )
        context.clinician_jwt = jose_jwt.encode(
            {
                "metadata": {"clinician_id": context.clinician_uuid},
                "iss": hs_issuer,
                "aud": proxy_url + "/",
                "scope": scope,
                "exp": 9_999_999_999,
            },
            key=hs_key,
            algorithm="HS512",
        )
    context.current_jwt = context.clinician_jwt
    return context.clinician_jwt


def generate_superclinician_token(context: Context) -> str:
    if not hasattr(context, "superclinician_jwt"):
        hs_issuer: str = os.environ["HS_ISSUER"]
        hs_key: str = os.environ["HS_KEY"]
        proxy_url: str = os.environ["PROXY_URL"]
        scope: str = " ".join(
            [
                "read:gdm_patient_all",
                "write:gdm_patient_all",
                "read:gdm_clinician_all",
                "write:gdm_clinician_all",
                "read:gdm_location_all",
                "read:gdm_message_all",
                "write:gdm_message_all",
                "read:gdm_bg_reading_all",
                "write:gdm_alert",
                "read:gdm_medication",
                "read:gdm_pdf",
                "write:gdm_pdf",
                "read:gdm_csv",
                "read:gdm_question",
                "read:gdm_answer_all",
                "write:gdm_answer_all",
                "write:gdm_activation",
                "read:gdm_activation",
                "read:gdm_trustomer",
                "read:gdm_telemetry_all",
                "write:gdm_telemetry",
                "write:gdm_terms_agreement",
            ]
        )
        context.superclinician_jwt = jose_jwt.encode(
            {
                "metadata": {"clinician_id": context.clinician_uuid},
                "iss": hs_issuer,
                "aud": proxy_url + "/",
                "scope": scope,
                "exp": 9_999_999_999,
            },
            key=hs_key,
            algorithm="HS512",
        )
    context.current_jwt = context.superclinician_jwt
    return context.superclinician_jwt


def generate_patient_token(context: Context) -> str:
    if not hasattr(context, "patient_jwt"):
        hs_issuer: str = os.environ["HS_ISSUER"]
        hs_key: str = os.environ["HS_KEY"]
        proxy_url: str = os.environ["PROXY_URL"]
        scope: str = " ".join(
            [
                "read:gdm_patient_abbreviated",
                "read:gdm_message",
                "write:gdm_message",
                "read:gdm_bg_reading",
                "write:gdm_bg_reading",
                "read:gdm_medication",
                "read:gdm_question",
                "read:gdm_answer",
                "write:gdm_answer",
                "read:gdm_trustomer",
                "read:gdm_telemetry",
                "write:gdm_telemetry",
                "write:gdm_terms_agreement",
            ]
        )
        context.patient_jwt = jose_jwt.encode(
            {
                "metadata": {"patient_id": context.patient_uuids[-1]},
                "iss": hs_issuer,
                "aud": proxy_url + "/",
                "scope": scope,
                "exp": 9_999_999_999,
            },
            key=hs_key,
            algorithm="HS512",
        )
    context.current_jwt = context.patient_jwt
    return context.patient_jwt


@fixture
def get_system_token(context: Context) -> str:
    return generate_system_token(context)


def generate_system_token(context: Context) -> str:
    if not hasattr(context, "system_jwt"):
        context.system_jwt = jose_jwt.encode(
            claims={
                "metadata": {"system_id": "dhos-robot"},
                "iss": "http://localhost/",
                "aud": "http://localhost/",
                "scope": Env().str("SYSTEM_JWT_SCOPE"),
                "exp": datetime.utcnow() + timedelta(seconds=3000),
            },
            key=Env().str("HS_KEY"),
            algorithm="HS512",
        )
    context.current_jwt = context.system_jwt
    return context.system_jwt


def generate_login_token(context: Context) -> str:
    """Special system token used just for login."""
    if not hasattr(context, "login_jwt"):
        if not hasattr(context, "patient_jwt"):
            hs_issuer: str = os.environ["HS_ISSUER"]
            hs_key: str = os.environ["HS_KEY"]
            proxy_url: str = os.environ["PROXY_URL"]
            context.login_jwt = jose_jwt.encode(
                {
                    "metadata": {"system_id": "dhos-robot"},
                    "iss": hs_issuer,
                    "aud": proxy_url + "/",
                    "scope": "read:gdm_clinician_auth_all",
                    "exp": 9_999_999_999,
                },
                key=hs_key,
                algorithm="HS512",
            )
    context.current_jwt = context.login_jwt
    return context.login_jwt
