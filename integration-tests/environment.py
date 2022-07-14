from behave import use_step_matcher
from behave.model import Scenario
from behave.runner import Context
from clients.users_api_client import drop_all_data
from helpers.jwt import get_system_token
from she_logging import logger

use_step_matcher("re")


def before_scenario(context: Context, scenario: Scenario) -> None:
    drop_all_data(get_system_token())


def after_scenario(context: Context, scenario: Scenario) -> None:
    drop_all_data(get_system_token())
    if scenario.status == "failed":
        logger.warning('scenario failed: "%s"', scenario.name)
        logger.warning(
            f"Response was: {context.response.status_code} {context.response.json()}"
        )
