import json
import logging
from typing import Any, Dict, List

from pydantic import ValidationError

from mcp.server import Server
from mcp.types import TextContent, Tool as MCPTool

from .registry import ToolRegistry

logger = logging.getLogger(__name__)

class GigaTIMEMCPServer:
    """Wrapper around the official MCP server."""
    
    def __init__(self, name: str = "gigatime-mcp-server") -> None:
        self.app = Server(name)
        self.registry = ToolRegistry()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Wire up the core MCP protocol handlers."""
        
        @self.app.list_tools()
        async def list_tools() -> List[MCPTool]:
            return self.registry.get_all_tool_schemas()

        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            try:
                tool = self.registry.get_tool(name)
                result = await tool.handler(**arguments)

                if not isinstance(result, str):
                    try:
                        result_text = json.dumps(result, indent=2)
                    except TypeError:
                        result_text = str(result)
                else:
                    result_text = result

                return [TextContent(type="text", text=result_text)]

            except ValueError as e:
                logger.error(f"Tool missing or validation error: {e}")
                return [TextContent(type="text", text=f"Bad Request: {str(e)}")]

            except KeyError as e:
                logger.error(f"Missing required parameter in tool payload: {e}")
                return [TextContent(type="text",
                                    text=f"Input Error: Missing required parameter {str(e)}")]

            except ValidationError as e:
                logger.error(f"Pydantic validation error in tool '{name}': {e}")
                return [TextContent(type="text", text=f"Validation Error: {str(e)}")]

            except Exception as e:
                logger.exception(f"Systemic failure executing tool '{name}'")
                return [TextContent(type="text",
                                    text=f"Internal Server Error in '{name}': {str(e)}")]
