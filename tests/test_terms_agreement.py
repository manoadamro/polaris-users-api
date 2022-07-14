import uuid
from datetime import datetime, timezone

import pytest

from dhos_users_api.models.terms_agreement import TermsAgreement


@pytest.mark.usefixtures("app")
class TestTermsAgreement:
    @pytest.fixture
    def terms_agreement_details(self) -> dict:
        time_now = datetime.now(tz=timezone.utc).isoformat(timespec="milliseconds")
        return {
            "uuid": str(uuid.uuid4()),
            "created_by": str(uuid.uuid4()),
            "created": time_now,
            "modified_by": str(uuid.uuid4()),
            "modified": time_now,
            "product_name": "GDM",
            "version": 2,
            "accepted_timestamp": time_now,
        }

    def test_create_new_terms_agreement(self, terms_agreement_details: dict) -> None:
        terms_agreement = TermsAgreement.new(**terms_agreement_details)
        assert isinstance(terms_agreement, TermsAgreement)

    def test_datetime_properties(self, terms_agreement_details: dict) -> None:
        new_time = datetime.now(tz=timezone.utc).isoformat(timespec="milliseconds")
        terms_agreement: TermsAgreement = TermsAgreement.new(**terms_agreement_details)
        terms_agreement.created_by = new_time
        terms_agreement.modified_by = new_time
        assert terms_agreement.created_by == new_time
        assert terms_agreement.modified_by == new_time

    def test_defaults(self, terms_agreement_details: dict) -> None:
        del terms_agreement_details["uuid"]
        del terms_agreement_details["accepted_timestamp"]
        terms_agreement_details["tou_version"] = 5
        terms_agreement_details["patient_notice_accepted_timestamp"] = 5
        terms_agreement: TermsAgreement = TermsAgreement.new(**terms_agreement_details)
        assert terms_agreement.uuid is not None
        assert terms_agreement.accepted_timestamp is not None
        assert terms_agreement.tou_accepted_timestamp is not None
        assert terms_agreement.patient_notice_accepted_timestamp is not None
