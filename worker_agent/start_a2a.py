import os

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import DatabaseTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

from worker_agent.agent_task_manager import MyAgentExecutor

from worker_agent.settings import settings

# ==========================
# НАСТРОЙКА ЛОГГЕРА
# ==========================
import logging

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
# ==========================

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        capabilities = AgentCapabilities(streaming=True)
        my_agent_executor = MyAgentExecutor()
        agent_card = AgentCard(
            name=settings.agent_name,
            description=settings.agent_description,
            url=settings.agent_url,
            version=settings.agent_version,
            default_input_modes=my_agent_executor.agent.SUPPORTED_CONTENT_TYPES,
            default_output_modes=my_agent_executor.agent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[],
            supports_authenticated_extended_card=True
        )
        request_handler = DefaultRequestHandler(
            agent_executor=my_agent_executor,
            task_store=DatabaseTaskStore(
                engine=create_async_engine(settings.db_a2a_url)
            ),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
        import uvicorn

        uvicorn.run(server.build(), host='0.0.0.0', port=int(settings.port))
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        exit(1)


if __name__ == '__main__':
    main()
