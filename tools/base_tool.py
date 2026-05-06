from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """Abstract base class defining the contract for all GigaTIME MCP tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the tool."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the tool does."""
        pass
        
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """The JSON schema defining the expected inputs."""
        pass
        
    @abstractmethod
    async def handler(self, **kwargs) -> Any:
        """The asynchronous handler containing the tool logic."""
        pass
