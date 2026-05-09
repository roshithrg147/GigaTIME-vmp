import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from store.job_store import JobStore
from integrations.azure_integrator import AzureIntegrator
from integrations.gemini_interpreter import GeminiInterpreter
from tools.analyze_slide import AnalyzeSlideTool
from tools.fetch_biomarkers import FetchBiomarkersTool
from tools.summarize_spatial_architecture import SummarizeSpatialArchitectureTool

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="GigaTIME-VMP API", version="0.6.0")

# ─── Dependency wiring ────────────────────────────────────────────────────────
job_store = JobStore()
azure_integrator = AzureIntegrator(job_store=job_store)
gemini_interpreter = GeminiInterpreter()

analyze_tool = AnalyzeSlideTool(azure_integrator=azure_integrator)
fetch_tool = FetchBiomarkersTool(job_store=job_store)
summarize_tool = SummarizeSpatialArchitectureTool(
    job_store=job_store,
    gemini_interpreter=gemini_interpreter,
)


# ─── Models ───────────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    image_path: str
    patient_id: str | None = None
    notes: str | None = None


class SummarizeRequest(BaseModel):
    job_id: str


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.6.0"}


@app.post("/analyze_slide")
async def analyze_slide(request: AnalyzeRequest):
    try:
        return await analyze_tool.handler(**request.model_dump())
    except Exception as exc:
        logger.exception("analyze_slide failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    try:
        return await fetch_tool.handler(job_id=job_id)
    except Exception as exc:
        logger.exception("fetch_biomarkers failed for job_id=%s", job_id)
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/summarize_spatial_architecture")
async def summarize_spatial_architecture(request: SummarizeRequest):
    try:
        return await summarize_tool.handler(job_id=request.job_id)
    except Exception as exc:
        logger.exception("summarize_spatial_architecture failed")
        raise HTTPException(status_code=500, detail=str(exc))
