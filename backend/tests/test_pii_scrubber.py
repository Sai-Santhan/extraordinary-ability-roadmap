"""Tests for the PII scrubber module."""

import pytest

from app.services.pii_scrubber import (
    scrub_email_headers,
    scrub_json_strings,
    scrub_text,
)


class TestEmailRedaction:
    def test_simple_email(self):
        assert scrub_text("contact john@example.com") == "contact [EMAIL REDACTED]"

    def test_email_with_plus(self):
        assert "[EMAIL REDACTED]" in scrub_text("send to user+tag@gmail.com")

    def test_email_in_sentence(self):
        result = scrub_text("My email is priya.sharma@stanford.edu for correspondence.")
        assert "[EMAIL REDACTED]" in result
        assert "priya.sharma@stanford.edu" not in result

    def test_multiple_emails(self):
        text = "From alice@test.com to bob@test.org"
        result = scrub_text(text)
        assert result.count("[EMAIL REDACTED]") == 2

    def test_no_false_positive_on_at_sign(self):
        assert scrub_text("meeting at 3pm") == "meeting at 3pm"


class TestPhoneRedaction:
    def test_us_format_dashes(self):
        assert "[PHONE REDACTED]" in scrub_text("Call 555-123-4567")

    def test_us_format_parens(self):
        assert "[PHONE REDACTED]" in scrub_text("Phone: (555) 123-4567")

    def test_us_format_dots(self):
        assert "[PHONE REDACTED]" in scrub_text("Tel: 555.123.4567")

    def test_international_format(self):
        assert "[PHONE REDACTED]" in scrub_text("Call +1 555 123 4567")

    def test_no_false_positive_on_year(self):
        # 4-digit years should not be matched
        assert scrub_text("Published in 2024") == "Published in 2024"

    def test_no_false_positive_on_citation_count(self):
        assert scrub_text("Citations: 1234") == "Citations: 1234"


class TestSSNRedaction:
    def test_ssn_pattern(self):
        assert scrub_text("SSN: 123-45-6789") == "SSN: [ID REDACTED]"

    def test_ssn_in_text(self):
        result = scrub_text("Social security number is 987-65-4321.")
        assert "[ID REDACTED]" in result
        assert "987-65-4321" not in result


class TestDOBRedaction:
    def test_born_on_date(self):
        result = scrub_text("born on January 15, 1990")
        assert "[DOB REDACTED]" in result
        assert "January 15, 1990" not in result

    def test_dob_with_slash_date(self):
        result = scrub_text("Date of birth: 01/15/1990")
        assert "[DOB REDACTED]" in result
        assert "01/15/1990" not in result

    def test_dob_abbreviation(self):
        result = scrub_text("DOB: 03-25-1985")
        assert "[DOB REDACTED]" in result

    def test_no_false_positive_on_regular_date(self):
        # Regular dates without DOB context should be preserved
        assert scrub_text("Published on March 15, 2023") == "Published on March 15, 2023"


class TestAddressRedaction:
    def test_full_us_address(self):
        result = scrub_text("Lives at 123 Main Street, San Francisco, CA 94102")
        assert "[ADDRESS REDACTED]" in result

    def test_street_only(self):
        result = scrub_text("Office at 456 Oak Avenue")
        assert "[ADDRESS REDACTED]" in result

    def test_no_false_positive_on_org(self):
        # Organization names should not be matched
        assert "Stanford University" in scrub_text("Studied at Stanford University")


class TestPreservation:
    """Ensure non-PII content is preserved."""

    def test_person_names_preserved(self):
        text = "Dr. Priya Sharma is a researcher at Google."
        result = scrub_text(text)
        assert "Dr. Priya Sharma" in result
        assert "Google" in result

    def test_org_names_preserved(self):
        text = "Awarded by IEEE, presented at ICML 2024."
        assert scrub_text(text) == text

    def test_publication_venues_preserved(self):
        text = "Published in Nature Machine Intelligence, 2023."
        assert scrub_text(text) == text

    def test_metrics_preserved(self):
        text = "H-index: 25, Citations: 3400, GitHub stars: 1200"
        assert scrub_text(text) == text

    def test_country_preserved(self):
        text = "Country of birth: India"
        assert scrub_text(text) == text

    def test_visa_status_preserved(self):
        text = "Current visa: H-1B"
        assert scrub_text(text) == text


class TestEmailHeaders:
    def test_from_header(self):
        text = "From: John Smith <john@example.com>"
        result = scrub_email_headers(text)
        assert "john@example.com" not in result
        assert "[EMAIL REDACTED]" in result
        assert "John Smith" in result

    def test_to_header(self):
        text = "To: alice@test.com, bob@test.org"
        result = scrub_email_headers(text)
        assert result.count("[EMAIL REDACTED]") == 2

    def test_preserves_non_header_lines(self):
        text = "Subject: Meeting tomorrow\nBody of the email"
        assert scrub_email_headers(text) == text


class TestJsonScrubbing:
    def test_scrubs_nested_strings(self):
        data = {
            "name": "Priya Sharma",
            "contact": "email: priya@test.com, phone: 555-123-4567",
            "pubs": [{"title": "Paper A", "note": "contact: x@y.com"}],
        }
        result = scrub_json_strings(data)
        assert result["name"] == "Priya Sharma"  # names preserved
        assert "[EMAIL REDACTED]" in result["contact"]
        assert "[PHONE REDACTED]" in result["contact"]
        assert "[EMAIL REDACTED]" in result["pubs"][0]["note"]

    def test_preserves_non_strings(self):
        data = {"count": 42, "active": True, "items": [1, 2, 3]}
        assert scrub_json_strings(data) == data


class TestEdgeCases:
    def test_empty_string(self):
        assert scrub_text("") == ""

    def test_none_input(self):
        assert scrub_text(None) is None

    def test_no_pii(self):
        text = "This is a clean text with no PII."
        assert scrub_text(text) == text

    def test_mixed_pii(self):
        text = (
            "Dr. Priya Sharma\n"
            "Email: priya@stanford.edu\n"
            "Phone: (650) 555-1234\n"
            "SSN: 123-45-6789\n"
            "Born on March 15, 1985\n"
            "123 University Avenue, Palo Alto, CA 94301\n"
            "Researcher at Stanford University\n"
            "Published in Nature, 2024"
        )
        result = scrub_text(text)
        # PII redacted
        assert "priya@stanford.edu" not in result
        assert "(650) 555-1234" not in result
        assert "123-45-6789" not in result
        assert "March 15, 1985" not in result
        # Non-PII preserved
        assert "Dr. Priya Sharma" in result
        assert "Stanford University" in result
        assert "Nature" in result
