"""Completeness-only prescription checks; no clinical appropriateness rules are active."""

from collections.abc import Mapping
from typing import Any


REQUIRED_REVIEW_FIELDS = {
    "antibiotic_name": "Antibiotic name",
    "strength_dosage": "Strength / dosage",
    "dose_frequency": "Dose frequency",
    "duration": "Treatment duration",
}

UNKNOWN_VALUES = {"", "not specified", "unknown", "none", "n/a"}


def audit_confirmed_details(details: Mapping[str, Any]) -> list[dict[str, str]]:
    """Flag absent or unclear required details without assessing treatment choices."""
    findings: list[dict[str, str]] = []
    for field in REQUIRED_REVIEW_FIELDS:
        value = str(details.get(field, "")).strip()
        normalized = value.casefold()
        if normalized in UNKNOWN_VALUES:
            findings.append({
                "status": "missing_information",
                "field": field,
                "reason_key": "missing_reason",
            })
        elif normalized in {"unclear", "illegible", "unreadable"}:
            findings.append({
                "status": "needs_review",
                "field": field,
                "reason_key": "unclear_reason",
            })

    if not findings:
        findings.append({
            "status": "no_flag_identified",
            "field": "",
            "reason_key": "no_flag_reason",
        })
    return findings
