from typing import Any, Dict

from tools.base_tool import BaseTool
from store.job_store import JobStore

class FetchBiomarkersTool(BaseTool):
    """Tool for fetching virtual mIF results for a job_id."""
    
    def __init__(self, job_store: JobStore) -> None:
        self.job_store = job_store
        
    @property
    def name(self) -> str:
        return "fetch_biomarkers"
        
    @property
    def description(self) -> str:
        return "Fetches virtual mIF results for a job_id."
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "The job_id returned by analyze_slide."
                }
            },
            "required": ["job_id"]
        }
        
    async def handler(self, **kwargs) -> Dict[str, Any]:
        job_id = kwargs.get("job_id")
        if not job_id:
            return {"error": "job_id is required."}
            
        job = await self.job_store.get_job(job_id)
        if not job:
            return {"error": f"Job {job_id} not found."}
            
        status = job["status"]
        if status == "DONE":
            return {
                "job_id": job_id,
                "status": status,
                "result": job.get("result")
            }
        else:
            return {
                "job_id": job_id,
                "status": status,
                "message": f"Job is currently {status}. Please check back later."
            }
