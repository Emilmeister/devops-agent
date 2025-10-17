from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.auth import AuthCredential
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.mcp_tool import MCPTool
from google.adk.tools.mcp_tool.mcp_session_manager import retry_on_closed_resource
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset
)
from google.genai import types
from mcp import ListToolsResult
from typing_extensions import override

short_info_to_user_what_you_do_desc = "В параметр short_info_to_user_what_you_do пиши краткое описание что ты сейчас собираешься сделать. Старайся чтобы они были разными у разных вызовов тулов и не повторялись"
smart_reasoning_desc = "В параметре smart_reasoning поразмышляй над тем что ты уже сделал и что еще нужно сделать чтобы удовлетворить пользователя. Этот параметр тула всегда пиши первым!"

class MCPToolWithHeaders(MCPTool):

    async def run_async_headers(
            self, *, args: dict[str, Any], tool_context: ToolContext, headers: dict
    ) -> Any:
        credential = None
        if self._credentials_manager:
            credential = await self._credentials_manager.get_auth_credential(
                tool_context
            )
            if not credential:
                await self._credentials_manager.request_credential(tool_context)
                return self._response_for_auth_required or "Pending User Authorization."

        return await self._run_async_impl(
            args=args,
            tool_context=tool_context,
            credential=credential,
            headers=headers
        )

    @retry_on_closed_resource
    @override
    async def _run_async_impl(
            self, *, args, tool_context: ToolContext, credential: AuthCredential, headers: dict
    ):
        """Runs the tool asynchronously.

        Args:
            args: The arguments as a dict to pass to the tool.
            tool_context: The tool context of the current invocation.

        Returns:
            Any: The response from the tool.
        """
        # Extract headers from credential for session pooling
        auth_headers = await self._get_headers(tool_context, credential)
        if auth_headers is None:
            auth_headers = {}
        headers = headers | auth_headers

        logging.info(f'headers={headers}')

        # Get the session from the session manager
        session = await self._mcp_session_manager.create_session(headers=headers)

        response = await session.call_tool(self.name, arguments=args)
        return response


class CallMcpTool(BaseTool):
    """Generic wrapper for *any* MCP tool across configured servers.

    Instead of returning the actual tool result, it:
      - stores the raw result in an in-memory store
      - returns {function_result_id, estimated_tokens, server, tool}
    """
    def __init__(self, base_tool: MCPToolWithHeaders):
        self.base_tool = base_tool
        super().__init__(
            name=base_tool.name,
            description=base_tool.description + "\n\n" + smart_reasoning_desc + "\n\n" + short_info_to_user_what_you_do_desc
        )

    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        declaration = self.base_tool._get_declaration()
        smart_reasoning_cortage = ('smart_reasoning', types.Schema(
            type=types.Type.STRING,
            title='Поразмышляй над тем что ты уже сделал и что еще нужно сделать чтобы удовлетворить пользователя. Этот параметр тула всегда пиши первым!'
        ))
        short_info_to_user_what_you_do_cortage = ('short_info_to_user_what_you_do', types.Schema(
            type=types.Type.STRING,
            title='Краткое описание что ты сейчас собираешься сделать.'
        ))
        ordered_properties = OrderedDict([smart_reasoning_cortage, short_info_to_user_what_you_do_cortage] + [(k, v) for k, v in declaration.parameters.properties.items()])
        declaration.parameters.properties = ordered_properties

        if declaration.parameters.required is None:
            declaration.parameters.required = []

        declaration.parameters.required = declaration.parameters.required + ['smart_reasoning', 'short_info_to_user_what_you_do']
        return declaration

    async def run_async(self, tool_context: ToolContext, args: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"tool_call {self.name}, args={args},  tool_context.state={tool_context.state.to_dict()}")
        if 'short_info_to_user_what_you_do' in args:
            del args['short_info_to_user_what_you_do']
        if 'smart_reasoning' in args:
            del args['smart_reasoning']
        return await self.base_tool.run_async_headers(tool_context=tool_context, args=args, headers=tool_context.state['headers'])



class McpProxyToolset(MCPToolset):
    def __init__(
            self,
            *,
            connection_params,
    ):
        super().__init__(
            connection_params=connection_params,
        )

    async def get_tools(
      self,
      readonly_context: Optional[ReadonlyContext] = None,
      ) -> List[BaseTool]:
        session = await self._mcp_session_manager.create_session()

        # Fetch available tools from the MCP server
        tools_response: ListToolsResult = await session.list_tools()

        # Apply filtering based on context and tool_filter
        tools = []
        for tool in tools_response.tools:
            mcp_tool = MCPToolWithHeaders(
                mcp_tool=tool,
                mcp_session_manager=self._mcp_session_manager,
                auth_scheme=self._auth_scheme,
                auth_credential=self._auth_credential,
            )
            if self._is_tool_selected(mcp_tool, readonly_context):
                tools.append(mcp_tool)

        tools = [CallMcpTool(base_tool=tool) for tool in tools]
        return tools
