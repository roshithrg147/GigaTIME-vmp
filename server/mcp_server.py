import json
import logging
from typing import Any, Dict, List

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
                # Retrieve the tool from our single source of truth
                tool = self.registry.get_tool(name)
                
                # Execute the registered handler safely
                result = await tool.handler(**arguments)
                
                # Convert the result to text content as required by MCP
                if not isinstance(result, str):
                    try:
                        result_text = json.dumps(result, indent=2)
                    except TypeError:
                        result_text = str(result)
                else:
                    result_text = result
                    
                return [TextContent(type="text", text=result_text)]
                
            except ValueError as e:
                logger.error(f"Tool missing error: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
            except Exception as e:
                logger.exception(f"Unexpected error executing tool '%s'", name)
                return [TextContent(type="text", text=f"Runtime error executing '{name}': {str(e)}")]
