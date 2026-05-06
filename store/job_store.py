from typing import Any, Dict, Optional
import uuid

from models.job_status import JobStatus

class JobStore:
    """In-memory storage for GigaTIME processing jobs."""
    
    def __init__(self) -> None:
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, payload: Dict[str, Any]) -> str:
        """Create a new job in PENDING state and return its job_id."""
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "status": JobStatus.PENDING.value,
            "payload": payload,
            "result": None
        }
        return job_id

    def update_job(self, job_id: str, status: JobStatus, result: Optional[Dict[str, Any]] = None) -> None:
        """Update the status and optional result of a job."""
        if job_id not in self._jobs:
            raise ValueError(f"Job {job_id} not found.")
        
        self._jobs[job_id]["status"] = status.value
        if result is not None:
            self._jobs[job_id]["result"] = result

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a job's current state."""
        return self._jobs.get(job_id)
