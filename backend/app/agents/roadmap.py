from app.agents.base import BaseAgent
from app.models.schemas import ImmigrationRoadmap
from app.prompts.roadmap import ROADMAP_SYSTEM, ROADMAP_USER


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
        return await super().run(
            assessment_json=assessment_json,
            name=name, field=field, pathway=pathway,
            timeline_years=timeline_years, strongest=strongest,
            weakest=weakest, focus=focus, profile_id=profile_id,
        )
