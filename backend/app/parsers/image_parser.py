"""Image parser using Claude Vision API to extract text from document images."""

import base64
import mimetypes

import anthropic

from app.config import settings

VISION_PROMPT = """Analyze this document image and extract relevant information for immigration evidence assessment.

1. Describe the document type (certificate, letter, article, patent, award, etc.)
2. Extract text visible in the image, with the following PRIVACY rules:
   - DO NOT include email addresses — replace with [EMAIL REDACTED]
   - DO NOT include phone numbers — replace with [PHONE REDACTED]
   - DO NOT include physical/mailing addresses — replace with [ADDRESS REDACTED]
   - DO NOT include social security numbers or ID numbers — replace with [ID REDACTED]
   - DO keep names of people, organizations, institutions, dates, and achievements
3. Identify key details:
   - Issuing organization or institution
   - Dates (issued, valid, event dates)
   - Names of people mentioned
   - Any evidence of achievement, recognition, or contribution
   - Quantitative data (amounts, rankings, metrics)

Format your response as:
DOCUMENT TYPE: [type]
ISSUING ORGANIZATION: [org or N/A]
DATE: [date or N/A]
KEY DETAILS:
- [detail 1]
- [detail 2]

EXTRACTED TEXT:
[text from the image, with contact PII redacted as described above]"""


def parse_image(file_path: str) -> dict:
    """Extract text and metadata from a document image using Claude Vision."""
    mime_type = mimetypes.guess_type(file_path)[0] or "image/jpeg"

    with open(file_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": VISION_PROMPT,
                    },
                ],
            }
        ],
    )

    extracted_text = response.content[0].text
    return {"text": extracted_text, "source": "vision_extraction"}
