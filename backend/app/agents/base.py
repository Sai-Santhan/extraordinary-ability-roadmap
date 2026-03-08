import json
from typing import AsyncGenerator

import anthropic

from app.config import settings


class BaseAgent:
    def __init__(self, name: str, system_prompt: str, user_prompt_template: str, output_schema: type):
        self.name = name
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.output_schema = output_schema
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run(self, **kwargs) -> dict:
        user_prompt = self.user_prompt_template.format(**kwargs)
        schema_json = json.dumps(self.output_schema.model_json_schema(), indent=2)

        system_with_schema = (
            self.system_prompt
            + "\n\nYou MUST respond with ONLY valid JSON matching this schema. "
            "No markdown, no code fences, no explanation — just the JSON object.\n\n"
            f"JSON Schema:\n{schema_json}"
        )

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16384,
            temperature=0.2,
            system=system_with_schema,
            messages=[{"role": "user", "content": user_prompt}],
        )

        text = response.content[0].text
        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return json.loads(text)

    async def run_streaming(self, **kwargs) -> AsyncGenerator[dict, None]:
        yield {"agent": self.name, "status": "started"}
        try:
            result = await self.run(**kwargs)
            yield {"agent": self.name, "status": "completed", "result": result}
        except Exception as e:
            yield {"agent": self.name, "status": "error", "error": str(e)}
