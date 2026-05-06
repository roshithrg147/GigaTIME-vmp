from enum import Enum

class JobStatus(str, Enum):
    """Represents the status of a GigaTIME processing job."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
