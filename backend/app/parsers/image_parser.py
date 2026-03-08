"""Image parser using Claude Vision API to extract text from document images."""

import base64
import mimetypes

import anthropic

from app.config import settings

VISION_PROMPT = """Analyze this document image and extract all relevant information.

1. Describe the document type (certificate, letter, article, patent, award, etc.)
2. Extract ALL text visible in the image
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

FULL EXTRACTED TEXT:
[all text from the image]"""


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
