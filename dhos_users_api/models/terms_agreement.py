from datetime import datetime, timezone
from typing import Any, Dict

from flask_batteries_included.helpers import generate_uuid
from flask_batteries_included.sqldb import ModelIdentifier, db


class TermsAgreement(ModelIdentifier, db.Model):
    product_name = db.Column(db.String, unique=False, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("user.uuid"), index=True)
    version = db.Column(db.Integer, nullable=True)
    accepted_timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )
    tou_version = db.Column(db.Integer, nullable=True)
    tou_accepted_timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )
    patient_notice_version = db.Column(db.Integer, nullable=True)
    patient_notice_accepted_timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
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
    def new(cls, uuid: str = None, **kw: Any) -> "TermsAgreement":
        if not uuid:
            uuid = generate_uuid()

        ta = TermsAgreement(uuid=uuid, **kw)

        # Default timestamps if required.
        time_now = datetime.now(tz=timezone.utc)
        if ta.version and not ta.accepted_timestamp:
            ta.accepted_timestamp = time_now
        if ta.tou_version and not ta.tou_accepted_timestamp:
            ta.tou_accepted_timestamp = time_now
        if ta.patient_notice_version and not ta.patient_notice_accepted_timestamp:
            ta.patient_notice_accepted_timestamp = time_now

        db.session.add(ta)
        return ta

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "product_name": self.product_name,
            **self.pack_identifier(),
        }
        if self.version:
            result.update(
                {
                    "version": self.version,
                    "accepted_timestamp": self.accepted_timestamp.isoformat(
                        timespec="milliseconds"
                    ),
                }
            )
        if self.tou_version:
            result.update(
                {
                    "tou_version": self.tou_version,
                    "tou_accepted_timestamp": self.tou_accepted_timestamp.isoformat(
                        timespec="milliseconds"
                    ),
                }
            )
        if self.patient_notice_version:
            result.update(
                {
                    "patient_notice_version": self.patient_notice_version,
                    "patient_notice_accepted_timestamp": self.patient_notice_accepted_timestamp.isoformat(
                        timespec="milliseconds"
                    ),
                }
            )
        return result

    @classmethod
    def schema(cls) -> Dict:
        raise NotImplementedError
