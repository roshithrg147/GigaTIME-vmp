import asyncio
import logging
import os
from typing import Any, Dict

from models.job_status import JobStatus
from store.job_store import JobStore
from integrations.preprocessing import load_and_tile_slide
from integrations.prediction_reducer import reduce_predictions

logger = logging.getLogger(__name__)


class AzureIntegrator:
    """
    GigaTIME inference integrator using the official healthcareai_toolkit
    GigaTimeClient. Falls back to mock mode if Azure endpoint is not configured,
    which preserves local dev / test workflows without credentials.
    """

    MOCK_MODE_SENTINEL = "MOCK"

    def __init__(self, job_store: JobStore) -> None:
        self.job_store = job_store
        self._client = None
        self._use_mock = False
        self._init_client()

    def _init_client(self) -> None:
        endpoint_name = os.getenv("GIGATIME_MODEL_ENDPOINT", "")
        if not endpoint_name or endpoint_name == self.MOCK_MODE_SENTINEL:
            logger.warning(
                "GIGATIME_MODEL_ENDPOINT not set or set to MOCK. "
                "Running in mock mode — real inference disabled."
            )
            self._use_mock = True
            return

        try:
            from healthcareai_toolkit.clients.medimage.gigatime import GigaTimeClient
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential()
            self._client = GigaTimeClient(
                endpoint_name=endpoint_name,
                credential=credential,
            )
            logger.info(
                "GigaTimeClient initialized with endpoint: %s", endpoint_name
            )
        except Exception as exc:
            logger.error(
                "Failed to initialize GigaTimeClient: %s. Falling back to mock.", exc
            )
            self._use_mock = True

    def submit_job(self, payload: Dict[str, Any]) -> str:
        """Create a job in the store and kick off async processing."""
        job_id = self.job_store.create_job(payload)
        asyncio.create_task(self._process_slide_async(job_id, payload))
        return job_id

    async def _process_slide_async(
        self, job_id: str, payload: Dict[str, Any]
    ) -> None:
        """Run preprocessing → GigaTIME inference → tensor reduction."""
        self.job_store.update_job(job_id, JobStatus.RUNNING)

        try:
            image_path = payload.get("image_path", "")
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._run_inference, image_path
            )
            self.job_store.update_job(job_id, JobStatus.DONE, result=result)
            logger.info("Job %s completed. Tile count: %d", job_id, result.get("tile_count", 0))

        except Exception as exc:
            logger.exception("Job %s failed: %s", job_id, exc)
            self.job_store.update_job(
                job_id,
                JobStatus.FAILED,
                result={"error": str(exc)},
            )

    def _run_inference(self, image_path: str) -> Dict[str, Any]:
        """
        Synchronous inference path (called via run_in_executor):
        1. Tile the slide using healthcareai_toolkit ImageReader
        2. Submit tiles to GigaTimeClient or generate mock output
        3. Reduce 4D float32 tensors to structured biomarker JSON
        """
        tiles = load_and_tile_slide(image_path)
        logger.info("Loaded %d tiles from %s", len(tiles), image_path)

        if self._use_mock or self._client is None:
            predictions = self._mock_predictions(len(tiles))
        else:
            predictions = self._client.submit(image_list=tiles)

        return reduce_predictions(predictions)

    @staticmethod
    def _mock_predictions(n_tiles: int):
        """Generate reproducible synthetic predictions for mock/test mode."""
        import numpy as np
        rng = np.random.default_rng(seed=42)
        return [
            rng.random((23, 256, 256)).astype(np.float32)
            for _ in range(max(n_tiles, 1))
        ]
