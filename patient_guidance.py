"""Bilingual patient-facing wording for professionally confirmed prescriptions."""

from datetime import datetime, timezone
from html import escape
from typing import Any

import streamlit as st

from data_store import get_prescription_audit_records, update_prescription_audit_record
from auth_service import get_current_user
from gemini_service import (
    GeminiServiceError,
    PATIENT_GUIDANCE_FIELDS,
    generate_patient_guidance,
    prepare_confirmed_guidance_source,
)


TEXT = {
    "English": {
        "title": "Patient Guidance",
        "intro": "Prepare a plain-language explanation from prescription details confirmed by a healthcare professional.",
        "safety_notice": "This guidance only restates confirmed prescription information. It does not change a prescription or replace advice from your healthcare professional.",
        "select_record": "Select a confirmed prescription",
        "no_records": "There are no professionally confirmed prescriptions available. Confirm a prescription in Prescription Audit first.",
        "preview": "Confirmed prescription details used",
        "language": "Language for patient guidance",
        "generate": "Generate patient guidance",
        "regenerate": "Regenerate patient guidance",
        "retry": "Retry patient guidance",
        "generating": "Preparing patient guidance…",
        "output": "Guidance based on confirmed information",
        "general_reminders": "General reminders",
        "reminder_follow": "Follow the directions confirmed by your healthcare professional.",
        "reminder_contact": "Contact your healthcare professional if you have questions or concerns.",
        "missing_details": "Details to confirm with your healthcare professional",
        "not_provided": "Not provided",
        "unclear": "Unclear",
        "confirm_missing": "This detail was not provided. Please confirm it with your healthcare professional before relying on it.",
        "confirm_unclear": "This detail is unclear. Please confirm it with your healthcare professional before relying on it.",
        "failed": "Patient guidance could not be generated. Your confirmed prescription remains saved; please retry.",
        "role_denied": "Sign in to view guidance. Only doctors can generate or change it.",
        "no_patient_guidance": "No guidance has been prepared for your linked prescriptions yet. Please contact your healthcare professional.",
        "read_only": "This guidance was prepared from details confirmed by a healthcare professional.",
        "timeout": "Gemini timed out. Your confirmed prescription remains saved; please retry.",
        "unavailable": "Gemini is temporarily unavailable. Your confirmed prescription remains saved; please retry shortly.",
        "connection_failed": "Could not connect to Gemini. Your confirmed prescription remains saved; please retry.",
        "missing_key": "Gemini is not configured. Your confirmed prescription remains saved; ask the administrator to configure the API.",
        "invalid_response": "Gemini returned guidance that could not be safely validated. Your confirmed prescription remains saved; please retry.",
        "disclaimer": "AI wording is based only on confirmed prescription details. If any detail is missing or unclear, confirm it with the healthcare professional. Do not use this text to change treatment.",
        "field_medicine_name": "Medicine name",
        "field_strength_and_dose": "Strength and prescribed dose",
        "field_frequency": "Frequency",
        "field_duration": "Prescribed duration",
        "field_route": "Route",
        "field_timing_special_instructions": "Confirmed timing or special instructions (if any)",
        "preview_timing_special_instructions": "Confirmed timing or other prescription notes (used only if they are explicit instructions)",
        "record_option": "Prescription · {date} · {medicine}",
    },
    "اردو": {
        "title": "مریض کے لیے رہنمائی",
        "intro": "صحت کے ماہر کی تصدیق شدہ نسخے کی معلومات کو آسان زبان میں بیان کریں۔",
        "safety_notice": "یہ رہنمائی صرف تصدیق شدہ نسخے کی معلومات کو آسان انداز میں بیان کرتی ہے۔ یہ نسخہ تبدیل نہیں کرتی اور صحت کے ماہر کے مشورے کا متبادل نہیں۔",
        "select_record": "تصدیق شدہ نسخہ منتخب کریں",
        "no_records": "صحت کے ماہر کی تصدیق شدہ کوئی معلومات موجود نہیں۔ پہلے نسخے کے جائزے میں نسخے کی تصدیق کریں۔",
        "preview": "استعمال ہونے والی تصدیق شدہ نسخے کی معلومات",
        "language": "مریض کے لیے رہنمائی کی زبان",
        "generate": "مریض کے لیے رہنمائی تیار کریں",
        "regenerate": "مریض کے لیے رہنمائی دوبارہ تیار کریں",
        "retry": "رہنمائی کے لیے دوبارہ کوشش کریں",
        "generating": "مریض کے لیے رہنمائی تیار کی جا رہی ہے…",
        "output": "تصدیق شدہ معلومات پر مبنی رہنمائی",
        "general_reminders": "عمومی یاد دہانیاں",
        "reminder_follow": "اپنے صحت کے ماہر کی تصدیق شدہ ہدایات پر عمل کریں۔",
        "reminder_contact": "اگر کوئی سوال یا تشویش ہو تو اپنے صحت کے ماہر سے رابطہ کریں۔",
        "missing_details": "وہ معلومات جن کی صحت کے ماہر سے تصدیق ضروری ہے",
        "not_provided": "درج نہیں کی گئی",
        "unclear": "واضح نہیں",
        "confirm_missing": "یہ معلومات فراہم نہیں کی گئی۔ اس پر عمل کرنے سے پہلے اپنے صحت کے ماہر سے تصدیق کریں۔",
        "confirm_unclear": "یہ معلومات واضح نہیں۔ اس پر عمل کرنے سے پہلے اپنے صحت کے ماہر سے تصدیق کریں۔",
        "failed": "مریض کے لیے رہنمائی تیار نہیں ہو سکی۔ تصدیق شدہ نسخہ محفوظ ہے؛ دوبارہ کوشش کریں۔",
        "role_denied": "رہنمائی دیکھنے کے لیے لاگ اِن کریں۔ صرف ڈاکٹر اسے تیار یا تبدیل کر سکتے ہیں۔",
        "no_patient_guidance": "آپ کے منسلک نسخوں کے لیے ابھی رہنمائی تیار نہیں ہوئی۔ اپنے صحت کے ماہر سے رابطہ کریں۔",
        "read_only": "یہ رہنمائی صحت کے ماہر کی تصدیق شدہ معلومات سے تیار کی گئی ہے۔",
        "timeout": "Gemini نے مقررہ وقت میں جواب نہیں دیا۔ تصدیق شدہ نسخہ محفوظ ہے؛ دوبارہ کوشش کریں۔",
        "unavailable": "Gemini عارضی طور پر دستیاب نہیں۔ تصدیق شدہ نسخہ محفوظ ہے؛ کچھ دیر بعد دوبارہ کوشش کریں۔",
        "connection_failed": "Gemini سے رابطہ نہیں ہو سکا۔ تصدیق شدہ نسخہ محفوظ ہے؛ دوبارہ کوشش کریں۔",
        "missing_key": "Gemini ترتیب نہیں دیا گیا۔ تصدیق شدہ نسخہ محفوظ ہے؛ منتظم سے API ترتیب دینے کو کہیں۔",
        "invalid_response": "Gemini کی رہنمائی کی محفوظ طریقے سے تصدیق نہیں ہو سکی۔ نسخہ محفوظ ہے؛ دوبارہ کوشش کریں۔",
        "disclaimer": "اے آئی کی عبارت صرف تصدیق شدہ نسخے کی معلومات پر مبنی ہے۔ اگر کوئی بات غائب یا غیر واضح ہو تو صحت کے ماہر سے تصدیق کریں۔ اس عبارت کی بنیاد پر علاج تبدیل نہ کریں۔",
        "field_medicine_name": "دوا کا نام",
        "field_strength_and_dose": "طاقت اور تجویز کردہ خوراک",
        "field_frequency": "استعمال کی تکرار",
        "field_duration": "تجویز کردہ مدت",
        "field_route": "دینے کا طریقہ",
        "field_timing_special_instructions": "تصدیق شدہ وقت یا خصوصی ہدایات (اگر موجود ہوں)",
        "preview_timing_special_instructions": "تصدیق شدہ وقت یا نسخے کی دیگر معلومات (صرف واضح ہدایات استعمال ہوں گی)",
        "record_option": "نسخہ · {date} · {medicine}",
    },
}


def _error_text(labels: dict[str, str], code: str | None) -> str:
    if code in {
        "timeout",
        "unavailable",
        "connection_failed",
        "missing_key",
        "invalid_response",
    }:
        return labels[code]
    return labels["failed"]


def _record_label(record: dict[str, Any], labels: dict[str, str]) -> str:
    confirmed = record["doctor_confirmed_details"]
    medicine = str(confirmed.get("antibiotic_name") or labels["not_provided"])
    return labels["record_option"].format(
        date=record.get("submitted_at", ""), medicine=medicine
    )


def _request_guidance(record: dict[str, Any], language: str) -> None:
    """Generate or retry guidance on an existing confirmed prescription record."""
    try:
        guidance = generate_patient_guidance(
            record["doctor_confirmed_details"], language
        )
        result = {
            "status": "ready",
            "content": guidance,
            "error": None,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    except GeminiServiceError as error:
        result = {
            "status": "error",
            "content": None,
            "error": error.code,
            "generated_at": None,
        }

    by_language = dict(record.get("patient_guidance") or {})
    by_language[language] = result
    update_prescription_audit_record(
        st.session_state,
        record["record_id"],
        {"patient_guidance": by_language},
    )


def _show_confirmed_preview(
    labels: dict[str, str], confirmed_details: dict[str, Any]
) -> dict[str, str]:
    source = prepare_confirmed_guidance_source(confirmed_details)
    with st.container(border=True):
        st.markdown(f"#### {labels['preview']}")
        for field in PATIENT_GUIDANCE_FIELDS:
            value = source[field]
            if value == "NOT_PROVIDED":
                shown = labels["not_provided"]
            elif value == "UNCLEAR":
                shown = labels["unclear"]
            else:
                shown = value
            label_key = (
                "preview_timing_special_instructions"
                if field == "timing_special_instructions"
                else "field_" + field
            )
            st.write(f"**{labels[label_key]}:** {shown}")
    return source


def _show_guidance(
    labels: dict[str, str],
    source: dict[str, str],
    content: dict[str, str],
    language: str,
) -> None:
    lines: list[tuple[str, str]] = []
    missing: list[tuple[str, str]] = []
    for field in PATIENT_GUIDANCE_FIELDS:
        source_value = source[field]
        content_value = content[field]
        if source_value == "NOT_PROVIDED" or content_value == "NOT_PROVIDED":
            shown = labels["not_provided"]
            missing.append((field, labels["confirm_missing"]))
        elif source_value == "UNCLEAR" or content_value == "UNCLEAR":
            shown = labels["unclear"]
            missing.append((field, labels["confirm_unclear"]))
        else:
            shown = content_value
        lines.append((labels["field_" + field], shown))

    direction = "rtl" if language == "اردو" else "ltr"
    alignment = "right" if language == "اردو" else "left"
    html = [
        f'<div dir="{direction}" style="direction:{direction};text-align:{alignment}">',
        f"<h4>{escape(labels['output'])}</h4>",
    ]
    html.extend(
        f"<p><strong>{escape(label)}:</strong> {escape(value)}</p>"
        for label, value in lines
    )
    if missing:
        html.append(f"<h5>{escape(labels['missing_details'])}</h5><ul>")
        html.extend(
            f"<li><strong>{escape(labels['field_' + field])}:</strong> {escape(advice)}</li>"
            for field, advice in missing
        )
        html.append("</ul>")
    html.extend(
        (
            f"<h5>{escape(labels['general_reminders'])}</h5>",
            f"<ul><li>{escape(labels['reminder_follow'])}</li>",
            f"<li>{escape(labels['reminder_contact'])}</li></ul>",
            f"<p><small>{escape(labels['disclaimer'])}</small></p>",
            "</div>",
        )
    )
    st.markdown("\n".join(html), unsafe_allow_html=True)


def render_patient_guidance(interface_language: str) -> None:
    """Render guidance controls for existing, professionally confirmed records only."""
    labels = TEXT[interface_language]
    user = get_current_user(st.session_state)
    if not user:
        st.error(labels["role_denied"])
        return
    st.write(labels["intro"])
    st.info(labels["safety_notice"])

    records = [
        record
        for record in get_prescription_audit_records(st.session_state)
        if isinstance(record.get("doctor_confirmed_details"), dict)
    ]
    if user["role"] == "patient":
        records = [record for record in records
                   if record.get("owner_user_id") == user["user_id"]
                   and any((item or {}).get("status") == "ready"
                           for item in (record.get("patient_guidance") or {}).values())]
        if not records:
            st.info(labels["no_patient_guidance"])
            return
        st.caption(labels["read_only"])
        record_ids = [item["record_id"] for item in records]
        selected_id = st.selectbox(
            labels["select_record"], options=record_ids,
            format_func=lambda record_id: _record_label(
                next(item for item in records if item["record_id"] == record_id), labels
            ), key="patient_guidance_owned_record_id",
        )
        record = next(item for item in records if item["record_id"] == selected_id)
        by_language = record.get("patient_guidance") or {}
        selected_language = st.selectbox(
            labels["language"], options=("English", "اردو"),
            index=0 if interface_language == "English" else 1,
            key="patient_guidance_patient_language",
        )
        current = by_language.get(selected_language, {})
        if current.get("status") != "ready":
            st.info(labels["no_patient_guidance"])
            return
        source = _show_confirmed_preview(labels, record["doctor_confirmed_details"])
        _show_guidance(TEXT[selected_language], source, current["content"], selected_language)
        return
    if user["role"] != "doctor":
        st.error(labels["role_denied"])
        return
    if not records:
        st.warning(labels["no_records"])
        return

    record_options = [record["record_id"] for record in records]
    selected_record_id = st.selectbox(
        labels["select_record"],
        options=record_options,
        format_func=lambda record_id: _record_label(
            next(record for record in records if record["record_id"] == record_id),
            labels,
        ),
        key="patient_guidance_record_id",
    )
    record = next(
        item for item in records if item["record_id"] == selected_record_id
    )
    source = _show_confirmed_preview(labels, record["doctor_confirmed_details"])

    default_language = "اردو" if interface_language == "اردو" else "English"
    selected_language = st.selectbox(
        labels["language"],
        options=("English", "اردو"),
        index=(0 if default_language == "English" else 1),
        key="patient_guidance_language",
    )
    previous = (record.get("patient_guidance") or {}).get(selected_language, {})
    if previous.get("status") == "error":
        st.warning(_error_text(labels, previous.get("error")))
        action_label = labels["retry"]
    elif previous.get("status") == "ready":
        action_label = labels["regenerate"]
    else:
        action_label = labels["generate"]

    if st.button(action_label, type="primary", key="generate_patient_guidance"):
        with st.spinner(labels["generating"]):
            _request_guidance(record, selected_language)
        st.rerun()

    current = (record.get("patient_guidance") or {}).get(selected_language, {})
    if current.get("status") == "ready" and isinstance(current.get("content"), dict):
        _show_guidance(TEXT[selected_language], source, current["content"], selected_language)
