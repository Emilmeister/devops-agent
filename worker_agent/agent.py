from __future__ import annotations
import os

import yaml
from google.adk.agents import Agent
from worker_agent.model import llm_model
from google.adk.tools.mcp_tool import StreamableHTTPConnectionParams
from worker_agent.mcp_reasoning_and_events_wrapper import McpProxyToolset

from phoenix.otel import register
from dotenv import load_dotenv

load_dotenv()

if os.getenv('ENABLE_PHOENIX', 'false').lower() == 'true':
    register(
        project_name=os.getenv("PHOENIX_PROJECT_NAME"),
        endpoint=os.getenv("PHOENIX_ENDPOINT"),
        auto_instrument=True
    )

with open('prompts.yaml', "r", encoding="utf8") as f:
    prompts = yaml.safe_load(f)

mcp_tool_set = McpProxyToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=os.getenv("MCP_URL"),
        sse_read_timeout=10.0 * 60,
        timeout=10.0 * 60
    )
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
