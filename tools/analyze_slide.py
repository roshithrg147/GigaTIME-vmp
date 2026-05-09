import asyncio
import uuid
from typing import Any, Dict

from integrations.azure_integrator import AzureIntegrator
from models.job_status import JobStatus
from models.wsi_payload import WSIPayload
from tools.base_tool import BaseTool


class AnalyzeSlideTool(BaseTool):
    """Tool for initiating a virtual mIF staining job on an H&E slide."""
    
    def __init__(self, azure_integrator: AzureIntegrator) -> None:
        self.azure_integrator = azure_integrator
        
    @property
    def name(self) -> str:
        return "analyze_slide"
        
    @property
    def description(self) -> str:
        return "Initiates a GigaTIME virtual mIF staining job on an H&E slide and returns a job_id for polling."
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return WSIPayload.model_json_schema()
        
    async def handler(self, **kwargs) -> Dict[str, Any]:
        # Validate input precisely using the WSIPayload pydantic model
        payload = WSIPayload(**kwargs)
        
        # Simulate small delay
        await asyncio.sleep(1)
        
        # Submit job to Azure integrator asynchronously
        job_id = await self.azure_integrator.submit_job(payload.to_json())
        
        return {
            "status": JobStatus.PENDING.value,
            "message": "Slide analysis job initiated successfully.",
            "job_id": job_id,
            "image_processed": payload.image_path
        }
