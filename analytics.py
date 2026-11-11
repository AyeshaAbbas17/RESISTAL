"""Bilingual, session-scoped aggregate analytics for reported use and audit completeness."""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from data_store import get_patient_history_records, get_prescription_audit_records


MIN_RECORDS_PER_MONTH = 5
MIN_TREND_MONTHS = 2

TEXT = {
    "English": {
        "title": "Institutional Analytics",
        "scope": "This view summarizes records stored in the current Streamlit session only. It shows reported antibiotic use and prescription completeness; it does not measure antimicrobial resistance or assess clinical appropriateness.",
        "no_records": "There are no Patient History or Prescription Audit records in this session yet. Statistics below are zero because no records are available.",
        "patient_section": "Patient-reported antibiotic history",
        "patient_scope": "The following counts come from patient-reported, unverified answers. They are not confirmed medication histories.",
        "no_history": "No Patient History submissions are available in this session.",
        "history_total": "Patient History submissions",
        "self_medication": "Reported non-prescribed use",
        "self_medication_help": "Bought without a prescription or used leftover antibiotics; patient-reported and unverified.",
        "leftover_use": "Reported leftover use",
        "early_stop": "Reported early discontinuation",
        "audit_section": "Prescription information completeness",
        "audit_scope": "Prescription flags are counted only from records with healthcare-professional-confirmed details. These flags concern missing or unclear information, not whether treatment is appropriate.",
        "no_audits": "No Prescription Audit records are available in this session.",
        "audit_total": "Prescription audit records",
        "audit_confirmed": "Records with confirmed details",
        "missing_flags": "Missing-information flags",
        "missing_records": "Records with missing information",
        "review_flags": "Details requiring review",
        "review_records": "Records with details requiring review",
        "trends": "Monthly patterns",
        "history_trend": "Patient-reported use over time",
        "audit_trend": "Confirmed prescription completeness flags over time",
        "trend_history_submissions": "History submissions",
        "trend_nonprescribed": "Reported non-prescribed use",
        "trend_leftover": "Reported leftover use",
        "trend_missing": "Missing-information flags",
        "trend_review": "Details requiring review",
        "history_trend_empty": "A patient-history trend is hidden until there are at least 5 dated records in each of at least 2 months. Summary metrics above still include all valid session records.",
        "audit_trend_empty": "A prescription trend is hidden until there are at least 5 confirmed, dated audits in each of at least 2 months. Summary metrics above still include all valid session records.",
        "trend_note": "Charts use monthly aggregates from records with valid submission timestamps. No names, record IDs, or individual answers are displayed.",
    },
    "اردو": {
        "title": "ادارہ جاتی اعداد و شمار",
        "scope": "یہ صفحہ صرف موجودہ Streamlit سیشن میں محفوظ ریکارڈز کا خلاصہ دکھاتا ہے۔ اس میں مریض کے بتائے ہوئے اینٹی بایوٹک استعمال اور نسخے کی معلومات کی تکمیل شامل ہے؛ یہ اینٹی مائیکروبیل مزاحمت یا علاج کی موزونیت نہیں ناپتا۔",
        "no_records": "اس سیشن میں مریض کی سابقہ معلومات یا نسخے کے جائزے کا کوئی ریکارڈ موجود نہیں۔ نیچے کے اعداد صفر ہیں کیونکہ کوئی ریکارڈ دستیاب نہیں۔",
        "patient_section": "مریض کی بتائی ہوئی اینٹی بایوٹک معلومات",
        "patient_scope": "یہ تعداد مریض کے بتائے ہوئے غیر تصدیق شدہ جوابات سے لی گئی ہے۔ یہ تصدیق شدہ ادویات کی تاریخ نہیں۔",
        "no_history": "اس سیشن میں مریض کی سابقہ معلومات کی کوئی جمع کرائی گئی تفصیل موجود نہیں۔",
        "history_total": "مریض کی جمع کرائی گئی معلومات",
        "self_medication": "بغیر نسخے کے استعمال کی اطلاع",
        "self_medication_help": "بغیر نسخے خریدی گئی یا بچی ہوئی اینٹی بایوٹک؛ مریض کی بتائی ہوئی غیر تصدیق شدہ معلومات۔",
        "leftover_use": "بچی ہوئی دوا کے استعمال کی اطلاع",
        "early_stop": "جلد استعمال چھوڑنے کی اطلاع",
        "audit_section": "نسخے کی معلومات کی تکمیل",
        "audit_scope": "نسخے کے نشانات صرف ان ریکارڈز سے شمار ہوتے ہیں جن کی صحت کے ماہر نے تصدیق کی ہو۔ یہ نشان دہی غائب یا غیر واضح معلومات کی ہے، علاج کی موزونیت کی نہیں۔",
        "no_audits": "اس سیشن میں نسخے کے جائزے کا کوئی ریکارڈ موجود نہیں۔",
        "audit_total": "نسخے کے جائزے کے ریکارڈز",
        "audit_confirmed": "تصدیق شدہ معلومات والے ریکارڈز",
        "missing_flags": "غائب معلومات کی نشان دہی",
        "missing_records": "غائب معلومات والے ریکارڈز",
        "review_flags": "جائزے کے لیے مطلوب تفصیلات",
        "review_records": "جائزے کے لیے مطلوب تفصیلات والے ریکارڈز",
        "trends": "ماہانہ رجحانات",
        "history_trend": "مریض کے بتائے ہوئے استعمال کا رجحان",
        "audit_trend": "تصدیق شدہ نسخوں میں معلومات کی کمی کے رجحانات",
        "trend_history_submissions": "جمع کرائی گئی معلومات",
        "trend_nonprescribed": "بغیر نسخے کے استعمال کی اطلاع",
        "trend_leftover": "بچی ہوئی دوا کے استعمال کی اطلاع",
        "trend_missing": "غائب معلومات کی نشان دہی",
        "trend_review": "جائزے کے لیے مطلوب تفصیلات",
        "history_trend_empty": "مریض کی تاریخ کا رجحان تب دکھایا جائے گا جب کم از کم 2 مہینوں میں ہر مہینے کی کم از کم 5 تاریخ والی معلومات موجود ہوں۔ اوپر کے خلاصہ اعداد تمام درست سیشن ریکارڈز شامل کرتے ہیں۔",
        "audit_trend_empty": "نسخے کا رجحان تب دکھایا جائے گا جب کم از کم 2 مہینوں میں ہر مہینے کے کم از کم 5 تاریخ والے تصدیق شدہ جائزے موجود ہوں۔ اوپر کے خلاصہ اعداد تمام درست سیشن ریکارڈز شامل کرتے ہیں۔",
        "trend_note": "چارٹس صرف درست جمع کرانے کے وقت والے ریکارڈز کے ماہانہ مجموعے دکھاتے ہیں۔ نام، ریکارڈ شناختی نمبر یا انفرادی جوابات نہیں دکھائے جاتے۔",
    },
}

_NONPRESCRIBED_SOURCES = {
    "bought without a prescription",
    "بغیر نسخے کے خریدی",
    "used leftover antibiotics",
    "پہلے سے بچی ہوئی اینٹی بایوٹک استعمال کی",
}
_LEFTOVER_SOURCES = {
    "used leftover antibiotics",
    "پہلے سے بچی ہوئی اینٹی بایوٹک استعمال کی",
}
_EARLY_STOP_CHOICES = {
    "stopped earlier than instructed",
    "ہدایت سے پہلے چھوڑ دی",
}


def _normalized_answer(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).casefold().split())


def unique_records(records: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Keep valid identified records once, without returning their IDs to the UI."""
    unique: list[Mapping[str, Any]] = []
    seen_ids: set[str] = set()
    for record in records:
        if not isinstance(record, Mapping):
            continue
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id.strip():
            continue
        if record_id in seen_ids:
            continue
        seen_ids.add(record_id)
        unique.append(record)
    return unique


def _finding_counts(record: Mapping[str, Any]) -> tuple[int, int]:
    """Count unique missing/review fields once within an audit record."""
    if not isinstance(record.get("doctor_confirmed_details"), Mapping):
        return 0, 0
    findings = record.get("audit_findings")
    if not isinstance(findings, list):
        return 0, 0
    seen: set[tuple[str, str]] = set()
    for finding in findings:
        if not isinstance(finding, Mapping):
            continue
        status = finding.get("status")
        if status not in ("missing_information", "needs_review"):
            continue
        field = finding.get("field")
        if not isinstance(field, str) or not field:
            continue
        seen.add((status, field))
    return (
        sum(status == "missing_information" for status, _ in seen),
        sum(status == "needs_review" for status, _ in seen),
    )


def aggregate_metrics(
    patient_records: Iterable[Mapping[str, Any]],
    prescription_records: Iterable[Mapping[str, Any]],
) -> dict[str, int]:
    """Aggregate distinct session records, separating reports from confirmed audits."""
    histories = unique_records(patient_records)
    audits = unique_records(prescription_records)
    nonprescribed = 0
    leftover = 0
    early_stop = 0
    for record in histories:
        responses = record.get("responses")
        if not isinstance(responses, Mapping):
            continue
        source = _normalized_answer(responses.get("source_of_antibiotic"))
        completion = _normalized_answer(responses.get("course_completion"))
        nonprescribed += int(source in _NONPRESCRIBED_SOURCES)
        leftover += int(source in _LEFTOVER_SOURCES)
        early_stop += int(completion in _EARLY_STOP_CHOICES)

    confirmed_audits = [
        record
        for record in audits
        if isinstance(record.get("doctor_confirmed_details"), Mapping)
    ]
    missing_flags = review_flags = missing_records = review_records = 0
    for record in confirmed_audits:
        missing, review = _finding_counts(record)
        missing_flags += missing
        review_flags += review
        missing_records += int(missing > 0)
        review_records += int(review > 0)

    return {
        "history_submissions": len(histories),
        "reported_nonprescribed_use": nonprescribed,
        "reported_leftover_use": leftover,
        "reported_early_discontinuation": early_stop,
        "prescription_audit_records": len(audits),
        "confirmed_prescription_records": len(confirmed_audits),
        "missing_information_flags": missing_flags,
        "records_with_missing_information": missing_records,
        "details_requiring_review": review_flags,
        "records_requiring_review": review_records,
    }


def _record_month(record: Mapping[str, Any]) -> str | None:
    value = record.get("submitted_at")
    try:
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str) and value.strip():
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        else:
            return None
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed.strftime("%Y-%m")


def monthly_history_counts(
    patient_records: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    """Return monthly patient-report counts using valid submission timestamps only."""
    months: dict[str, dict[str, int]] = defaultdict(
        lambda: {"records": 0, "nonprescribed": 0, "leftover": 0}
    )
    for record in unique_records(patient_records):
        month = _record_month(record)
        if month is None:
            continue
        counts = months[month]
        counts["records"] += 1
        responses = record.get("responses")
        if not isinstance(responses, Mapping):
            continue
        source = _normalized_answer(responses.get("source_of_antibiotic"))
        counts["nonprescribed"] += int(source in _NONPRESCRIBED_SOURCES)
        counts["leftover"] += int(source in _LEFTOVER_SOURCES)
    return dict(sorted(months.items()))


def monthly_audit_counts(
    prescription_records: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    """Return monthly counts for confirmed audits and their unique completeness findings."""
    months: dict[str, dict[str, int]] = defaultdict(
        lambda: {"records": 0, "missing": 0, "review": 0}
    )
    for record in unique_records(prescription_records):
        if not isinstance(record.get("doctor_confirmed_details"), Mapping):
            continue
        month = _record_month(record)
        if month is None:
            continue
        counts = months[month]
        counts["records"] += 1
        missing, review = _finding_counts(record)
        counts["missing"] += missing
        counts["review"] += review
    return dict(sorted(months.items()))


def _trend_has_enough_data(months: Mapping[str, Mapping[str, int]]) -> bool:
    return (
        len(months) >= MIN_TREND_MONTHS
        and all(counts["records"] >= MIN_RECORDS_PER_MONTH for counts in months.values())
    )


def _render_history_chart(
    labels: dict[str, str], monthly: Mapping[str, Mapping[str, int]]
) -> None:
    st.markdown(f"#### {labels['history_trend']}")
    if not _trend_has_enough_data(monthly):
        st.info(labels["history_trend_empty"])
        return
    frame = pd.DataFrame.from_dict(monthly, orient="index").rename(
        columns={
            "records": labels["trend_history_submissions"],
            "nonprescribed": labels["trend_nonprescribed"],
            "leftover": labels["trend_leftover"],
        }
    )
    st.line_chart(frame.sort_index())


def _render_audit_chart(
    labels: dict[str, str], monthly: Mapping[str, Mapping[str, int]]
) -> None:
    st.markdown(f"#### {labels['audit_trend']}")
    if not _trend_has_enough_data(monthly):
        st.info(labels["audit_trend_empty"])
        return
    frame = pd.DataFrame.from_dict(monthly, orient="index").rename(
        columns={
            "missing": labels["trend_missing"],
            "review": labels["trend_review"],
        }
    )
    st.line_chart(frame.sort_index())


def render_analytics(language: str) -> None:
    """Render session-only aggregate metrics and privacy-thresholded monthly charts."""
    labels = TEXT[language]
    patient_records = unique_records(get_patient_history_records(st.session_state))
    prescription_records = unique_records(
        get_prescription_audit_records(st.session_state)
    )
    metrics = aggregate_metrics(patient_records, prescription_records)

    st.markdown(f"### {labels['title']}")
    st.info(labels["scope"])
    if not patient_records and not prescription_records:
        st.info(labels["no_records"])

    st.markdown(f"#### {labels['patient_section']}")
    st.caption(labels["patient_scope"])
    if not patient_records:
        st.caption(labels["no_history"])
    history_columns = st.columns(4)
    history_metrics = (
        ("history_total", "history_submissions"),
        ("self_medication", "reported_nonprescribed_use"),
        ("leftover_use", "reported_leftover_use"),
        ("early_stop", "reported_early_discontinuation"),
    )
    for column, (label_key, metric_key) in zip(history_columns, history_metrics):
        with column:
            help_text = labels["self_medication_help"] if metric_key == "reported_nonprescribed_use" else None
            st.metric(labels[label_key], metrics[metric_key], help=help_text)

    st.markdown(f"#### {labels['audit_section']}")
    st.caption(labels["audit_scope"])
    if not prescription_records:
        st.caption(labels["no_audits"])
    audit_metrics = (
        ("audit_total", "prescription_audit_records"),
        ("audit_confirmed", "confirmed_prescription_records"),
        ("missing_flags", "missing_information_flags"),
        ("missing_records", "records_with_missing_information"),
        ("review_flags", "details_requiring_review"),
        ("review_records", "records_requiring_review"),
    )
    for start in range(0, len(audit_metrics), 3):
        columns = st.columns(3)
        for column, (label_key, metric_key) in zip(
            columns, audit_metrics[start : start + 3]
        ):
            with column:
                st.metric(labels[label_key], metrics[metric_key])

    st.markdown(f"#### {labels['trends']}")
    st.caption(labels["trend_note"])
    _render_history_chart(labels, monthly_history_counts(patient_records))
    _render_audit_chart(labels, monthly_audit_counts(prescription_records))
