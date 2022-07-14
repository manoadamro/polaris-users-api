from environs import Env
from flask import Flask


class Configuration:
    env = Env()
    DISABLE_CREATE_USER_IN_AUTH0: bool = env.bool("DISABLE_CREATE_USER_IN_AUTH0", False)


def init_config(app: Flask) -> None:
    app.config.from_object(Configuration)
