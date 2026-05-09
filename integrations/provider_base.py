from abc import ABC, abstractmethod
from typing import Any, Dict


class GigatimeProvider(ABC):
    """Abstract base for all GigaTIME inference backends."""

    @abstractmethod
    async def submit_job(self, payload: Dict[str, Any]) -> str:
        """Submit a job and return a job_id string."""
        ...

    @abstractmethod
    async def poll_job(self, job_id: str) -> Dict[str, Any]:
        """Return current job state: {status, result?, error?}"""
        ...
