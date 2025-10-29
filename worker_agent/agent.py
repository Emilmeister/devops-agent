from __future__ import annotations
from typing import Dict

import yaml
from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext

from worker_agent.model import llm_model
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
from worker_agent.mcp_reasoning_and_events_wrapper import McpProxyToolset

from phoenix.otel import register
from dotenv import load_dotenv
from worker_agent.settings import settings

load_dotenv()

if settings.enable_phoenix.lower() == 'true':
    register(
        project_name=settings.phoenix_project_name,
        endpoint=settings.phoenix_endpoint,
        auto_instrument=True
    )

with open('prompts.yaml', "r", encoding="utf8") as f:
    prompts = yaml.safe_load(f)


def header_provider(ctx: ReadonlyContext) -> Dict[str, str]:
    return ctx.state['temp:headers']

mcp_tool_set = McpProxyToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=settings.mcp_url,
        sse_read_timeout=10.0 * 60,
        timeout=10.0 * 60
    ),
    header_provider=header_provider
)

async def get_instruction(context):
    return prompts.get('devops_agent_prompt')

devops_agent = Agent(
    model=llm_model,
    name="devops_agent",
    description="""
        Senior developer и senior devops агент который имеет доступ к виртуальным машинам.
        Твоя задача развернуть на них сервис или сервисы которые хочет пользователь.
        Для этого можешь использовать любые команды терминала.
    """,
    instruction=get_instruction,
    tools=[mcp_tool_set],
)

root_agent = devops_agent
