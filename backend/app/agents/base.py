import json
import logging
import re
from typing import AsyncGenerator

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

# Patterns that may indicate prompt injection in uploaded documents
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*:", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?prior", re.IGNORECASE),
    re.compile(r"<\s*/?system\s*>", re.IGNORECASE),
    re.compile(r"override\s+(your|the)\s+instructions", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+are", re.IGNORECASE),
    re.compile(r"act\s+as\s+if\s+you", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
]


def detect_injection(text: str) -> list[str]:
    """Scan text for potential prompt injection patterns. Returns list of matched patterns."""
    matches = []
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            matches.append(pattern.pattern)
    return matches


def _validate_confidence_scores(data: dict) -> list[str]:
    """Check that confidence scores are within valid ranges (0-100)."""
    warnings = []
    if "criteria" in data and isinstance(data["criteria"], list):
        for criterion in data["criteria"]:
            conf = criterion.get("confidence", {})
            if isinstance(conf, dict):
                for key in ("data_confidence", "criteria_match", "overall"):
                    val = conf.get(key)
                    if val is not None and (not isinstance(val, (int, float)) or val < 0 or val > 100):
                        warnings.append(f"Invalid confidence score {key}={val} for criterion {criterion.get('criterion_name', '?')}")
    return warnings


class BaseAgent:
    def __init__(self, name: str, system_prompt: str, user_prompt_template: str, output_schema: type):
        self.name = name
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.output_schema = output_schema
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run(self, **kwargs) -> dict:
        user_prompt = self.user_prompt_template.format(**kwargs)

        # Scan user input for potential prompt injection
        injection_matches = detect_injection(user_prompt)
        safety_metadata = {}
        if injection_matches:
            logger.warning(f"[{self.name}] Potential prompt injection detected: {injection_matches}")
            safety_metadata["injection_warning"] = True
            safety_metadata["flagged_patterns"] = len(injection_matches)

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

        result = json.loads(text)

        # Post-processing: validate output
        confidence_warnings = _validate_confidence_scores(result)
        if confidence_warnings:
            logger.warning(f"[{self.name}] Confidence validation: {confidence_warnings}")
            safety_metadata["confidence_warnings"] = confidence_warnings

        if safety_metadata:
            result["_safety_metadata"] = safety_metadata

        return result

    async def run_streaming(self, **kwargs) -> AsyncGenerator[dict, None]:
        yield {"agent": self.name, "status": "started"}
        try:
            result = await self.run(**kwargs)
            yield {"agent": self.name, "status": "completed", "result": result}
        except Exception as e:
            yield {"agent": self.name, "status": "error", "error": str(e)}
