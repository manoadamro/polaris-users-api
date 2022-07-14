from datetime import datetime
from typing import Dict, List, Optional

from dhos_users_api.blueprint_api import controller


def create_clinician(
    first_name: str,
    last_name: str,
    product_name: str,
    nhs_smartcard_number: str,
    send_entry_identifier: str = None,
    email_address: Optional[str] = None,
    expiry: Optional[datetime] = None,
    login_active: bool = True,
    groups: Optional[List[str]] = None,
    locations: Optional[List[str]] = None,
    uuid: Optional[str] = None,
) -> Dict:
    extra: Dict = {}
    if not email_address:
        email_address = f"{first_name}.{last_name}@test.com"

    if uuid:
        extra = {"uuid": uuid}

    if groups is None:
        groups = ["SEND Clinician"]

    if locations is None:
        locations = []

    clinician_details = {
        "first_name": first_name,
        "last_name": last_name,
        "job_title": "doctor",
        "phone_number": "",
        "groups": groups,
        "products": [{"product_name": product_name, "opened_date": "2021-7-19"}],
        "locations": locations,
        "nhs_smartcard_number": nhs_smartcard_number,
        "send_entry_identifier": send_entry_identifier,
        "email_address": email_address,
        "can_edit_ews": False,
        "contract_expiry_eod_date": expiry,
        "login_active": login_active,
        **extra,
    }

    clinician = controller.create_clinician(
        clinician_details=clinician_details, send_welcome_email=False
    )
    return clinician
