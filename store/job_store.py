# NOTE FOR CLOUD RUN DEPLOYMENT:
# This implementation uses a SQLite file on the local container filesystem.
# On Cloud Run (stateless, scales to zero), this file is NOT shared between
# container instances. This implementation is correct for single-instance
# or local development. For true multi-instance Cloud Run production use,
# replace the sqlite3 backend with Cloud Firestore, Cloud SQL (PostgreSQL),
# or a Redis-backed implementation.
# The interface (create_job / update_job / get_job) remains unchanged —
# only the backend implementation needs to change.

import asyncio
import json
import sqlite3
import uuid
from typing import Any, Dict, Optional

from config.settings import get_settings
from models.job_status import JobStatus


class JobStore:
    """Persistent SQLite-backed storage for GigaTIME processing jobs."""

    def __init__(self) -> None:
        settings = get_settings()
        self.db_path = settings.database_url.replace("sqlite:///", "")
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id  TEXT PRIMARY KEY,
                    status  TEXT NOT NULL,
                    payload TEXT,
                    result  TEXT
                )
                """
            )
            conn.commit()

    async def create_job(self, payload: Dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        payload_str = json.dumps(payload)

        def _insert() -> None:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO jobs (job_id, status, payload, result) "
                    "VALUES (?, ?, ?, ?)",
                    (job_id, JobStatus.PENDING.value, payload_str, None),
                )
                conn.commit()

        await asyncio.to_thread(_insert)
        return job_id

    async def update_job(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        result_str = json.dumps(result) if result is not None else None

        def _update() -> None:
            with sqlite3.connect(self.db_path) as conn:
                if result_str is not None:
                    conn.execute(
                        "UPDATE jobs SET status = ?, result = ? WHERE job_id = ?",
                        (status.value, result_str, job_id),
                    )
                else:
                    conn.execute(
                        "UPDATE jobs SET status = ? WHERE job_id = ?",
                        (status.value, job_id),
                    )
                conn.commit()

        await asyncio.to_thread(_update)

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        def _fetch() -> Optional[Dict[str, Any]]:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT job_id, status, payload, result "
                    "FROM jobs WHERE job_id = ?",
                    (job_id,),
                ).fetchone()
                if row is None:
                    return None
                return {
                    "job_id": row["job_id"],
                    "status": row["status"],
                    "payload": json.loads(row["payload"]) if row["payload"] else None,
                    "result": json.loads(row["result"]) if row["result"] else None,
                }

        return await asyncio.to_thread(_fetch)
