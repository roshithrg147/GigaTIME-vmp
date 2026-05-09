
import json
import logging
import asyncio
from typing import Dict, Any

from google import genai
from google.genai import types

from models.spatial_summary_result import SpatialSummaryResult

logger = logging.getLogger(__name__)

class GeminiInterpreter:
    """Service to interpret deterministic spatial data using Gemini."""
    
    def __init__(self):
        from config.settings import get_settings
        settings = get_settings()
        self.model_name = settings.gemini_model
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def summarize_spatial_architecture(
        self,
        job_id: str,
        biomarker_result: Dict[str, Any],
        report_style: str = "concise",
        audience: str = "oncologist",
        include_limitations: bool = True
    ) -> SpatialSummaryResult:
        """
        Sends structured biomarker data to Gemini to generate a clinical summary.
        """
        logger.info(f"Generating spatial summary for job {job_id} using {self.model_name}")
        
        persona_map = {
            "oncologist": (
                "You are assisting a board-certified oncologist reviewing precision "
                "medicine eligibility. Prioritize PD-L1 status, TMB signals, and "
                "CD8 infiltration patterns."
            ),
            "pathologist": (
                "You are assisting a clinical pathologist interpreting tissue architecture. "
                "Prioritize spatial density gradients, immune phenotype classification, "
                "and entropy patterns."
            ),
            "researcher": (
                "You are assisting a translational research scientist. "
                "Prioritize mechanistic hypotheses and signal combinations without "
                "clinical language constraints."
            ),
        }
        persona_prefix = persona_map.get(
            audience,
            f"You are assisting a medical professional specializing in {audience}."
        )

        system_instruction = (
            persona_prefix + "\n\n"
            "You are a clinical interpretation assistant for virtual proteomics outputs. "
            "You must adhere strictly to the following rules:\n"
            "1. Use ONLY the evidence provided in the input payload.\n"
            "2. Separate direct observations from inferred biological hypotheses.\n"
            "3. Avoid definitive diagnosis language.\n"
            "4. Avoid treatment recommendations.\n"
            "5. State uncertainty when evidence is limited.\n"
            f"6. {'Include limitations of the evidence' if include_limitations else 'Do not focus extensively on limitations'}.\n"
            "7. ALWAYS include a non-diagnostic disclaimer stating this is clinician-support only.\n"
            "8. DO NOT invent numeric values, biomarkers, mutations, or literature citations.\n"
            f"9. Tailor the language and tone for a {audience}.\n"
            f"10. The report style should be {report_style}."
        )

        OR_LOGIC_BLOCK = (
            "\n\nSIGNAL COMBINATION LOGIC — apply strictly to biological_hypotheses ONLY:\n"
            "- If PD_L1 density > 50 AND CD8 density > 30: "
            "consider immune-active phenotype hypothesis.\n"
            "- If PD_L1 density > 50 AND CD8 density < 20: "
            "consider immune-excluded phenotype hypothesis.\n"
            "- If spatial_metrics entropy > 3.0 AND immune_phenotype contains 'excluded': "
            "consider TMB-H in silico hypothesis.\n"
            "- If CD20 density > 20 AND CD8 density > 30: "
            "consider tertiary lymphoid structure signal.\n"
            "Label each hypothesis with a confidence level: HIGH, MODERATE, or LOW.\n"
            "If data is insufficient to evaluate a condition, do not generate a hypothesis for it."
        )

        prompt = (
            f"Job ID: {job_id}\n\n"
            f"Biomarker and Spatial Evidence:\n"
            f"{json.dumps(biomarker_result, indent=2)}"
            f"{OR_LOGIC_BLOCK}\n\n"
            "Generate the structured clinical interpretation based strictly on the above data."
        )

        try:
            # We use the modern genai SDK. Structured output uses the Pydantic schema.
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=SpatialSummaryResult,
                    temperature=0.0  # Force maximum determinism
                )
            )
            
            # The SDK automatically parses the JSON into the pydantic model if response_schema is provided,
            # but as a fallback, we can parse the text.
            if hasattr(response, "parsed") and isinstance(response.parsed, SpatialSummaryResult):
                return response.parsed
                
            return SpatialSummaryResult.model_validate_json(response.text)
            
        except Exception as e:
            logger.error(f"Failed to generate summary for job {job_id}: {e}")
            # Fail safely according to requirements
            return SpatialSummaryResult(
                status="FAILED",
                job_id=job_id,
                biomarker_findings=[],
                spatial_architecture="Analysis failed.",
                biological_hypotheses=[],
                clinical_summary=f"Error generating interpretation: {str(e)}",
                limitations=["Analysis interrupted by technical error."],
                disclaimer="This is an automated error message, not clinical advice."
            )
