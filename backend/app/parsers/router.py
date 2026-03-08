from app.parsers.pdf_parser import parse_pdf
from app.parsers.mbox_parser import parse_mbox
from app.parsers.ics_parser import parse_ics
from app.parsers.json_parser import parse_chatgpt_export, parse_google_takeout_json
from app.parsers.linkedin_parser import parse_linkedin_pdf
from app.parsers.image_parser import parse_image

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def parse_text(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    return {"text": text}


def parse_json_generic(file_path: str) -> dict:
    import json
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"text": json.dumps(data, indent=2), "data": data}


PARSER_MAP = {
    ("pdf", "cv"): parse_pdf,
    ("pdf", "linkedin"): parse_linkedin_pdf,
    ("txt", "cv"): parse_text,
    ("txt", "linkedin"): parse_text,
    ("mbox", "gmail"): parse_mbox,
    ("ics", "calendar"): parse_ics,
    ("json", "chatgpt_export"): parse_chatgpt_export,
    ("json", "google_takeout"): parse_google_takeout_json,
    ("json", "scholar"): parse_json_generic,
    ("json", "github"): parse_json_generic,
    ("json", "manual"): parse_json_generic,
}


def route_parser(file_type: str, source_type: str, file_path: str) -> dict:
    # Image files always use vision parser
    if file_type in IMAGE_EXTENSIONS:
        return parse_image(file_path)

    parser = PARSER_MAP.get((file_type, source_type))
    if not parser:
        # Fallback: try matching by file type alone
        for (ft, _), p in PARSER_MAP.items():
            if ft == file_type:
                parser = p
                break
    if not parser:
        # Last resort: read as plain text
        parser = parse_text
    return parser(file_path)
