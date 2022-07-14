# -*- coding: utf-8 -*-

from flask_batteries_included.sqldb import db
from she_logging.logging import logger

from dhos_users_api.models.product import Product
from dhos_users_api.models.terms_agreement import TermsAgreement
from dhos_users_api.models.user import User


def reset_database() -> None:
    """Drops SQL data"""
    try:
        for model in (Product, TermsAgreement, User):
            db.session.query(model).delete()
        db.session.commit()
    except Exception:
        logger.exception("Drop SQL data failed")
        db.session.rollback()
