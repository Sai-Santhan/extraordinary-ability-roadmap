from app.agents.base import BaseAgent
from app.models.schemas import CriteriaAssessment
from app.prompts.assessment import ASSESSMENT_SYSTEM, ASSESSMENT_USER
from app.prompts.shared import CONFIDENCE_RUBRIC, USCIS_EB1A_CRITERIA


class AssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="assessment",
            system_prompt=ASSESSMENT_SYSTEM.format(
                uscis_criteria=USCIS_EB1A_CRITERIA,
                confidence_rubric=CONFIDENCE_RUBRIC,
            ),
            user_prompt_template=ASSESSMENT_USER,
            output_schema=CriteriaAssessment,
        )

    async def run(self, profile_json: str, pathway: str = "EB-1A") -> dict:
        return await super().run(profile_json=profile_json, pathway=pathway)
