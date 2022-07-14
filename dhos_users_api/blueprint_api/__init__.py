from typing import Dict, List, Optional

import flask
from flask import Blueprint, Response, jsonify, make_response, request
from flask_batteries_included.helpers.routes import deprecated_route
from flask_batteries_included.helpers.security import protected_route
from flask_batteries_included.helpers.security.endpoint_security import (
    and_,
    key_present,
    match_keys,
    or_,
    scopes_present,
)
from flask_batteries_included.helpers.security.jwt import current_jwt_user

from dhos_users_api.blueprint_api import controller

clinicians_blueprint = Blueprint("clinicians_api", __name__)


@clinicians_blueprint.route("/dhos/v1/clinician", methods=["POST"])
@protected_route(
    or_(
        scopes_present(required_scopes="write:gdm_clinician_all"),
        scopes_present(required_scopes="write:send_clinician_all"),
        scopes_present(required_scopes="write:send_clinician_temp"),
    )
)
def create_clinician(
    clinician_details: Dict,
    send_welcome_email: bool = True,
) -> flask.Response:
    """
    ---
    post:
      summary: Create clinician
      description: Create a new clinician using the details provided in the request body.
      tags: [clinician]
      parameters:
        - name: send_welcome_email
          in: query
          required: false
          description: Whether to send a welcome email
          schema:
            type: boolean
            default: true
      requestBody:
        description: Clinician details
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ClinicianCreateRequest'
              x-body-name: clinician_details
      responses:
        '200':
          description: New clinician
          content:
            application/json:
              schema: ClinicianResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    response: Dict = controller.create_clinician(
        clinician_details=clinician_details,
        send_welcome_email=send_welcome_email,
    )
    return jsonify(response)


@clinicians_blueprint.route(
    "/dhos/v1/clinician/<clinician_id>/terms_agreement", methods=["POST"]
)
@protected_route(
    and_(
        or_(
            scopes_present(required_scopes="write:gdm_terms_agreement"),
            scopes_present(required_scopes="write:send_terms_agreement"),
        ),
        or_(match_keys(clinician_id="clinician_id"), key_present("system_id")),
    )
)
def create_clinician_tos(clinician_id: str, clinician_tos: Dict) -> flask.Response:
    """
    ---
    post:
      summary: Create clinician terms of service agreement
      description: Create a new clinician terms of service agreement using the details provided in the request body.
      tags: [terms-agreement]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: Clinician UUID
          schema:
            type: string
            example: bba65af9-88d3-459b-8c09-c359873828f7
      requestBody:
        description: Clinician terms of service details
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ClinicianTermsRequest'
              x-body-name: clinician_tos
      responses:
        '200':
          description: New clinician terms of service
          content:
            application/json:
              schema: ClinicianTermsResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    response: Dict = controller.create_clinician_tos(
        clinician_id=clinician_id, clinician_details=clinician_tos
    )
    return jsonify(response)


@clinicians_blueprint.route("/dhos/v1/clinician/<clinician_id>", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_clinician_all"),
        scopes_present(required_scopes="read:send_clinician_all"),
        and_(
            scopes_present(required_scopes="read:gdm_clinician"),
            match_keys(clinician_id="clinician_id"),
        ),
        and_(
            scopes_present(required_scopes="read:send_clinician"),
            match_keys(clinician_id="clinician_id"),
        ),
        scopes_present(required_scopes="read:send_clinician_temp"),
    )
)
def get_clinician_by_uuid(
    clinician_id: str, product_name: str = None, temp_only: bool = False
) -> flask.Response:
    """
    ---
    get:
      summary: Get clinician by UUID
      description: >-
        Get the clinician with the provided UUID.
      tags: [clinician]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: Clinician UUID
          schema:
            type: string
            example: "bba65af9-88d3-459b-8c09-c359873828f7"
        - name: product_name
          in: query
          required: false
          description: Name of product
          schema:
            type: string
            example: SEND
        - name: temp_only
          in: query
          required: false
          description: Restrict to temporary clinicians only
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Requested clinician
          content:
            application/json:
              schema: ClinicianResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """

    response: Dict = controller.get_clinician_by_id(
        clinician_id=clinician_id, get_temp_only=temp_only
    )
    return jsonify(response)


@clinicians_blueprint.route("/dhos/v1/clinician/<clinician_id>", methods=["PATCH"])
@protected_route(
    or_(
        scopes_present(required_scopes="write:gdm_clinician_all"),
        and_(
            scopes_present(required_scopes="write:gdm_clinician"),
            match_keys(clinician_id="clinician_id"),
        ),
        scopes_present(required_scopes="write:send_clinician_all"),
        scopes_present(required_scopes="write:send_clinician_temp"),
        and_(
            scopes_present(required_scopes="write:send_clinician"),
            match_keys(clinician_id="clinician_id"),
        ),
    )
)
def update_clinician(
    clinician_id: str,
    clinician_details: Dict,
    temp_only: bool = False,
) -> flask.Response:
    """
    ---
    patch:
      summary: Update clinician
      description: Update the clinician with the provided UUID using the details in the request body.
      tags: [clinician]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: Clinician UUID
          schema:
            type: string
            example: bba65af9-88d3-459b-8c09-c359873828f7
        - name: product_name
          in: query
          required: false
          description: Name of product
          deprecated: true
          schema:
            type: string
            example: SEND
        - name: temp_only
          in: query
          required: false
          description: Can edit temporary clinicians only
          schema:
            type: boolean
            default: false
      requestBody:
        description: Clinician update
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ClinicianUpdateRequest'
              x-body-name: clinician_details
      responses:
        '200':
          description: Updated clinician
          content:
            application/json:
              schema: ClinicianResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    response: Dict = controller.update_clinician(
        clinician_id=clinician_id,
        update_fields=clinician_details,
        edit_temp_only=temp_only,
    )
    return jsonify(response)


@clinicians_blueprint.route(
    "/dhos/v1/clinician/<clinician_id>/delete", methods=["PATCH"]
)
@protected_route(
    or_(
        scopes_present(required_scopes="write:gdm_clinician_all"),
        and_(
            scopes_present(required_scopes="write:gdm_clinician"),
            match_keys(clinician_id="clinician_id"),
        ),
        scopes_present(required_scopes="write:send_clinician_all"),
    )
)
def remove_from_clinician(clinician_id: str, clinician_details: Dict) -> flask.Response:
    """
    ---
    patch:
      summary: Remove details from clinician
      description: >-
        Remove the details in the request body from the clinician with the provided UUID.
        Note that this endpoint does not remove the clinician itself.
      tags: [clinician]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: Clinician UUID
          schema:
            type: string
            example: bba65af9-88d3-459b-8c09-c359873828f7
      requestBody:
        description: >-
          Details to remove from clinician:
          This endpoint can only delete individual items from a collection such as a list or tuple.
          The list here includes bookmarks, bookmarked_patients, groups, locations and products.
          There are some specific permissions required for groups and bookmarked_patients.
          It will ignore a single key-value pair e.g. { "phone_number" : "01234999999" }.
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ClinicianRemoveRequest'
              x-body-name: clinician_details
      responses:
        '200':
          description: Updated clinician
          content:
            application/json:
              schema: ClinicianResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """

    response: Dict = controller.remove_from_clinician(
        clinician_id=clinician_id, clinician_details=clinician_details
    )
    return jsonify(response)


@clinicians_blueprint.route("/dhos/v1/clinician", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:gdm_clinician_all"))
def get_clinician_by_email(email: str) -> flask.Response:
    """
    ---
    get:
      summary: Get clinician by email
      description: Get clinician with the provided email address.
      tags: [clinician]
      parameters:
        - name: email
          in: query
          required: true
          description: Email address of the clinician requested.
          schema:
            type: string
            example: robert@mail.com
      responses:
        '200':
          description: Requested clinician with the provided email address
          content:
            application/json:
              schema: ClinicianResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """

    response: Dict = controller.get_clinician_by_email(email=email)
    return jsonify(response)


@clinicians_blueprint.route("/dhos/v1/clinician", methods=["PATCH"])
@protected_route(scopes_present(required_scopes="write:gdm_clinician_all"))
def update_clinician_password_by_email(
    email: str, clinician_details: Dict
) -> flask.Response:
    """
    ---
    patch:
      summary: Update clinician's password by email
      description: Update the clinician with the provided email using the details in the request body.
      tags: [clinician]
      parameters:
        - name: email
          in: query
          required: true
          description: Email address of clinician
          schema:
            type: string
            example: robert@mail.com
      requestBody:
        description: Clinician password update
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ClinicianPasswordUpdateRequest'
              x-body-name: clinician_details
      responses:
        '200':
          description: Updated clinician
          content:
            application/json:
              schema: ClinicianResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """

    response: Dict = controller.update_clinician_password_by_email(
        email=email, password=clinician_details["password"]
    )
    return jsonify(response)


@clinicians_blueprint.route("/dhos/v1/clinician/login", methods=["GET"])
@protected_route(scopes_present(required_scopes="read:gdm_clinician_auth_all"))
def clinician_login() -> flask.Response:
    """
    ---
    get:
      summary: Validate clinician login
      description: Validate a clinician's login credentials and return a login response
      tags: [login]
      parameters:
        - name: UserAuthorization
          in: header
          required: true
          description: User authorization bearer token base64 encoded string containing the username and password, separated by colon
          schema:
            type: string
            example: Bearer bGF6YXJvLnZhbmRlcnZvcnRAbWFpbC5jb206UGFzc0B3b3JkMSE=
      responses:
        '200':
          description: Clinician's user details
          content:
            application/json:
              schema: ClinicianLoginResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    if not request.headers.get("UserAuthorization"):
        raise PermissionError("Login failed")

    ua_header: str = str(request.headers.get("UserAuthorization", ""))

    if not ua_header.startswith("Bearer "):
        raise PermissionError("Login failed")

    # Header is in the form "Bearer <b64str>", so trim it.
    user_auth_string_b64: str = ua_header[7:]

    response: Optional[Dict] = controller.clinician_login(user_auth_string_b64)
    return jsonify(response)


@clinicians_blueprint.route("/dhos/v1/clinicians", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_clinician_all"),
        scopes_present(required_scopes="read:gdm_clinician"),
        scopes_present(required_scopes="read:send_clinician_all"),
        scopes_present(required_scopes="read:send_clinician_temp"),
    )
)
@deprecated_route(superseded_by="GET /dhos/v2/clinicians")
def get_clinicians_v1(
    product_name: Optional[str] = None,
    login_active: Optional[bool] = None,
    compact: bool = False,
    expanded: bool = False,
    modified_since: Optional[str] = None,
    temp_only: bool = False,
    q: Optional[str] = None,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[str]] = None,
    order: Optional[str] = None,
) -> flask.Response:
    """
    ---
    get:
      summary: Get all clinicians
      description: Get all clinicians. Supports pagination.
      tags: [clinician]
      parameters:
        - name: product_name
          in: query
          required: false
          description: Product name
          schema:
            type: string
            example: GDM
        - name: login_active
          in: query
          required: false
          description: Return only active/inactive clinicians. If not passed in, returns all clinicians regardless of active status.
          schema:
            type: boolean
            example: true
        - name: compact
          in: query
          required: false
          description: Specifies if the response should be in compact form.
          schema:
            type: boolean
            default: false
            example: false
        - name: expanded
          in: query
          required: false
          description: Specifies if the response should be in expanded form.
          schema:
            type: boolean
            default: false
            example: false
        - name: modified_since
          in: query
          required: false
          description: Filter clinicians to those modified since this datetime. Note, if timezone is used, a `+` symbol should be passed as an URL-encoded character, i.e. `%2B`
          schema:
            type: string
            example: 2000-01-01T01:01:01.123%2B01:00
        - name: temp_only
          in: query
          required: false
          description: Only return temporary clinicians
          schema:
            type: boolean
            default: false
        - name: q
          in: query
          required: false
          description: Filter clinicians by a string (substring) provided.
            Search is performed in `name` (substring), `role` (substring),
            `badge_id` (string).
          schema:
            type: string
            example: Lorem
        - name: offset
          in: query
          required: false
          description: Apply offset to the search results, i.e. given
            there are 75 clinicians in the database and the offset param is
            set to 50, the outcome would be the last 25 clinicians.
          schema:
            type: integer
            example: 50
        - name: limit
          in: query
          required: false
          description: Limit the search results to the number provided.
          schema:
            type: integer
            example: 25
        - name: sort
          in: query
          required: false
          description: List of clinician's field to sort the search results by
          schema:
            type: array
            nullable: true
            items:
                type: string
                enum: [last_name, first_name, uuid, nhs_smartcard_number, email_address, modified, created, phone_number, send_entry_identifier, job_title]
            default: [last_name,first_name]
        - name: order
          in: query
          required: false
          description: Sort order
          schema:
            type: string
            enum: [asc, desc]
            default: asc
      responses:
        '200':
          description: List of clinicians
          content:
            application/json:
              schema:
                type: array
                items: ClinicianResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    clinicians, _ = controller.get_clinicians(
        login_active=login_active,
        product_name=product_name,
        temp_only=temp_only,
        compact=compact,
        expanded=expanded,
        modified_since=modified_since,
        q=q,
        offset=offset,
        limit=limit,
        sort=sort,
        order=order,
    )
    return jsonify(clinicians)


@clinicians_blueprint.route("/dhos/v2/clinicians", methods=["GET"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_clinician_all"),
        scopes_present(required_scopes="read:gdm_clinician"),
        scopes_present(required_scopes="read:send_clinician_all"),
        scopes_present(required_scopes="read:send_clinician_temp"),
    )
)
def get_clinicians(
    product_name: Optional[str] = None,
    login_active: Optional[bool] = None,
    compact: bool = False,
    expanded: bool = False,
    modified_since: Optional[str] = None,
    temp_only: bool = False,
    q: Optional[str] = None,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    sort: Optional[List[str]] = None,
    order: Optional[str] = None,
) -> flask.Response:
    """
    ---
    get:
      summary: Get all clinicians
      description: Get all clinicians. Supports pagination.
      tags: [clinician]
      parameters:
        - name: product_name
          in: query
          required: false
          description: Product name
          schema:
            type: string
            example: GDM
        - name: login_active
          in: query
          required: false
          description: Return only active/inactive clinicians. If not passed in, returns all clinicians regardless of active status.
          schema:
            type: boolean
            example: true
        - name: compact
          in: query
          required: false
          description: Specifies if the response should be in compact form.
          schema:
            type: boolean
            default: false
            example: false
        - name: expanded
          in: query
          required: false
          description: Specifies if the response should be in expanded form.
          schema:
            type: boolean
            default: false
            example: false
        - name: modified_since
          in: query
          required: false
          description: Filter clinicians to those modified since this datetime. Note, if timezone is used, a `+` symbol should be passed as an URL-encoded character, i.e. `%2B`
          schema:
            type: string
            example: 2000-01-01T01:01:01.123%2B01:00
        - name: temp_only
          in: query
          required: false
          description: Only return temporary clinicians
          schema:
            type: boolean
            default: false
        - name: q
          in: query
          required: false
          description: Filter clinicians by a string (substring) provided.
            Search is performed in `name` (substring), `role` (substring),
            `badge_id` (string).
          schema:
            type: string
            example: Lorem
        - name: offset
          in: query
          required: false
          description: Apply offset to the search results, i.e. given
            there are 75 clinicians in the database and the offset param is
            set to 50, the outcome would be the last 25 clinicians.
          schema:
            type: integer
            example: 50
        - name: limit
          in: query
          required: false
          description: Limit the search results to the number provided.
          schema:
            type: integer
            example: 25
        - name: sort
          in: query
          required: false
          description: List of clinician's field to sort the search results by
          schema:
            type: array
            nullable: true
            items:
                type: string
                enum: [last_name, first_name, uuid, nhs_smartcard_number, email_address, modified, created, phone_number, send_entry_identifier, job_title]
            default: [last_name,first_name]
        - name: order
          in: query
          required: false
          description: Sort order
          schema:
            type: string
            enum: [asc, desc]
            default: asc
      responses:
        '200':
          description: List of clinicians and total
          content:
            application/json:
              schema: CliniciansResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    clinician_list, total = controller.get_clinicians(
        login_active=login_active,
        product_name=product_name,
        temp_only=temp_only,
        compact=compact,
        expanded=expanded,
        modified_since=modified_since,
        q=q,
        offset=offset,
        limit=limit,
        sort=sort,
        order=order,
    )
    return jsonify({"results": clinician_list, "total": total})


@clinicians_blueprint.route("/dhos/v1/clinician_list", methods=["POST"])
@protected_route(
    or_(
        scopes_present(required_scopes="read:gdm_clinician_all"),
        scopes_present(required_scopes="read:gdm_clinician"),
        scopes_present(required_scopes="read:send_clinician_all"),
        scopes_present(required_scopes="read:send_clinician"),
    )
)
def retrieve_clinicians_by_uuids(
    clinician_uuids: List[str], compact: bool = False
) -> flask.Response:
    """
    ---
    post:
      summary: Retrieve clinicians by UUIDs
      description: >-
        Retrieve clinicians by list of UUIDs. Response contains a map of clinician UUIDs to clinician details.
      tags: [clinician]
      parameters:
        - name: compact
          in: query
          required: false
          description: Specifies if the response should be in compact form.
          schema:
            type: boolean
            default: false
            example: false
      requestBody:
        description: List of clinician uuids
        required: true
        content:
          application/json:
            schema:
              x-body-name: clinician_uuids
              type: array
              items:
                type: string
              example: ["bba65af9-88d3-458b-8c09-c359873828f7", "276ff208-8893-4592-a4a5-ed4d7dd35f89"]
      responses:
        '200':
          description: Map of clinicians
          content:
            application/json:
              schema:
                type: object
                additionalProperties:
                  $ref: '#/components/schemas/ClinicianResponse'
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return jsonify(
        controller.get_clinicians_by_uuids(uuids=clinician_uuids, compact=compact)
    )


@clinicians_blueprint.route(
    "/dhos/v1/location/<location_id>/clinician", methods=["GET"]
)
@protected_route(scopes_present(required_scopes="read:gdm_clinician_all"))
def get_clinicians_by_location(location_id: str) -> flask.Response:
    """
    ---
    get:
      summary: Get clinicians at location
      description: Get the clinicians associated with the location with the provided UUID.
      tags: [clinician]
      parameters:
        - name: location_id
          in: path
          required: true
          description: Location UUID
          schema:
            type: string
            example: 2ee7c51b-0a5c-4843-9dc3-635461ea729c
      responses:
        '200':
          description: List of clinicians
          content:
            application/json:
              schema:
                type: array
                items: ClinicianResponse
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    if request.is_json:
        raise ValueError("Request should not contain a json body")

    clinicians: List[Dict] = controller.get_clinicians_at_location(
        location_uuid=location_id
    )
    return jsonify(clinicians)


@clinicians_blueprint.route(
    "/dhos/v1/clinician/<clinician_id>/location/<location_id>/bookmark",
    methods=["POST"],
)
@protected_route(
    and_(
        scopes_present(required_scopes="read:send_clinician"),
        scopes_present(required_scopes="read:send_location"),
        or_(match_keys(clinician_id="clinician_id"), key_present("system_id")),
    )
)
def create_clinician_location_bookmark(clinician_id: str, location_id: str) -> Response:
    """
    ---
    post:
      summary: Create a clinician-location bookmark
      description: Create a bookmark between the clinician and location with the provided UUIDs.
      tags: [bookmark]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: Clinician UUID
          schema:
            type: string
            example: 621ff25d-4768-4fc5-a9f0-2b5b7cf52b39
        - name: location_id
          in: path
          required: true
          description: Location UUID
          schema:
            type: string
            example: 99f86b12-0112-42be-a0bb-fbe8e65c6b2f
      responses:
        '201':
          description: Bookmark created
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    if request.is_json:
        raise ValueError("Request should not contain a json body")
    controller.add_clinician_location_bookmark(
        clinician_id=clinician_id, location_id=location_id
    )
    return make_response("", 201)


@clinicians_blueprint.route(
    "/dhos/v1/clinician/<clinician_id>/location/<location_id>/bookmark",
    methods=["DELETE"],
)
@protected_route(
    and_(
        scopes_present(required_scopes="read:send_clinician"),
        scopes_present(required_scopes="read:send_location"),
        or_(match_keys(clinician_id="clinician_id"), key_present("system_id")),
    )
)
def delete_clinician_location_bookmark(clinician_id: str, location_id: str) -> Response:
    """
    ---
    delete:
      summary: Delete a clinician-location bookmark
      description: Delete a bookmark between the clinician and location with the provided UUIDs.
      tags: [bookmark]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: Clinician UUID
          schema:
            type: string
            example: 621ff25d-4768-4fc5-a9f0-2b5b7cf52b39
        - name: location_id
          in: path
          required: true
          description: Location UUID
          schema:
            type: string
            example: 99f86b12-0112-42be-a0bb-fbe8e65c6b2f
      responses:
        '204':
          description: Bookmark deleted
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    if request.is_json:
        raise ValueError("Request should not contain a json body")

    controller.remove_clinician_location_bookmark(
        clinician_id=clinician_id, location_id=location_id
    )
    return make_response("", 204)


@clinicians_blueprint.route(
    "/dhos/v1/clinician/<clinician_id>/patient/<patient_id>/bookmark", methods=["POST"]
)
@protected_route(scopes_present(required_scopes="write:send_patient"))
def create_clinician_patient_bookmark(clinician_id: str, patient_id: str) -> Response:
    """
    ---
    post:
      summary: Create a clinician-patient bookmark
      description: >-
        Create a bookmark between the patient with the provided UUID and a clinician. Note
        that the clinician is determined by the JWT and not the clinician UUID in the path.
      tags: [patient]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: Clinician UUID (this is ignored)
          schema:
            type: string
            example: 621ff25d-4768-4fc5-a9f0-2b5b7cf52b39
        - name: patient_id
          in: path
          required: true
          description: Patient UUID
          schema:
            type: string
            example: ff9279e6-7a70-4fbb-b532-eb8a602751ae
      responses:
        '201':
          description: Bookmark created
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    if request.is_json:
        raise ValueError("Request should not contain a json body")

    user_uuid: str = current_jwt_user()
    controller.add_clinician_patient_bookmark(
        clinician_id=user_uuid, patient_id=patient_id
    )
    return make_response("", 201)


@clinicians_blueprint.route(
    "/dhos/v1/clinician/<clinician_id>/patient/<patient_id>/bookmark",
    methods=["DELETE"],
)
@protected_route(scopes_present(required_scopes="write:send_patient"))
def delete_clinician_patient_bookmark(clinician_id: str, patient_id: str) -> Response:
    """
    ---
    delete:
      summary: Delete a clinician-patient bookmark
      description: >-
        Delete a bookmark between the patient with the provided UUID and a clinician. Note
        that the clinician is determined by the JWT and not the clinician UUID in the path.
      tags: [patient]
      parameters:
        - name: clinician_id
          in: path
          required: true
          description: Clinician UUID (this is ignored)
          schema:
            type: string
            example: 621ff25d-4768-4fc5-a9f0-2b5b7cf52b39
        - name: patient_id
          in: path
          required: true
          description: Patient UUID
          schema:
            type: string
            example: ff9279e6-7a70-4fbb-b532-eb8a602751ae
      responses:
        '204':
          description: Bookmark deleted
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    if request.is_json:
        raise ValueError("Request should not contain a json body")

    user_uuid: str = current_jwt_user()
    controller.remove_clinician_patient_bookmark(
        clinician_id=user_uuid, patient_id=patient_id
    )
    return make_response("", 204)


# Endpoint to help with migration of data from Services API.
@clinicians_blueprint.route("/dhos/v1/clinician/bulk", methods=["POST"])
@protected_route(scopes_present(required_scopes="write:clinician_migration"))
def create_clinician_bulk(clinician_details: List[Dict]) -> flask.Response:
    """
    ---
    post:
      summary: Create clinician in bulk (migration only)
      description: >-
        Creates clinicians using the details provided in the request body. Intended for migration from
        Services API only.
      tags: [migration]
      requestBody:
        description: Clinician details
        required: true
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/ClinicianCreateRequest'
              x-body-name: clinician_details
      responses:
        '200':
          description: Bulk clinician creation complete
          content:
            application/json:
              schema:
                type: object
                properties:
                  created:
                    type: integer
                    description: Number of clinicians created
                    example: 50
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    response: Dict = controller.create_clinicians_bulk(
        clinician_details=clinician_details
    )
    return jsonify(response)


@clinicians_blueprint.route("/dhos/v1/roles", methods=["GET"])
@protected_route()
def get_roles() -> flask.Response:
    """
    ---
    get:
      summary: Get roles
      description: Get a map of roles and their associated permissions
      tags: [roles]
      responses:
        '200':
          description: Map of roles and permissions
          content:
            application/json:
              schema:
                type: object
                additionalProperties:
                  type: string
                example: {"System": ["read:patient_all", "write:patient_all"]}
        default:
          description: >-
            Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return jsonify(controller.get_roles())
