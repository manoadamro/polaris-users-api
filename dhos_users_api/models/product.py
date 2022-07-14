from typing import Any, Dict, Optional

from flask_batteries_included.helpers import generate_uuid
from flask_batteries_included.sqldb import ModelIdentifier, db
from sqlalchemy import Column, Date, ForeignKey, String, func


class Product(ModelIdentifier, db.Model):
    product_name = Column(String, nullable=False)
    opened_date = Column(
        Date,
        unique=False,
        nullable=False,
        default=func.now(),
    )
    closed_date = Column(
        Date,
        unique=False,
        nullable=True,
        default=None,
    )
    closed_reason = Column(String, nullable=True)
    closed_reason_other = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("user.uuid"), index=True)

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
    def schema(cls) -> Dict[str, Dict[str, type]]:
        return {
            "optional": {"closed_date": str},
            "required": {"product_name": str, "opened_date": str},
            "updatable": {"product_name": str, "opened_date": str, "closed_date": str},
        }

    @classmethod
    def new(cls, uuid: str = None, **kw: Any) -> "Product":
        if not uuid:
            uuid = generate_uuid()

        product = Product(uuid=uuid, **kw)
        db.session.add(product)
        return product

    def update(self, product_name: str, **kw: Any) -> None:
        if product_name != self.product_name:
            clinician_products = Product.query.filter_by(user_id=self.user_id).all()

            for prod in clinician_products:
                if (
                    prod is not self
                    and prod.product_name == product_name
                    and prod.closed_date is None
                ):
                    raise ValueError(f"User is already active on {product_name}")
            self.product_name = product_name

        for key, key_type in self.schema()["updatable"].items():
            if key in kw:
                value = kw[key]
                if not isinstance(value, key_type):
                    raise TypeError(f"Product.{key}")
                setattr(self, key, value)

        db.session.add(self)

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "product_name": self.product_name,
            "opened_date": self.opened_date,
            "closed_date": self.closed_date,
            **self.pack_identifier(),
        }
