from app.models.schemas import EvidenceSource, RawCareerData, RawSourceData
from app.parsers.router import route_parser


class IngestionAgent:
    """No LLM call - parses files and assembles raw career data."""

    async def run(self, evidence_files: list[dict]) -> RawCareerData:
        sources = []
        notes = []

        for ef in evidence_files:
            try:
                parsed = route_parser(ef["file_type"], ef["source_type"], ef["file_path"])
                text = parsed.get("text", str(parsed))
                sources.append(RawSourceData(
                    source=EvidenceSource(ef["source_type"]),
                    raw_text=text[:30000],
                    file_name=ef["filename"],
                    metadata={k: v for k, v in parsed.items() if k != "text" and not isinstance(v, (list, dict)) or k in ("count", "pages")},
                ))
            except Exception as e:
                notes.append(f"Failed to parse {ef['filename']}: {str(e)}")

        return RawCareerData(
            sources=sources,
            total_files_processed=len(evidence_files),
            extraction_notes=notes,
        )
