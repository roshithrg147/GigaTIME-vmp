from typing import Any, Dict

from models.spatial_summary_payload import SpatialSummaryPayload
from models.spatial_summary_result import SpatialSummaryResult
from store.job_store import JobStore
from integrations.gemini_interpreter import GeminiInterpreter
from models.job_status import JobStatus
from tools.base_tool import BaseTool

class SummarizeSpatialArchitectureTool(BaseTool):
    """Tool to summarize the spatial architecture using Gemini."""
    
    def __init__(self, job_store: JobStore, gemini_interpreter: GeminiInterpreter):
        self.job_store = job_store
        self.gemini_interpreter = gemini_interpreter

    @property
    def name(self) -> str:
        return "summarize_spatial_architecture"

    @property
    def description(self) -> str:
        return "Interprets completed GigaTIME biomarker/spatial outputs into a structured clinician-support summary."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return SpatialSummaryPayload.model_json_schema()

    async def handler(self, **kwargs) -> Any:
        # Validate input
        try:
            payload = SpatialSummaryPayload(**kwargs)
        except Exception as e:
            return {"status": "FAILED", "error": f"Invalid payload: {e}"}

        # Fetch job from JobStore
        job = await self.job_store.get_job(payload.job_id)
        if not job:
            return {"status": "FAILED", "error": f"Job {payload.job_id} does not exist."}

        if job["status"] != JobStatus.DONE.value:
            return {"status": "PENDING", "message": f"Job {payload.job_id} is currently {job['status']}."}

        # Validate biomarker results
        result = job.get("result")
        if not result:
            return {"status": "FAILED", "error": f"Biomarker results are missing for job {payload.job_id}."}

        # Generate interpretation
        summary_result: SpatialSummaryResult = await self.gemini_interpreter.summarize_spatial_architecture(
            job_id=payload.job_id,
            biomarker_result=result,
            report_style=payload.report_style,
            audience=payload.audience,
            include_limitations=payload.include_limitations
        )

        # Return as structured dict
        return summary_result.model_dump()
