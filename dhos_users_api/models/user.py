import codecs
import itertools
import string
from typing import Any, Dict, List, Optional, Sequence

from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Random import random as crr
from flask_batteries_included.helpers import generate_uuid
from flask_batteries_included.sqldb import ModelIdentifier, db
from she_logging import logger
from sqlalchemy import Boolean, Column, Date, String
from sqlalchemy.dialects.postgresql import ARRAY

from dhos_users_api.models.product import Product
from dhos_users_api.models.terms_agreement import TermsAgreement


class User(ModelIdentifier, db.Model):
    nhs_smartcard_number = Column(String, nullable=True, index=True)
    send_entry_identifier = Column(String, nullable=True, index=True)
    job_title = Column(String, nullable=True, index=True)
    first_name = Column(String, nullable=True, index=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email_address = Column(String, unique=True, nullable=True, index=True)
    can_edit_ews = Column(Boolean, nullable=False, default=False)
    can_edit_encounter = Column(Boolean, nullable=True)
    professional_registration_number = Column(String, nullable=True)
    agency_name = Column(String, nullable=True)
    agency_staff_employee_number = Column(String, nullable=True)
    booking_reference = Column(String, nullable=True)
    contract_expiry_eod_date = Column(Date, nullable=True)
    password_hash = Column(String, nullable=True)
    password_salt = Column(String, nullable=True)
    login_active = Column(Boolean, nullable=False, default=True)
    analytics_consent = Column(Boolean, nullable=True)
    groups = Column(ARRAY(String))
    locations = Column(ARRAY(String))
    bookmarks = Column(ARRAY(String))
    bookmarked_patients = Column(ARRAY(String))

    products = db.relationship(
        Product,
        lazy="joined",
        primaryjoin="User.uuid == Product.user_id",
        cascade="all, delete-orphan",
        backref="product",
    )

    terms_agreement = db.relationship(
        TermsAgreement,
        lazy="joined",
        primaryjoin="User.uuid == TermsAgreement.user_id",
        cascade="all, delete-orphan",
        backref="terms_agreement",
    )

    @property
    def created_by(self) -> str:
        return self.created_by_

    @created_by.setter
    def created_by(self, value: str) -> None:
        self.created_by_ = value

    @property
    def modified_by(self) -> str:
        return self.modified_by_

    @modified_by.setter
    def modified_by(self, value: str) -> None:
        self.modified_by_ = value

    @classmethod
    def generate_secure_random_string(cls, length: int = 10) -> str:
        if length < 3:
            raise ValueError("Cannot generate a secure random string of length < 3")
        return "".join(
            [
                str(crr.choice(string.ascii_uppercase + string.digits))
                for _ in range(length)
            ]
        )

    def generate_password_hash(self, password: str) -> str:
        if not self.password_salt:
            raise RuntimeError("Password_salt does not exist")
        code_bytes = bytes(password, "utf8")
        salt_bytes = bytes(self.password_salt, "utf8")
        _hash: bytes = scrypt(code_bytes, salt_bytes, 256, 16384, 8, 1)  # type: ignore
        return codecs.encode(_hash, "hex_codec").decode()

    def set_password(self, password: str) -> None:
        self.password_salt = self.generate_secure_random_string(32)
        self.password_hash = self.generate_password_hash(password)

    def validate_password(self, password: str) -> bool:
        if not self.password_salt or not self.password_hash:
            logger.warning(
                "Login for clinician %s attempted prior to password generation",
                self.uuid,
            )
            return False

        if self.generate_password_hash(password) == self.password_hash:
            return True

        return False

    def _latest_terms_agreement_by_product(self) -> Dict[str, Dict]:
        """
        Returns a dictionary mapping product name to TermsAgreement (as a dict).
        For each product the TermsAgreement that is used is the one with the highest
        version number.

        Only products where the clinician has agreed to terms are included in the dict.
        """
        tos = itertools.groupby(
            sorted(
                self.terms_agreement,
                key=lambda x: (x.product_name, x.version),
                reverse=True,
            ),
            key=lambda x: x.product_name,
        )
        return {k: next(g).to_dict() for k, g in tos}

    def to_dict(self) -> Dict[str, Any]:
        analytics_consent = {}
        if self.analytics_consent is not None:
            analytics_consent = {"analytics_consent": self.analytics_consent}

        return {
            "job_title": self.job_title,
            "send_entry_identifier": self.send_entry_identifier,
            "nhs_smartcard_number": self.nhs_smartcard_number,
            "professional_registration_number": self.professional_registration_number,
            "agency_name": self.agency_name,
            "agency_staff_employee_number": self.agency_staff_employee_number,
            "email_address": self.email_address,
            "locations": self.locations,
            "bookmarks": self.bookmarks,
            "bookmarked_patients": self.bookmarked_patients,
            "terms_agreement": self._latest_terms_agreement_by_product(),
            "login_active": self.login_active,
            "groups": self.groups,
            "products": [p.to_dict() for p in self.products],
            "can_edit_ews": self.can_edit_ews,
            "can_edit_encounter": self.can_edit_encounter,
            "contract_expiry_eod_date": self.contract_expiry_eod_date,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            **analytics_consent,
            **self.pack_identifier(),
        }

    def to_auth_dict(self) -> Dict[str, Any]:
        return {
            "job_title": self.job_title,
            "send_entry_identifier": self.send_entry_identifier,
            "locations": self.locations,
            "login_active": self.login_active,
            "contract_expiry_eod_date": self.contract_expiry_eod_date,
            "groups": self.groups,
            "products": [p.to_dict() for p in self.products],
            **self.pack_identifier(),
        }

    def to_login_dict(self) -> Dict[str, Any]:
        return {
            "job_title": self.job_title,
            "email_address": self.email_address,
            "user_id": self.uuid,
            "groups": self.groups,
            "products": [p.to_dict() for p in self.products if p.closed_date is None],
            "can_edit_ews": self.can_edit_ews,
            "can_edit_encounter": self.can_edit_encounter,
        }

    def to_compact_dict(self) -> Dict[str, str]:
        return {
            "job_title": self.job_title,
            "email_address": self.email_address,
            "first_name": self.first_name,
            "last_name": self.last_name,
            **self.pack_identifier(),
        }

    @classmethod
    def new(
        cls,
        uuid: Optional[str] = None,
        products: Sequence[Dict] = (),
        **kw: Any,
    ) -> "User":
        if not uuid:
            uuid = generate_uuid()

        user: User = User(
            uuid=uuid,
            **kw,
        )

        if products:
            for p in products:
                user.products.append(
                    Product.new(
                        user_id=user.uuid,
                        **p,
                    )
                )

        db.session.add(user)

        return user

    def update(
        self,
        products: Optional[List[dict]] = None,
        **kw: Any,
    ) -> None:
        if products:
            for p1 in products:
                if "uuid" in p1:
                    Product.query.get(p1["uuid"]).update(**p1)
                else:
                    if p1.get("closed_date", None) is None:
                        if any(
                            p2.product_name == p1["product_name"]
                            and p2.closed_date is None
                            for p2 in self.products
                        ):
                            raise ValueError("Cannot add duplicate open product")
                    self.products.append(Product.new(**p1))
        for k in kw:
            setattr(self, k, kw[k])

    @classmethod
    def schema(cls) -> Dict:
        return {
            "optional": {
                "login_active": bool,
                "contract_expiry_eod_date": str,
                "send_entry_identifier": str,
                "bookmarks": [str],
                "bookmarked_patients": [str],
                "can_edit_ews": bool,
                "can_edit_encounter": bool,
                "professional_registration_number": str,
                "agency_name": str,
                "agency_staff_employee_number": str,
                "email_address": str,
                "booking_reference": str,
                "analytics_consent": bool,
            },
            "required": {
                "first_name": str,
                "last_name": str,
                "phone_number": str,
                "job_title": str,
                "nhs_smartcard_number": str,
                "locations": [str],
                "groups": [str],
                "products": [dict],
            },
            "updatable": {
                "first_name": str,
                "last_name": str,
                "job_title": str,
                "login_active": bool,
                "contract_expiry_eod_date": str,
                "phone_number": str,
                "nhs_smartcard_number": str,
                "send_entry_identifier": str,
                "email_address": str,
                "locations": [str],
                "groups": [str],
                "products": [dict],
                "bookmarks": [str],
                "can_edit_ews": bool,
                "can_edit_encounter": bool,
                "professional_registration_number": str,
                "agency_name": str,
                "agency_staff_employee_number": str,
                "booking_reference": str,
                "analytics_consent": bool,
            },
        }
