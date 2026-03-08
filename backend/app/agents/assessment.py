import logging
import re

from app.agents.base import BaseAgent
from app.models.schemas import CriteriaAssessment
from app.prompts.assessment import ASSESSMENT_SYSTEM, ASSESSMENT_USER
from app.prompts.shared import (
    CONFIDENCE_RUBRIC,
    PATHWAY_NOTES,
    PATHWAY_REGISTRY,
    THRESHOLD_GUIDANCE,
)
from app.services.vector_db import query as rag_query

logger = logging.getLogger(__name__)


def _normalize_pathway_key(pathway: str) -> str:
    """Convert display pathway (e.g. 'EB-1A', 'EB1A') to registry key ('eb1a')."""
    return re.sub(r"[-_]", "", pathway).lower()


def _build_rag_context(profile_summary: str, pathway_key: str) -> str:
    """Query the vector DB for relevant legal passages and format as context."""
    try:
        # Query with pathway filter first
        results = rag_query(
            text=f"{pathway_key} criteria assessment evidence standards",
            n_results=4,
            pathway_filter=pathway_key,
        )
        # Also get general guidance
        general = rag_query(
            text=profile_summary[:500],
            n_results=2,
            pathway_filter="all",
        )
        results.extend(general)
    except Exception as e:
        logger.warning(f"RAG query failed, proceeding without legal context: {e}")
        return ""

    if not results:
        return ""

    passages = []
    for r in results:
        source = r["metadata"].get("source", "USCIS")
        passages.append(f"[{source}]\n{r['text'].strip()}")

    context = "\n\n---\n\n".join(passages)
    return f"""RELEVANT LEGAL CONTEXT (use these authoritative sources to ground your assessment):

{context}

Use the above legal context to inform your criteria evaluation. Cite specific standards
or frameworks when they apply to the evidence being assessed."""


class AssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="assessment",
            system_prompt="",  # Set dynamically in run()
            user_prompt_template=ASSESSMENT_USER,
            output_schema=CriteriaAssessment,
        )

    async def run(self, profile_json: str, pathway: str = "EB-1A") -> dict:
        pathway_key = _normalize_pathway_key(pathway)
        registry = PATHWAY_REGISTRY.get(pathway_key, PATHWAY_REGISTRY["eb1a"])

        # Build RAG context from vector DB
        rag_context = _build_rag_context(profile_json[:1000], pathway_key)

        self.system_prompt = ASSESSMENT_SYSTEM.format(
            display_name=registry["display_name"],
            legal_framework=registry["legal_framework"],
            criteria_text=registry["criteria_text"],
            confidence_rubric=CONFIDENCE_RUBRIC,
            pathway_specific_notes=PATHWAY_NOTES[pathway_key],
            criteria_count=registry["criteria_count"],
            threshold_guidance=THRESHOLD_GUIDANCE[pathway_key],
            rag_context=rag_context,
        )

        return await super().run(
            profile_json=profile_json,
            pathway=pathway,
            criteria_count=registry["criteria_count"],
            display_name=registry["display_name"],
        )
