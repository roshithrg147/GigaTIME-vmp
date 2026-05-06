import asyncio
from typing import Any, Dict

from models.job_status import JobStatus
from store.job_store import JobStore

class AzureIntegrator:
    """Mock integration layer for asynchronous Azure processing."""
    
    def __init__(self, job_store: JobStore) -> None:
        self.job_store = job_store

    def submit_job(self, payload: Dict[str, Any]) -> str:
        """Stores the job and triggers asynchronous processing."""
        job_id = self.job_store.create_job(payload)
        
        # Trigger background processing without blocking
        asyncio.create_task(self._process_slide_async(job_id))
        
        return job_id

    async def _process_slide_async(self, job_id: str) -> None:
        """Simulates asynchronous processing of a slide on Azure."""
        # Update status to RUNNING
        self.job_store.update_job(job_id, JobStatus.RUNNING)
        
        # Simulate processing time
        await asyncio.sleep(3)
        
        # Mock result data
        mock_result = {
            "biomarkers": {
                "CD8": "Positive",
                "PD-L1": "Negative",
                "FoxP3": "Positive"
            },
            "confidence_score": 0.95
        }
        
        # Update status to DONE with result
        self.job_store.update_job(job_id, JobStatus.DONE, result=mock_result)
