"""PII scrubber for redacting contact-level personally identifiable information.

Redacts: email addresses, phone numbers, SSNs, physical addresses, dates of birth.
Preserves: person names, org names, publication venues, metrics, dates (non-DOB).
"""

import json
import os
import re

# --- Regex Patterns ---

EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
)

# US/international phone formats:
# (555) 123-4567, 555-123-4567, 555.123.4567, +1 555 123 4567, +91-98765-43210
PHONE_RE = re.compile(
    r'(?<!\d)'                          # not preceded by digit
    r'(?:'
    r'\+\d{1,3}[\s\-.]?'               # international prefix
    r')?'
    r'(?:'
    r'\(?\d{3}\)?[\s\-.]?'             # area code
    r'\d{3}[\s\-.]?'                   # first 3 digits
    r'\d{4}'                           # last 4 digits
    r')'
    r'(?!\d)',                          # not followed by digit
)

SSN_RE = re.compile(
    r'\b\d{3}-\d{2}-\d{4}\b',
)

# Date of birth indicators followed by a date
DOB_RE = re.compile(
    r'(?:date\s+of\s+birth|DOB|born\s+on|birthdate|birth\s+date)'
    r'\s*[:\-]?\s*'
    r'('
    r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}'   # MM/DD/YYYY or similar
    r'|[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}'       # January 15, 1990
    r'|\d{1,2}\s+[A-Z][a-z]+\s+\d{4}'         # 15 January 1990
    r')',
    re.IGNORECASE,
)

# US street addresses: "123 Main St" optionally followed by city, state, zip
# This is intentionally conservative to avoid false positives
US_ADDRESS_RE = re.compile(
    r'\b\d{1,5}\s+'                             # street number
    r'(?:[A-Z][a-z]+\s+){1,3}'                  # street name words
    r'(?:St(?:reet)?|Ave(?:nue)?|Blvd|Boulevard|Dr(?:ive)?|Rd|Road|Ln|Lane|Way|Ct|Court|Pl(?:ace)?|Cir(?:cle)?|Pkwy|Parkway)\b'
    r'(?:'
    r'[,.\s]+'                                  # separator
    r'(?:[A-Z][a-z]+[\s,]*){1,2}'               # city
    r',?\s*[A-Z]{2}\s+'                         # state abbreviation
    r'\d{5}(?:-\d{4})?'                         # zip code
    r')?',
)

# Mbox "From:" / "To:" header lines with email addresses
MBOX_HEADER_EMAIL_RE = re.compile(
    r'^((?:From|To|Cc|Bcc)\s*:\s*)(.*)$',
    re.MULTILINE | re.IGNORECASE,
)


def scrub_text(text: str) -> str:
    """Scrub contact-level PII from free-form text.

    Redacts emails, phones, SSNs, DOBs, and US addresses.
    Preserves names, org names, and all other content.
    """
    if not text:
        return text

    # Order matters: SSN before phone (SSN pattern is more specific)
    text = SSN_RE.sub('[ID REDACTED]', text)
    text = EMAIL_RE.sub('[EMAIL REDACTED]', text)
    text = DOB_RE.sub(lambda m: m.group(0).replace(m.group(1), '[DOB REDACTED]'), text)
    text = US_ADDRESS_RE.sub('[ADDRESS REDACTED]', text)
    text = PHONE_RE.sub('[PHONE REDACTED]', text)

    return text


def scrub_email_headers(text: str) -> str:
    """Strip email addresses from From/To/Cc/Bcc header lines in mbox-style text."""
    if not text:
        return text

    def _redact_header(match: re.Match) -> str:
        prefix = match.group(1)
        value = match.group(2)
        # Remove email addresses but keep display names
        cleaned = EMAIL_RE.sub('[EMAIL REDACTED]', value)
        return prefix + cleaned

    return MBOX_HEADER_EMAIL_RE.sub(_redact_header, text)


def scrub_file_on_disk(file_path: str, source_type: str) -> None:
    """Redact PII in the uploaded file on disk.

    For text-based files (txt, json, mbox, ics): read, scrub, overwrite.
    For PDFs: extract text, scrub, write as .txt replacement.
    For images: skip (can't text-edit; DB extracted_text is scrubbed separately).
    """
    if not file_path or not os.path.exists(file_path):
        return

    ext = os.path.splitext(file_path)[1].lower()

    # Images: skip
    if ext in ('.jpg', '.jpeg', '.png', '.webp'):
        return

    # PDF: extract text, scrub, write as .txt
    if ext == '.pdf':
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            full_text = "\n".join(page.get_text() for page in doc)
            doc.close()
            scrubbed = scrub_text(full_text)
            txt_path = file_path.rsplit('.', 1)[0] + '.scrubbed.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(scrubbed)
            # Remove original PDF, keep scrubbed text
            os.remove(file_path)
        except ImportError:
            pass  # PyMuPDF not available; skip PDF scrubbing
        return

    # Text-based files: read, scrub, overwrite
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        scrubbed = scrub_text(content)
        if source_type in ('gmail', 'mbox'):
            scrubbed = scrub_email_headers(scrubbed)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(scrubbed)
    except (OSError, UnicodeDecodeError):
        pass  # Skip files that can't be read as text


def scrub_json_strings(data):
    """Recursively scrub PII from all string values in a JSON-like structure."""
    if isinstance(data, str):
        return scrub_text(data)
    if isinstance(data, list):
        return [scrub_json_strings(item) for item in data]
    if isinstance(data, dict):
        return {key: scrub_json_strings(value) for key, value in data.items()}
    return data
