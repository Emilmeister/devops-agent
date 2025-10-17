import os
from typing import Dict, Any, AsyncGenerator
import asyncio
import logging
import traceback

from google.adk.auth.credential_service.session_state_credential_service import SessionStateCredentialService
from google.genai import types
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import Session, DatabaseSessionService

from worker_agent.agent import devops_agent

logger = logging.getLogger("agents_logger")


def truncate_string(text: str, limit: int = 100) -> str:
    """
    Обрезает строку до указанного количества символов.
    Если строка длиннее, добавляет '...' в конце.
    """
    if len(text) > limit:
        return text[:limit] + "..."
    return text


class A2Aagent:
    def __init__(self):
        # Initialize runner storage
        self.agent = devops_agent
        self.runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            # todo Заменить на свой
            artifact_service=InMemoryArtifactService(),
            session_service=DatabaseSessionService(db_url=os.getenv("DB_URL")),
            # todo Заменить на свой
            memory_service=InMemoryMemoryService(),
            credential_service=SessionStateCredentialService()
        )

    async def get_session(self, session_id: str, headers: dict) -> Session:
        session = await self.runner.session_service.get_session(
            app_name=self.agent.name,
            user_id='a2a_user',
            session_id=session_id
        )

        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.agent.name,
                user_id='a2a_user',
                session_id=session_id,
                state={'headers': headers}
            )

        return session

    async def invoke(self, query: str, session_id: str, metadata: dict) -> Dict[str, Any]:
        """Stream the agent's processing and responses."""
        session = await self.get_session(session_id, metadata)

        content = types.Content(
            role='user',
            parts=[types.Part.from_text(text=query)],
        )
        last_event = None
        async for event in self.runner.run_async(
                user_id=session.user_id, session_id=session.id, new_message=content
        ):
            last_event = event

        response = '\n'.join(p.text for p in last_event.content.parts if p.text)

        # Format the response
        return {
            "is_task_complete": True,
            "require_user_input": False,
            "content": response,
            "is_error": False,
            "is_event": False
        }


    async def stream(self, query: str, session_id: str, metadata: dict) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream the agent's processing and responses."""
        session = await self.get_session(session_id, metadata)

        content = types.Content(
            role='user',
            parts=[types.Part.from_text(text=query)],
        )
        last_event = None
        try:
            async for event in self.runner.run_async(
                    user_id=session.user_id, session_id=session.id, new_message=content
            ):
                logger.info(f'self.runner.run_async {event}')
                for part in event.content.parts:
                    if part.function_call is not None:
                        if 'short_info_to_user_what_you_do' in part.function_call.args:
                            yield {
                                "is_task_complete": True,
                                "require_user_input": False,
                                "content": part.function_call.args['short_info_to_user_what_you_do'],
                                "is_error": False,
                                "is_event": True
                            }
                        if 'command' in part.function_call.args:
                            yield {
                                "is_task_complete": True,
                                "require_user_input": False,
                                "content": f'Вызов команды:\n```bash\n{truncate_string(part.function_call.args['command'])}\n```',
                                "is_error": False,
                                "is_event": True
                            }
                    # if part.function_response is not None:
                    #     if part.function_response.name == 'execute_ssh_command':
                    #         # Находим позицию 'STDOUT:' и берем все после него
                    #         try:
                    #             stdout_index = part.function_response.response['result'].content[0].text.find('STDOUT:')
                    #             stderr_index = part.function_response.response['result'].content[0].text.find('STDERR:')
                    #             if stderr_index == -1:
                    #                 stderr_index = len(part.function_response.response['result'].content[0].text)
                    #             command_result = part.function_response.response['result'].content[0].text[stdout_index + len('STDOUT:'):stderr_index].strip()
                    #             yield {
                    #                 "is_task_complete": True,
                    #                 "require_user_input": False,
                    #                 "content": f'Результат выполнения команды:\n```bash\n{command_result}\n```',
                    #                 "is_error": False,
                    #                 "is_event": True
                    #             }
                    #         except Exception as e:
                    #             logging.error(traceback.format_exc())
                    #             yield {
                    #                 "is_task_complete": True,
                    #                 "require_user_input": False,
                    #                 "content": f'{part.function_response.response['result'].content[0]}',
                    #                 "is_error": False,
                    #                 "is_event": True
                    #             }

                last_event = event

            response = '\n'.join(p.text for p in last_event.content.parts if p.text)

            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response,
                "is_error": False,
                "is_event": False
            }
        except Exception as e:
            logging.error(traceback.format_exc())
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Произошла ошибка при вызове агента",
                "is_error": True,
                "is_event": False
            }


    # For compatibility with the original implementation
    def sync_invoke(self, query: str, session_id: str, metadata: dict) -> Dict[str, Any]:
        """Synchronous wrapper for invoke."""
        return asyncio.run(self.invoke(query, session_id, metadata))

    # For compatibility with the original API
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]