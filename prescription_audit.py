"""Bilingual prescription image extraction and professional review workflow."""

from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4
from typing import Any

import streamlit as st
from PIL import Image, UnidentifiedImageError

from audit_rules import audit_confirmed_details
from data_store import (
    add_prescription_audit_record,
    get_prescription_audit_records,
    update_prescription_audit_record,
)
from gemini_service import GeminiServiceError, extract_prescription_details


TEXT = {
    "English": {
        "title": "Prescription Audit",
        "intro": "Upload a prescription image for text extraction and completeness review by healthcare staff.",
        "disclaimer": "Resistal supports professional review; it does not replace clinical judgment, verify the prescription, assess treatment appropriateness, or recommend treatment.",
        "upload": "Upload prescription image (PNG, JPG, JPEG)",
        "upload_hint": "Only upload a prescription you are authorized to review. Images remain in this Streamlit session.",
        "extract": "Extract prescription details",
        "extracting": "Extracting visible details…",
        "uploaded": "Uploaded prescription",
        "unsupported": "Unsupported or unreadable image. Please upload a valid PNG or JPG/JPEG image.",
        "extract_failed": "Prescription details could not be extracted. The uploaded image is saved in this session; you can retry.",
        "timeout": "Gemini timed out. The uploaded image is saved in this session; please retry.",
        "unavailable": "Gemini is temporarily unavailable. The uploaded image is saved in this session; please retry shortly.",
        "connection_failed": "Could not connect to Gemini. The uploaded image is saved in this session; please retry.",
        "missing_key": "Gemini is not configured. The uploaded image is saved in this session; ask the administrator to configure the API.",
        "invalid_response": "Gemini returned incomplete or unreadable structured data. The uploaded image is saved; please retry.",
        "extracted": "AI-extracted details — unverified",
        "extracted_note": "These details are extracted from visible text and are not verified. Review and edit every field before confirmation.",
        "confirm_title": "Review and confirm prescription details",
        "confirm_button": "Confirm details and run completeness check",
        "confirmed": "Healthcare-professional-confirmed details",
        "confirmed_note": "These details were confirmed in this session by the healthcare professional. Confirmation does not establish clinical appropriateness.",
        "results": "Audit findings",
        "missing_information": "Missing Information",
        "needs_review": "Needs Review",
        "no_flag_identified": "No Flag Identified",
        "no_records": "No prescription has been extracted in this session yet.",
        "retry": "Retry extraction",
        "field_patient_name": "Patient name (if visible)",
        "field_prescription_date": "Prescription date (if visible)",
        "field_diagnosis_or_indication": "Diagnosis or stated indication",
        "field_antibiotic_name": "Antibiotic name",
        "field_strength_dosage": "Strength / dosage",
        "field_dose_frequency": "Dose frequency / instructions",
        "field_duration": "Treatment duration",
        "field_route": "Route of administration",
        "field_other_relevant_details": "Other relevant prescription details",
        "why": "Reason",
        "audit_scope": "This check only identifies missing or unclear antibiotic name, strength/dosage, frequency, and duration. It applies no clinical guideline or treatment rule.",
        "missing_reason": "{field} was not provided in the confirmed details.",
        "unclear_reason": "{field} remains unclear and needs professional review.",
        "no_flag_reason": "No missing or unclear required details were identified by the completeness check.",
    },
    "اردو": {
        "title": "نسخے کا جائزہ",
        "intro": "صحت کے عملے کے جائزے کے لیے نسخے کی تصویر اپ لوڈ کریں تاکہ تحریر نکالی اور معلومات کی موجودگی دیکھی جا سکے۔",
        "disclaimer": "Resistal پیشہ ورانہ جائزے میں مدد دیتا ہے؛ یہ طبی فیصلے کا متبادل نہیں، نسخے کی تصدیق یا علاج کی موزونیت کا فیصلہ نہیں کرتا اور علاج تجویز نہیں کرتا۔",
        "upload": "نسخے کی تصویر اپ لوڈ کریں (PNG، JPG، JPEG)",
        "upload_hint": "صرف وہ نسخہ اپ لوڈ کریں جس کا جائزہ لینے کی آپ کو اجازت ہو۔ تصویر اسی Streamlit سیشن میں رہے گی۔",
        "extract": "نسخے کی معلومات نکالیں",
        "extracting": "نظر آنے والی معلومات نکالی جا رہی ہیں…",
        "uploaded": "اپ لوڈ کیا گیا نسخہ",
        "unsupported": "تصویر کی قسم معاون نہیں یا تصویر پڑھی نہیں جا سکی۔ درست PNG یا JPG/JPEG اپ لوڈ کریں۔",
        "extract_failed": "نسخے کی معلومات نہیں نکالی جا سکیں۔ اپ لوڈ کی گئی تصویر اس سیشن میں محفوظ ہے؛ دوبارہ کوشش کر سکتے ہیں۔",
        "timeout": "Gemini نے مقررہ وقت میں جواب نہیں دیا۔ تصویر اس سیشن میں محفوظ ہے؛ دوبارہ کوشش کریں۔",
        "unavailable": "Gemini عارضی طور پر دستیاب نہیں۔ تصویر اس سیشن میں محفوظ ہے؛ کچھ دیر بعد دوبارہ کوشش کریں۔",
        "connection_failed": "Gemini سے رابطہ نہیں ہو سکا۔ تصویر اس سیشن میں محفوظ ہے؛ دوبارہ کوشش کریں۔",
        "missing_key": "Gemini ترتیب نہیں دیا گیا۔ تصویر اس سیشن میں محفوظ ہے؛ منتظم سے API ترتیب دینے کو کہیں۔",
        "invalid_response": "Gemini نے نامکمل یا ناقابلِ مطالعہ معلومات دیں۔ تصویر محفوظ ہے؛ دوبارہ کوشش کریں۔",
        "extracted": "اے آئی سے نکالی گئی معلومات — غیر تصدیق شدہ",
        "extracted_note": "یہ معلومات نظر آنے والی تحریر سے نکالی گئی ہیں اور تصدیق شدہ نہیں۔ تصدیق سے پہلے ہر خانے کا جائزہ لیں اور ضرورت ہو تو ترمیم کریں۔",
        "confirm_title": "نسخے کی معلومات کا جائزہ اور تصدیق",
        "confirm_button": "معلومات کی تصدیق کرکے مکمل ہونے کا جائزہ لیں",
        "confirmed": "صحت کے ماہر کی تصدیق شدہ معلومات",
        "confirmed_note": "اس سیشن میں صحت کے ماہر نے ان معلومات کی تصدیق کی۔ اس سے علاج کی موزونیت ثابت نہیں ہوتی۔",
        "results": "جائزے کے نتائج",
        "missing_information": "معلومات موجود نہیں",
        "needs_review": "جائزہ درکار ہے",
        "no_flag_identified": "کوئی نشان دہی نہیں ہوئی",
        "no_records": "اس سیشن میں ابھی کسی نسخے کی معلومات نہیں نکالی گئیں۔",
        "retry": "معلومات نکالنے کی دوبارہ کوشش کریں",
        "field_patient_name": "مریض کا نام (اگر نظر آئے)",
        "field_prescription_date": "نسخے کی تاریخ (اگر نظر آئے)",
        "field_diagnosis_or_indication": "تشخیص یا درج کردہ وجہ",
        "field_antibiotic_name": "اینٹی بایوٹک کا نام",
        "field_strength_dosage": "طاقت / خوراک",
        "field_dose_frequency": "خوراک کی تکرار / ہدایات",
        "field_duration": "استعمال کی مدت",
        "field_route": "دینے کا طریقہ",
        "field_other_relevant_details": "نسخے کی دیگر متعلقہ معلومات",
        "why": "وجہ",
        "audit_scope": "یہ جانچ صرف اینٹی بایوٹک کے نام، طاقت/خوراک، تکرار اور مدت کی غیر موجودگی یا عدم وضاحت دکھاتی ہے۔ اس میں کوئی طبی رہنما اصول یا علاج کا قاعدہ استعمال نہیں ہوتا۔",
        "missing_reason": "تصدیق شدہ معلومات میں {field} درج نہیں تھا۔",
        "unclear_reason": "{field} اب بھی واضح نہیں اور صحت کے ماہر کا جائزہ درکار ہے۔",
        "no_flag_reason": "مکمل ہونے کی جانچ میں کوئی ضروری معلومات غائب یا غیر واضح نہیں پائی گئیں۔",
    },
}

FIELDS = (
    "patient_name",
    "prescription_date",
    "diagnosis_or_indication",
    "antibiotic_name",
    "strength_dosage",
    "dose_frequency",
    "duration",
    "route",
    "other_relevant_details",
)


def _error_label(labels: dict[str, str], code: str | None) -> str:
    if code in {"timeout", "unavailable", "connection_failed", "missing_key", "invalid_response"}:
        return labels[code]
    return labels["extract_failed"]


def _image_mime_type(image_bytes: bytes) -> str:
    """Validate the actual image bytes, not only the uploaded filename or MIME hint."""
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image_format = image.format
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise ValueError("invalid image") from error
    if image_format == "PNG":
        return "image/png"
    if image_format == "JPEG":
        return "image/jpeg"
    raise ValueError("unsupported image format")


def _run_extraction(record: dict[str, Any]) -> None:
    try:
        extracted = extract_prescription_details(
            record["uploaded_prescription"]["image_bytes"],
            record["uploaded_prescription"]["mime_type"],
        )
        update_prescription_audit_record(
            st.session_state,
            record["record_id"],
            {
                "ai_extracted_details": extracted,
                "extraction_status": "ready",
                "extraction_error": None,
            },
        )
    except GeminiServiceError as error:
        update_prescription_audit_record(
            st.session_state,
            record["record_id"],
            {"extraction_status": "error", "extraction_error": error.code},
        )


def _display_details(labels: dict[str, str], details: dict[str, Any]) -> None:
    for field in FIELDS:
        st.write(f"**{labels['field_' + field]}:** {details.get(field, 'Not specified')}")


def _show_audit(labels: dict[str, str], findings: list[dict[str, str]]) -> None:
    st.markdown(f"#### {labels['results']}")
    status_labels = {
        "missing_information": labels["missing_information"],
        "needs_review": labels["needs_review"],
        "no_flag_identified": labels["no_flag_identified"],
    }
    for finding in findings:
        if finding["status"] == "no_flag_identified":
            st.success(status_labels[finding["status"]])
        elif finding["status"] == "missing_information":
            st.warning(status_labels[finding["status"]])
        else:
            st.info(status_labels[finding["status"]])
        if finding["field"]:
            field_label = labels["field_" + finding["field"]]
            reason = labels[finding["reason_key"]].format(field=field_label)
            st.write(f"{labels['why']}: {reason}")
        elif finding["status"] == "no_flag_identified":
            st.write(labels[finding["reason_key"]])
    st.caption(labels["audit_scope"])


def render_prescription_audit(language: str) -> None:
    """Render image upload, AI extraction, staff confirmation, then completeness audit."""
    labels = TEXT[language]
    st.write(labels["intro"])
    st.info(labels["disclaimer"])
    uploaded = st.file_uploader(
        labels["upload"],
        type=("png", "jpg", "jpeg"),
        help=labels["upload_hint"],
        key="prescription_upload",
    )
    valid_upload: tuple[bytes, str] | None = None
    if uploaded is not None:
        image_bytes = uploaded.getvalue()
        try:
            mime_type = _image_mime_type(image_bytes)
        except ValueError:
            st.error(labels["unsupported"])
        else:
            valid_upload = (image_bytes, mime_type)
            st.markdown(f"#### {labels['uploaded']}")
            st.image(image_bytes, caption=uploaded.name, use_container_width=True)

    if st.button(labels["extract"], type="primary", key="extract_prescription"):
        if valid_upload is None or uploaded is None:
            st.error(labels["unsupported"])
        else:
            record = {
                "record_id": uuid4().hex[:12],
                "submitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "uploaded_prescription": {
                    "filename": uploaded.name,
                    "mime_type": valid_upload[1],
                    "image_bytes": valid_upload[0],
                },
                "ai_extracted_details": None,
                "extraction_status": "pending",
                "extraction_error": None,
                "doctor_corrections": None,
                "doctor_confirmed_details": None,
                "audit_findings": None,
            }
            add_prescription_audit_record(st.session_state, record)
            with st.spinner(labels["extracting"]):
                _run_extraction(record)
            st.rerun()

    records = get_prescription_audit_records(st.session_state)
    if not records:
        st.caption(labels["no_records"])
        return

    for record in records:
        with st.container(border=True):
            preview, extracted_panel = st.columns([.85, 1.4], gap="large")
            with preview:
                st.markdown(f"#### {labels['uploaded']}")
                st.caption(record["uploaded_prescription"]["filename"])
                st.image(record["uploaded_prescription"]["image_bytes"], use_container_width=True)
            with extracted_panel:
                if record["extraction_status"] == "ready":
                    extracted = record["ai_extracted_details"]
                    st.markdown(f"#### {labels['extracted']}")
                    st.caption(labels["extracted_note"])
                    _display_details(labels, extracted)
                else:
                    st.warning(_error_label(labels, record.get("extraction_error")))
                    if st.button(labels["retry"], key=f"retry_prescription_{record['record_id']}"):
                        with st.spinner(labels["extracting"]):
                            _run_extraction(record)
                        st.rerun()
                    continue

            st.markdown(f"#### {labels['confirm_title']}")
            starting_details = record.get("doctor_confirmed_details") or extracted
            edited: dict[str, str] = {}
            field_columns = st.columns(2, gap="large")
            for index, field in enumerate(FIELDS):
                with field_columns[index % 2]:
                    widget = st.text_area if field == "other_relevant_details" else st.text_input
                    edited[field] = widget(
                        labels["field_" + field],
                        value=starting_details.get(field, "Not specified"),
                        key=f"prescription_{record['record_id']}_{field}",
                    )
            if st.button(
                labels["confirm_button"],
                key=f"confirm_prescription_{record['record_id']}",
            ):
                corrections = {
                    field: edited[field]
                    for field in FIELDS
                    if edited[field] != extracted.get(field, "Not specified")
                }
                update_prescription_audit_record(
                    st.session_state,
                    record["record_id"],
                    {
                        "doctor_corrections": corrections,
                        "doctor_confirmed_details": dict(edited),
                        "audit_findings": audit_confirmed_details(edited),
                    },
                )
                st.rerun()

            confirmed = record.get("doctor_confirmed_details")
            if confirmed is not None:
                st.markdown(f"#### {labels['confirmed']}")
                st.caption(labels["confirmed_note"])
                _display_details(labels, confirmed)
                if record.get("audit_findings"):
                    _show_audit(labels, record["audit_findings"])
