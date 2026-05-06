from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List

from mcp.types import Tool as MCPTool


@dataclass
class Tool:
    """Internal representation of a registered MCP tool."""
    schema: MCPTool
    handler: Callable[..., Awaitable[Any]]


class ToolRegistry:
    """Registry for managing MCP tools and their handlers."""
    
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, name: str, description: str, input_schema: dict, handler: Callable[..., Awaitable[Any]]) -> None:
        """Register a new tool with the given schema and handler."""
        schema = MCPTool(
            name=name,
            description=description,
            inputSchema=input_schema
        )
        self._tools[name] = Tool(schema=schema, handler=handler)

    def get_tool(self, name: str) -> Tool:
        """Retrieve a registered tool by name. Raises ValueError if not found."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def get_all_tool_schemas(self) -> List[MCPTool]:
        """Return a list of all registered tool schemas in MCP format."""
        return [tool.schema for tool in self._tools.values()]
