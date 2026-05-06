from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WSIPayload(BaseModel):
    """Payload representing a Whole Slide Image (WSI) for processing."""
    
    image_path: str = Field(
        ..., 
        description="The path to the Whole Slide Image (WSI)."
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Optional metadata associated with the slide."
    )

    def to_json(self) -> dict:
        """Returns the payload serialized to a dictionary using Pydantic v2 conventions."""
        return self.model_dump()
