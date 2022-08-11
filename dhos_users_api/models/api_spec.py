from datetime import datetime
from typing import Any, TypedDict

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask_batteries_included.helpers.apispec import (
    FlaskBatteriesPlugin,
    initialise_apispec,
    openapi_schema,
)
from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate

dhos_users_api_spec: APISpec = APISpec(
    version="1.0.0",
    openapi_version="3.0.3",
    title="DHOS USERS API",
    info={"description": "A service for storing information about users"},
    plugins=[FlaskPlugin(), MarshmallowPlugin(), FlaskBatteriesPlugin()],
)

initialise_apispec(dhos_users_api_spec)


def validate_identifier(data: Any) -> None:
    if isinstance(data, str):
        return
    if isinstance(data, dict):
        if (
            isinstance(data.get("uuid"), str)
            and isinstance(data.get("first_name"), str)
            and isinstance(data.get("last_name"), str)
        ):
            return
    raise ValidationError("Invalid identifier field")


class ExpandableIdentifier(Schema):
    """
    TODO: We need this because of the horrible clinician UUID -> dict expansion that happens in this service.
    When this expansion logic is moved to the GDM BFF, we can get rid of this class and use Identifier instead.
    """

    class Meta:
        class Dict(TypedDict, total=False):
            uuid: str
            created: datetime
            created_by: str
            modified: datetime
            modified_by: str

    uuid = fields.String(
        required=True,
        metadata={
            "description": "Universally unique identifier for object",
            "example": "2c4f1d24-2952-4d4e-b1d1-3637e33cc161",
        },
    )
    created = fields.DateTime(
        required=True,
        metadata={
            "description": "When the object was created",
            "example": "2017-09-23T08:29:19.123+00:00",
        },
    )
    created_by = fields.String(
        required=True,
        allow_none=True,
        metadata={
            "description": "UUID of the user that created the object",
            "example": "d26570d8-a2c9-4906-9c6a-ea1a98b8b80f",
        },
    )
    modified = fields.DateTime(
        required=True,
        metadata={
            "description": "When the object was created",
            "example": "2017-09-23T08:29:19.123+00:00",
        },
    )
    modified_by = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "UUID of the user that modified the object",
            "example": "2a0e26e5-21b6-463a-92e8-06d7290067d0",
        },
    )


class BaseProductSchema(Schema):
    class Meta:
        description = "Product"
        unknown = EXCLUDE
        ordered = True

    product_name = fields.String(
        required=True,
        metadata={
            "description": "Product name",
            "example": "SEND",
        },
    )
    opened_date = fields.Date(
        required=True,
        metadata={
            "description": "Opened date",
            "example": "2018-01-01",
        },
    )
    closed_date = fields.Date(
        required=False,
        allow_none=True,
        metadata={
            "description": "Closed date",
            "example": "2018-06-01",
        },
    )
    closed_reason = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "Closed reason",
            "example": "Some reason",
        },
    )
    closed_reason_other = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "Closed reason other",
            "example": "Some other reason",
        },
    )
    accessibility_discussed = fields.Boolean(
        required=False,
        allow_none=True,
        metadata={
            "description": "Whether accessibility was discussed",
            "example": True,
        },
    )
    accessibility_discussed_date = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "When was accessibility discussed",
            "example": "2019-10-07",
        },
    )


class ClinicianProductSchema(BaseProductSchema):
    class Meta:
        description = "Clinician product"
        unknown = EXCLUDE
        ordered = True

    accessibility_discussed_with = fields.Dict(required=False, allow_none=True)


class ClinicianCommonOptionalFields(Schema):
    class Meta:
        ordered = True

    bookmarks = fields.List(
        fields.String(),
        required=False,
        allow_none=True,
        metadata={
            "description": "List of bookmarked location UUIDs",
            "example": ["2ae1e5f0-2e64-405b-a5e2-96d38a688df1"],
        },
    )

    bookmarked_patients = fields.List(
        fields.String(),
        required=False,
        allow_none=True,
        metadata={
            "description": "List of bookmarked patient UUIDs",
            "example": ["eb42ee95-6aa6-46b7-9c3e-0e96526747a6"],
        },
    )

    can_edit_ews = fields.Boolean(
        required=False,
        allow_none=True,
        metadata={
            "description": "Whether the clinician is allowed to change a patient's early warning score in SEND",
            "example": True,
        },
    )

    contract_expiry_eod_date = fields.Date(
        required=False,
        allow_none=True,
        metadata={
            "description": "Contract expiry date",
            "example": "2020-12-31",
        },
    )

    professional_registration_number = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "Professional registration number",
            "example": "321",
        },
    )

    agency_name = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "Agency name", "example": "XYZ Ltd"},
    )

    agency_staff_employee_number = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "Agency staff employee number",
            "example": "321",
        },
    )

    email_address = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "e-mail address",
            "example": "abc@xyz.com",
        },
    )

    booking_reference = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "Booking reference", "example": "4321"},
    )

    analytics_consent = fields.Boolean(
        required=False,
        allow_none=True,
        metadata={
            "description": "Indicates if the user has given consent to analytics",
            "example": True,
        },
    )

    send_entry_identifier = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "Identifier used by clinician to log into SEND entry",
            "example": "321",
        },
    )

    login_active = fields.Boolean(
        required=False,
        allow_none=True,
        metadata={
            "description": "Whether the clinician is allowed to log in",
            "example": True,
        },
    )


class ClinicianAllFieldsAsOptional(ClinicianCommonOptionalFields):
    class Meta:
        ordered = True

    first_name = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "First name", "example": "John"},
    )

    last_name = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "last name", "example": "Roberts"},
    )

    phone_number = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "Phone number",
            "example": "01234098765",
        },
    )

    job_title = fields.String(
        required=False,
        allow_none=True,
        metadata={"description": "Job title", "example": "Doctor"},
    )

    nhs_smartcard_number = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "NHS Smartcard number",
            "example": "012345",
        },
    )

    locations = fields.List(
        fields.String(),
        required=False,
        allow_none=True,
        metadata={
            "description": "List of UUIDs of locations with which the clinician is associated",
            "example": ["eb42ee95-6aa6-46b7-9c3e-0e96526747a6"],
        },
    )

    groups = fields.List(
        fields.String(),
        required=False,
        allow_none=True,
        metadata={
            "description": "List of user groups assigned to",
            "example": ["SEND Clinician"],
        },
    )

    products = fields.List(
        fields.Nested(ClinicianProductSchema()),
        required=False,
        allow_none=True,
        metadata={
            "description": "Products with which the clinician should be associated",
            "example": [{"product_name": "SEND", "opened_date": "2019-06-01"}],
        },
    )


@openapi_schema(dhos_users_api_spec)
class ClinicianCreateRequest(ClinicianCommonOptionalFields):
    class Meta:
        description = "Clinician create request"
        unknown = EXCLUDE
        ordered = True

    first_name = fields.String(
        required=True,
        metadata={
            "description": "First name",
            "example": "John",
        },
    )

    last_name = fields.String(
        required=True,
        metadata={
            "description": "last name",
            "example": "Roberts",
        },
    )

    phone_number = fields.String(
        required=True,
        metadata={
            "description": "Phone number",
            "example": "01234098765",
        },
    )

    job_title = fields.String(
        required=True, metadata={"description": "Job title", "example": "Doctor"}
    )

    nhs_smartcard_number = fields.String(
        required=True,
        metadata={
            "description": "NHS Smartcard number",
            "example": "012345",
        },
    )

    locations = fields.List(
        fields.String(),
        required=True,
        metadata={
            "description": "List of UUIDs of locations with which the clinician is associated",
            "example": ["eb42ee95-6aa6-46b7-9c3e-0e96526747a6"],
        },
    )

    groups = fields.List(
        fields.String(),
        required=True,
        metadata={
            "description": "List of user groups assigned to",
            "example": ["SEND Clinician"],
        },
    )

    products = fields.List(
        fields.Nested(ClinicianProductSchema()),
        required=True,
        metadata={
            "description": "Products with which the clinician should be associated",
            "example": [{"product_name": "SEND", "opened_date": "2019-06-01"}],
        },
        validate=validate.Length(min=1),
    )


@openapi_schema(dhos_users_api_spec)
class ClinicianTermsRequest(Schema):
    class Meta:
        description = "Create Clinician Terms of Service request"
        unknown = EXCLUDE
        ordered = True

    product_name = fields.String(
        required=True,
        metadata={
            "description": "Product name",
            "example": "SEND",
        },
    )
    version = fields.Integer(
        required=True, metadata={"description": "Product version", "example": 12}
    )

    accepted_timestamp = fields.String(
        required=False,
        allow_none=True,
        metadata={
            "description": "Accepted at timestamp",
            "example": "2019-01-01T12:01:01.000Z",
        },
    )


@openapi_schema(dhos_users_api_spec)
class ClinicianTermsResponse(ClinicianTermsRequest, ExpandableIdentifier):
    class Meta:
        description = "Create Clinician Terms of Service response"
        unknown = EXCLUDE
        ordered = True


@openapi_schema(dhos_users_api_spec)
class ClinicianUpdateRequest(ClinicianAllFieldsAsOptional):
    class Meta:
        description = "Clinician update request"
        unknown = EXCLUDE
        ordered = True


@openapi_schema(dhos_users_api_spec)
class ClinicianPasswordUpdateRequest(Schema):
    class Meta:
        description = "Clinician password update request"
        unknown = EXCLUDE
        ordered = True

    password = fields.String(
        required=True, metadata={"description": "Password", "example": "abc*_123"}
    )


@openapi_schema(dhos_users_api_spec)
class ClinicianRemoveRequest(ClinicianAllFieldsAsOptional):
    class Meta:
        description = "Clinician remove request"
        unknown = EXCLUDE
        ordered = True


@openapi_schema(dhos_users_api_spec)
class ClinicianResponse(ClinicianAllFieldsAsOptional, ExpandableIdentifier):
    class Meta:
        description = "Clinician response"
        unknown = EXCLUDE
        ordered = True

    terms_agreement = fields.Dict(
        required=False,
        allow_none=True,
        metadata={"description": "Latest terms agreement"},
    )


@openapi_schema(dhos_users_api_spec)
class CliniciansResponse(Schema):
    class Meta:
        description = "Clinicians response"
        unknown = EXCLUDE
        ordered = True

    results = fields.Nested(
        ClinicianResponse(), required=True, allow_none=False, many=True
    )
    total = fields.Integer(
        required=True,
        allow_none=False,
        metadata={
            "description": "Total clinicians in the database matching the request"
        },
    )


class ClinicianLocations(Schema):
    class Meta:
        ordered = True

    name = fields.String(
        metadata={
            "description": "Name used to display the location for product",
            "example": "John Radcliffe Hospital",
        }
    )
    id = fields.String(
        metadata={
            "description": "Location UUID",
            "example": "eb42ee95-6aa6-46b7-9c3e-0e96526747a6",
        }
    )
    products = fields.List(
        fields.Nested(ClinicianProductSchema()),
        metadata={
            "description": "Products with which the clinician should be associated",
            "example": [{"product_name": "SEND", "opened_date": "2019-06-01"}],
        },
    )


@openapi_schema(dhos_users_api_spec)
class ClinicianLoginResponse(Schema):
    class Meta:
        description = "Create Clinician Terms of Service response"
        unknown = EXCLUDE
        ordered = True

    job_title = fields.String(
        required=True, metadata={"description": "Job title", "example": "Doctor"}
    )

    email_address = fields.String(
        metadata={
            "description": "e-mail address",
            "example": "abc@xyz.com",
        },
        required=True,
        allow_none=True,
    )

    locations = fields.List(
        fields.Nested(ClinicianLocations()),
        metadata={
            "description": "Locations with which the clinician should be associated",
        },
        required=True,
    )

    user_id = fields.String(
        metadata={
            "description": "User UUID of clinician",
            "example": "eb42ee95-6aa6-46b7-9c3e-0e96526747a6",
        },
        required=True,
    )

    groups = fields.List(
        fields.String(),
        metadata={
            "description": "List of user groups assigned to",
            "example": ["SEND Clinician"],
        },
        required=True,
    )

    permissions = fields.List(
        fields.String(),
        metadata={
            "description": "List of permissions user has",
            "example": ["read:patient_all", "write:patient_all"],
        },
        required=True,
    )

    products = fields.List(
        fields.Nested(ClinicianProductSchema()),
        metadata={
            "description": "Products with which the clinician should be associated",
            "example": [{"product_name": "SEND", "opened_date": "2019-06-01"}],
        },
        required=True,
    )

    can_edit_ews = fields.Boolean(
        metadata={
            "description": "Whether the clinician is allowed to change a patient's SpO2 scale in SEND",
        },
        required=True,
        allow_none=True,
    )
