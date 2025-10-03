from __future__ import annotations
import os

from google.adk.agents import Agent
from worker_agent.model import llm_model
from google.adk.tools.mcp_tool import SseConnectionParams
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

mcp_tool_set = McpProxyToolset(
    connection_params=SseConnectionParams(
        url=os.getenv("MCP_URL"),
        sse_read_timeout=10.0 * 60
    )
)

async def get_instruction(context):
    return """
    Ты senior developer и senior devops агент который имеет доступ к виртуальным машинам.
    Твоя задача развернуть на них сервис или сервисы которые хочет пользователь.
    Для этого можешь использовать любые команды терминала.
    Используй преимущественно docker и docker compose для поднятия сервисов, если пользователь не просит что-то иное.
    Во всех виртуальных машинах веди основную работу в папке /devops_agent_services (создай если ее нет).
    Перед тем как начинать работу на виртуальной машине узнай, существует ли файл /devops_agent_services/vm_info.md и прочти его.
    В конце когда нужно отдать url для доступа к сервису вызывай тул get_host_info чтобы посмотреть ip адрес виртуальной машины.

    ВАЖНО: Все манипуляции с виртуальной машиной, какие на ней развернуты сервисы и прочее что помогло бы тебе не забыть состояние виртуальной машины записывай в файл /devops_agent_services/vm_info.md (создай если его нет)
    """

devops_agent = Agent(
    model=llm_model,
    name="devops_agent",
    description="""
        Ты senior developer и senior devops агент который имеет доступ к виртуальным машинам.
        Твоя задача развернуть на них сервис или сервисы которые хочет пользователь.
        Для этого можешь использовать любые команды терминала.
    """,
    instruction=get_instruction,
    tools=[mcp_tool_set],
)

root_agent = devops_agent
