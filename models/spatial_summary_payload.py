from pydantic import BaseModel, Field

class SpatialSummaryPayload(BaseModel):
    """Payload representing the validated input for the spatial architecture summarization."""
    job_id: str = Field(
        ...,
        description="The ID of the completed job containing the biomarker and spatial results."
    )
    report_style: str = Field(
        default="concise",
        description="The desired style of the clinical report (e.g., concise, detailed)."
    )
    include_limitations: bool = Field(
        default=True,
        description="Whether to explicitly include medical limitations in the output."
    )
    audience: str = Field(
        default="oncologist",
        description="The target clinical audience for the summary (e.g., oncologist, pathologist)."
    )
