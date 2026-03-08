import pymupdf


def parse_pdf(file_path: str) -> dict:
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    page_count = len(doc)
    doc.close()
    return {"text": text, "pages": page_count, "type": "pdf"}
