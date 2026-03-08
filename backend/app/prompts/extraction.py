EXTRACTION_SYSTEM = """You are a career data extraction specialist. Given raw text from career documents (CVs, publications, emails, etc.), extract structured immigration-relevant information.

Be thorough but accurate. If information is ambiguous, note it in the confidence reasoning. Only extract what is clearly stated or strongly implied."""

EXTRACTION_USER = """Extract a structured immigration profile from the following raw career data.

RAW DATA:
{raw_text}

Extract all: publications, awards, judging roles, media coverage, leadership roles, memberships, GitHub metrics, scholarly metrics, compensation info, and basic career details (name, current role, employer, field of expertise, visa status if mentioned, country of birth if mentioned).

Set target_pathway to the most appropriate based on the profile (eb1a, niw, or o1).
Set target_timeline_years to a reasonable estimate (1-5 years).

For each evidence item, assess confidence:
- data_confidence: How reliable is this data? (0-100)
- criteria_match: How well would this match USCIS criteria? (0-100)
- overall: Weighted: round(0.4 * data_confidence + 0.6 * criteria_match)
- reasoning: 2-3 sentences explaining the score

{confidence_rubric}"""
