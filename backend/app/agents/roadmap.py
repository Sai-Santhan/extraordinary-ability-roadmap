import logging
import re

from app.agents.base import BaseAgent
from app.models.schemas import ImmigrationRoadmap
from app.prompts.roadmap import ROADMAP_SYSTEM, ROADMAP_USER
from app.services.vector_db import query as rag_query

logger = logging.getLogger(__name__)


def _normalize_pathway_key(pathway: str) -> str:
    return re.sub(r"[-_]", "", pathway).lower()


def _build_roadmap_rag_context(pathway: str, weakest: str, field: str) -> str:
    """Query vector DB for strategy guidance relevant to weak criteria and field."""
    try:
        pathway_key = _normalize_pathway_key(pathway)
        results = rag_query(
            text=f"{pathway} strengthen weak criteria {weakest} {field}",
            n_results=3,
            pathway_filter=pathway_key,
        )
        general = rag_query(
            text=f"{field} immigration evidence building strategy",
            n_results=2,
            pathway_filter="all",
        )
        results.extend(general)
    except Exception as e:
        logger.warning(f"RAG query failed for roadmap, proceeding without: {e}")
        return ""

    if not results:
        return ""

    passages = []
    for r in results:
        source = r["metadata"].get("source", "USCIS")
        passages.append(f"[{source}]\n{r['text'].strip()}")

    context = "\n\n---\n\n".join(passages)
    return f"""
RELEVANT LEGAL CONTEXT (use to inform roadmap recommendations):

{context}

Reference these standards when recommending specific actions to strengthen criteria."""


class RoadmapAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="roadmap",
            system_prompt=ROADMAP_SYSTEM,
            user_prompt_template=ROADMAP_USER,
            output_schema=ImmigrationRoadmap,
        )

    async def run(self, assessment_json: str, name: str, field: str,
                  pathway: str, timeline_years: int, strongest: str,
                  weakest: str, focus: str, profile_id: str) -> dict:
        # Inject RAG context into the system prompt for this run
        rag_context = _build_roadmap_rag_context(pathway, weakest, field)
        if rag_context:
            self.system_prompt = ROADMAP_SYSTEM + rag_context

        return await super().run(
            assessment_json=assessment_json,
            name=name, field=field, pathway=pathway,
            timeline_years=timeline_years, strongest=strongest,
            weakest=weakest, focus=focus, profile_id=profile_id,
        )
