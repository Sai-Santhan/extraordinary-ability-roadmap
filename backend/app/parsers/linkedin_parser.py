import pymupdf


def parse_linkedin_pdf(file_path: str) -> dict:
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return {"text": text, "type": "linkedin_pdf"}
