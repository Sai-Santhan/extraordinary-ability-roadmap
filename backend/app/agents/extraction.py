from app.agents.base import BaseAgent
from app.models.schemas import ImmigrationProfile
from app.prompts.extraction import EXTRACTION_SYSTEM, EXTRACTION_USER
from app.prompts.shared import CONFIDENCE_RUBRIC


class ExtractionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="extraction",
            system_prompt=EXTRACTION_SYSTEM,
            user_prompt_template=EXTRACTION_USER,
            output_schema=ImmigrationProfile,
        )

    async def run(self, raw_career_data_json: str) -> dict:
        return await super().run(
            raw_text=raw_career_data_json,
            confidence_rubric=CONFIDENCE_RUBRIC,
        )
