from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset
)
from google.genai import types

short_info_to_user_what_you_do_desc = "В параметр short_info_to_user_what_you_do пиши краткое описание что ты сейчас собираешься сделать. Старайся чтобы они были разными у разных вызовов тулов и не повторялись"
smart_reasoning_desc = "В параметре smart_reasoning поразмышляй над тем что ты уже сделал и что еще нужно сделать чтобы удовлетворить пользователя. Этот параметр тула всегда пиши первым!"

class CallMcpTool(BaseTool):
    """Generic wrapper for *any* MCP tool across configured servers.

    Instead of returning the actual tool result, it:
      - stores the raw result in an in-memory store
      - returns {function_result_id, estimated_tokens, server, tool}
    """
    def __init__(self, base_tool: BaseTool):
        self.base_tool = base_tool
        super().__init__(
            name=base_tool.name,
            description=base_tool.description + "\n\n" + short_info_to_user_what_you_do_desc
        )

    def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
        declaration = self.base_tool._get_declaration()
        declaration.parameters.properties['smart_reasoning'] = types.Schema(
            type=types.Type.STRING,
            title='Поразмышляй над тем что ты уже сделал и что еще нужно сделать чтобы удовлетворить пользователя. Этот параметр тула всегда пиши первым!'
        )
        declaration.parameters.properties['short_info_to_user_what_you_do'] = types.Schema(
            type=types.Type.STRING,
            title='Краткое описание что ты сейчас собираешься сделать.'
        )
        return declaration

    async def run_async(self, tool_context: ToolContext, args: Dict[str, Any]) -> Dict[str, Any]:
        logging.info(f"tool_call {self.name}, args={args}")
        if 'short_info_to_user_what_you_do' in args:
            del args['short_info_to_user_what_you_do']
        if 'smart_reasoning' in args:
            del args['smart_reasoning']
        return await self.base_tool.run_async(tool_context=tool_context, args=args)



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
        tools = await super().get_tools()

        tools = [CallMcpTool(base_tool=tool) for tool in tools]
        return tools

    async def get_original_tools(self):
        return await super().get_tools()
