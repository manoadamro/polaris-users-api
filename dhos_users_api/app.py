from pathlib import Path

import connexion
import kombu_batteries_included
from connexion import FlaskApp
from flask import Flask
from flask_batteries_included import augment_app as fbi_augment_app
from flask_batteries_included import sqldb
from flask_batteries_included.config import is_not_production_environment

from dhos_users_api.blueprint_api import clinicians_blueprint
from dhos_users_api.blueprint_development import development_blueprint
from dhos_users_api.config import init_config
from dhos_users_api.helpers.cli import add_cli_command


def create_app(testing: bool = False) -> Flask:
    openapi_dir: Path = Path(__file__).parent / "openapi"
    connexion_app: FlaskApp = connexion.App(
        __name__,
        specification_dir=openapi_dir,
        options={"swagger_ui": is_not_production_environment()},
    )
    connexion_app.add_api("openapi.yaml", strict_validation=True)

    app: Flask = fbi_augment_app(
        app=connexion_app.app,
        use_pgsql=True,
        use_sqlite=False,
        testing=testing,
        use_auth0=True,
        use_customdb_auth0=True,
    )

    # Apply config
    init_config(app)

    # Initialise k-b-i library to allow publishing to RabbitMQ.
    kombu_batteries_included.init()

    # Configure the sqlalchemy connection.
    sqldb.init_db(app=app, testing=testing)

    # API blueprint registration
    app.register_blueprint(clinicians_blueprint)
    app.logger.info("Registered API blueprint")

    if is_not_production_environment():
        app.register_blueprint(development_blueprint)
        app.logger.info("Registered development blueprint")

    add_cli_command(app)

    return app
