from pydantic import BaseModel, Field
from typing import List

class SpatialSummaryResult(BaseModel):
    """The structured interpretation response returned by the Gemini integration."""
    status: str = Field(
        ...,
        description="Status of the summarization (e.g., SUCCESS, FAILED)."
    )
    job_id: str = Field(
        ...,
        description="The associated job ID."
    )
    biomarker_findings: List[str] = Field(
        ...,
        description="Direct observations based exclusively on provided biomarker data."
    )
    spatial_architecture: str = Field(
        ...,
        description="Description of the spatial context and arrangements."
    )
    biological_hypotheses: List[str] = Field(
        ...,
        description="Inferred biological hypotheses drawn cautiously from the observations."
    )
    clinical_summary: str = Field(
        ...,
        description="Overall concise clinical interpretation."
    )
    limitations: List[str] = Field(
        ...,
        description="Limitations of the evidence or analysis."
    )
    disclaimer: str = Field(
        ...,
        description="Explicit medical disclaimer stating this is clinician-support only, not a standalone diagnosis."
    )
