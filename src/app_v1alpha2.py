import logging
import os
import re
import time
from typing import Any

import dotenv
from flask import Blueprint, Flask
from pydantic import BaseModel
from theoriq import ExecuteContext, ExecuteResponse, ExecuteRuntimeError
from theoriq.agent import AgentDeploymentConfiguration
from theoriq.api.v1alpha2 import ConfigureContext
from theoriq.api.v1alpha2.configure import AgentConfigurator
from theoriq.api.v1alpha2.schemas import ExecuteRequestBody
from theoriq.biscuit import TheoriqBudget, TheoriqCost
from theoriq.dialog import CodeItemBlock, TextItemBlock
from theoriq.dialog.data import DataItemBlock
from theoriq.extra.flask.logging import init_logging, list_routes
from theoriq.extra.flask.v1alpha2.flask import theoriq_blueprint
from theoriq.types import Currency, Metric

logger = logging.getLogger(__name__)
regex = r"^\d+$"


class AwesomeConfig(BaseModel):
    prefix: str
    offset: int


def build_schema():
    return AwesomeConfig.model_json_schema()


def deployed_agent_blueprint() -> Blueprint:
    agent_config = AgentDeploymentConfiguration.from_env("DEPLOYED_")
    # Create and register theoriq blueprint
    blueprint = Blueprint("deployed", __name__)
    blueprint.register_blueprint(theoriq_blueprint(agent_config, execute), url_prefix="/deployed")
    return blueprint


def configurable_agent_blueprint() -> Blueprint:
    agent_config = AgentDeploymentConfiguration.from_env("CONFIGURABLE_")
    # Create and register theoriq blueprint
    blueprint = Blueprint("configurable", __name__)
    agent_configurator = AgentConfigurator(configure_fn=configure, is_long_running_fn=is_long_running)
    blueprint.register_blueprint(
        theoriq_blueprint(agent_config, execute, build_schema(), agent_configurator),
        url_prefix="/configurable",
    )
    return blueprint


def is_long_running(_context: ConfigureContext, config: Any) -> bool:
    awesome_config = AwesomeConfig(**config)
    return awesome_config.offset > 10


def configure(_context: ConfigureContext, config: Any) -> None:
    awesome_config = AwesomeConfig(**config)

    if awesome_config.offset % 2 == 1:
        raise ValueError("Offset must be an even number")

    time.sleep(awesome_config.offset)


def execute(context: ExecuteContext, req: ExecuteRequestBody) -> ExecuteResponse:
    logger.warning(f"Received request: {context.request_id.replace('-', '')}")
    if req.last_item is None:
        raise ExecuteRuntimeError("no item in dialog")

    last_block = req.last_item.blocks[0]
    expression = last_block.data.text

    tokens = expression.split(" ", 1)
    if tokens[0].startswith("error"):
        raise ExecuteRuntimeError(
            f"This is an error: {tokens[-1]}",
            message="Occurs because the prompt starts with error",
        )

    if re.match(regex, expression):
        number = int(expression)
        context.send_event(f"Now multiplying: {number} * 2")
        context.send_metric(Metric(name="number_of_multiplications", value=1))
        result = number * 2
    else:
        raise ExecuteRuntimeError(f"Invalid expression: {expression}")

    configuration = context.agent_configuration or {"prefix": "", "offset": 0}
    return context.new_response(
        blocks=[
            TextItemBlock(text=f"{configuration['prefix']}! The result is {result + configuration['offset']}"),
            CodeItemBlock(code=f"def multiply() -> int:\n    return {number} * 2", language="python"),
            DataItemBlock(data=f"multiply,{result}", data_type="csv"),
        ],
        cost=TheoriqCost(amount=result, currency=Currency.USDC),
    )


def main():
    dotenv.load_dotenv()
    app = Flask(__name__)
    init_logging(app, logging.INFO)

    # Create and register theoriq blueprint
    app.register_blueprint(deployed_agent_blueprint())
    app.register_blueprint(configurable_agent_blueprint())

    list_routes(app)
    app.run(host="0.0.0.0", port=int(os.environ["PORT"]))


if __name__ == "__main__":
    main()
