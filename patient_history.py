"""Bilingual patient antibiotic-history questionnaire and result display."""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

import streamlit as st

from data_store import (
    add_patient_history_record,
    get_patient_history_records,
    update_patient_history_record,
)
from auth_service import get_current_user
from gemini_service import GeminiServiceError, generate_patient_history_summary


def _choice_text(labels: dict[str, str], code: str) -> str:
    return labels[f"choice_{code}"]


def _choice_code(labels: dict[str, str], text: str | None, codes: tuple[str, ...]) -> str | None:
    if text is None:
        return None
    return next((code for code in codes if _choice_text(labels, code) == text), None)


def _create_responses(
    labels: dict[str, str],
    recent_use: str,
    memory: str | None,
    antibiotic_name: str,
    source: str | None,
    other_source: str,
    reason: str,
    duration: str,
    completion: str | None,
    early_reason: str,
) -> tuple[dict[str, str], dict[str, str]]:
    """Capture submitted values and their labels without editing patient text."""
    responses = {"recent_antibiotic_use": _choice_text(labels, recent_use)}
    question_labels = {"recent_antibiotic_use": labels["q_recent"]}

    if recent_use == "no":
        return responses, question_labels

    if memory == "dont_remember":
        responses["antibiotic_name"] = labels["choice_dont_remember"]
    else:
        responses["antibiotic_name"] = antibiotic_name
    responses["source_of_antibiotic"] = _choice_text(labels, source or "not_sure")
    responses["reason_for_use"] = reason
    responses["duration"] = duration
    responses["course_completion"] = _choice_text(labels, completion or "not_sure")
    responses["early_discontinuation_reason"] = (
        early_reason if completion == "stopped_early" else ""
    )
    if source == "other":
        responses["other_source_details"] = other_source

    question_labels.update({
        "antibiotic_name": labels["q_name"],
        "source_of_antibiotic": labels["q_source"],
        "reason_for_use": labels["q_reason"],
        "duration": labels["q_duration"],
        "course_completion": labels["q_completion"],
        "early_discontinuation_reason": labels["q_early_reason"],
    })
    if source == "other":
        question_labels["other_source_details"] = labels["q_other_source"]
    return responses, question_labels


def _request_summary(record: dict[str, Any]) -> None:
    """Make exactly one request for this user action, preserving data on failure."""
    try:
        summary = generate_patient_history_summary(record["responses"])
        update_patient_history_record(
            st.session_state,
            record["record_id"],
            {"summary": summary, "summary_status": "ready", "summary_error": None},
        )
    except GeminiServiceError as error:
        update_patient_history_record(
            st.session_state,
            record["record_id"],
            {"summary": None, "summary_status": "error", "summary_error": error.code},
        )


def _error_message(labels: dict[str, str], code: str | None) -> str:
    if code == "unavailable":
        return labels["summary_unavailable"]
    if code == "timeout":
        return labels["summary_timeout"]
    if code == "connection_failed":
        return labels["summary_connection_failed"]
    if code == "invalid_response":
        return labels["summary_invalid"]
    if code == "missing_key":
        return labels["summary_missing_key"]
    return labels["summary_failed"]


def _show_summary(labels: dict[str, str], summary: dict[str, Any]) -> None:
    st.markdown("#### Patient-Reported Antibiotic History")
    field_labels = (
        ("recent_antibiotic_use", "Recent antibiotic use"),
        ("antibiotic_name", "Antibiotic name"),
        ("source_of_antibiotic", "Source of antibiotic"),
        ("reason_for_use", "Reason for use"),
        ("duration", "Duration"),
        ("course_completion", "Course completion"),
        ("early_discontinuation_reason", "Early discontinuation reason"),
    )
    for key, title in field_labels:
        st.write(f"{title}: {summary[key]}")

    st.markdown("#### Important Notes for Doctor")
    notes = summary["important_notes_for_doctor"]
    if notes:
        for note in notes:
            st.markdown(f"- {note}")
    else:
        st.write("No additional notes reported.")
    st.caption(labels["summary_caveat"])


def _show_original_answers(labels: dict[str, str], record: dict[str, Any]) -> None:
    with st.expander(labels["original_answers"], expanded=False):
        for key, value in record["responses"].items():
            question = record["question_labels"].get(key, key)
            st.markdown(f"**{question}**")
            st.write(value if value else labels["not_reported"])


def _show_records(labels: dict[str, str], records: list[dict[str, Any]]) -> None:
    for index, record in enumerate(records, start=1):
        with st.container(border=True):
            st.markdown(f"#### {labels['submission']} {index}")
            st.caption(f"{labels['submitted_at']}: {record['submitted_at']}")
            if record["summary_status"] == "ready" and record["summary"]:
                _show_summary(labels, record["summary"])
            else:
                st.warning(_error_message(labels, record.get("summary_error")))
                if st.button(
                    labels["retry_summary"],
                    key=f"retry_history_{record['record_id']}",
                ):
                    with st.spinner(labels["summary_loading"]):
                        _request_summary(record)
                    st.rerun()
            _show_original_answers(labels, record)


def render_patient_history(labels: dict[str, str], language: str, user: dict[str, str] | None = None) -> None:
    """Render the history questionnaire using the app's shared language state."""
    user = user or get_current_user(st.session_state)
    if not user:
        st.error("Please sign in to access patient history." if language == "English" else "مریض کی معلومات دیکھنے کے لیے لاگ اِن کریں۔")
        return
    if user["role"] == "doctor":
        records = get_patient_history_records(st.session_state)
        st.write("Review patient-reported, unverified histories." if language == "English" else "مریض کی بتائی ہوئی غیر تصدیق شدہ سابقہ معلومات کا جائزہ لیں۔")
        if not records:
            st.info("No patient histories have been submitted in this session." if language == "English" else "اس سیشن میں مریض کی سابقہ معلومات جمع نہیں ہوئیں۔")
        else:
            _show_records(labels, records)
        return
    if user["role"] != "patient":
        st.error("This section is not available for your account role." if language == "English" else "یہ حصہ آپ کے اکاؤنٹ کے کردار کے لیے دستیاب نہیں۔")
        return
    st.write(labels["history_intro"])
    st.info(labels["ai_notice"])

    submitted = False
    recent_use: str | None = None
    memory: str | None = None
    antibiotic_name = ""
    source: str | None = None
    other_source = ""
    reason = ""
    duration = ""
    completion: str | None = None
    early_reason = ""
    validation_slots: dict[str, Any] = {}

    # Keep these as regular Streamlit widgets rather than form widgets so
    # conditional questions can rerun immediately when a selection changes.
    recent_selection = st.radio(
        labels["q_recent"],
        options=tuple(_choice_text(labels, code) for code in ("yes", "no", "not_sure")),
        index=None,
        key="history_recent_use",
    )
    recent_use = _choice_code(labels, recent_selection, ("yes", "no", "not_sure"))
    validation_slots["recent"] = st.empty()
    if recent_use in ("yes", "not_sure"):
        memory_selection = st.radio(
            labels["q_name"],
            options=(labels["choice_remember"], labels["choice_dont_remember"]),
            index=None,
            key="history_name_memory",
        )
        memory = _choice_code(labels, memory_selection, ("remember", "dont_remember"))
        validation_slots["memory"] = st.empty()
        if memory == "remember":
            antibiotic_name = st.text_input(
                labels["name_input"], key="history_antibiotic_name"
            )
            validation_slots["name"] = st.empty()

        source_selection = st.selectbox(
            labels["q_source"],
            options=tuple(
                _choice_text(labels, code)
                for code in ("doctor", "bought_without_prescription", "leftover", "someone_else", "other", "not_sure")
            ),
            index=None,
            key="history_source",
        )
        source = _choice_code(
            labels,
            source_selection,
            ("doctor", "bought_without_prescription", "leftover", "someone_else", "other", "not_sure"),
        )
        validation_slots["source"] = st.empty()
        if source == "other":
            other_source = st.text_input(
                labels["q_other_source"], key="history_other_source"
            )
            validation_slots["other_source"] = st.empty()

        reason = st.text_area(
            labels["q_reason"],
            help=labels["reason_hint"],
            key="history_reason",
        )
        duration = st.text_input(
            labels["q_duration"],
            placeholder=labels["duration_hint"],
            key="history_duration",
        )
        completion_selection = st.radio(
            labels["q_completion"],
            options=tuple(
                _choice_text(labels, code)
                for code in ("completed", "stopped_early", "still_taking", "no_instructions", "not_sure")
            ),
            index=None,
            key="history_completion",
        )
        completion = _choice_code(
            labels,
            completion_selection,
            ("completed", "stopped_early", "still_taking", "no_instructions", "not_sure"),
        )
        validation_slots["completion"] = st.empty()
        if completion == "stopped_early":
            early_reason = st.text_area(
                labels["q_early_reason"], key="history_early_reason"
            )

    st.caption(labels["required_hint"])
    submitted = st.button(labels["submit_history"], type="primary", key="submit_history")

    if submitted:
        has_errors = False
        if recent_use is None:
            validation_slots["recent"].error(labels["validation_recent"])
            has_errors = True
        elif recent_use in ("yes", "not_sure"):
            if memory is None:
                validation_slots["memory"].error(labels["validation_memory"])
                has_errors = True
            elif memory == "remember" and not antibiotic_name.strip():
                validation_slots["name"].error(labels["validation_name"])
                has_errors = True
            if source is None:
                validation_slots["source"].error(labels["validation_source"])
                has_errors = True
            elif source == "other" and not other_source.strip():
                validation_slots["other_source"].error(labels["validation_other_source"])
                has_errors = True
            if completion is None:
                validation_slots["completion"].error(labels["validation_completion"])
                has_errors = True

        if not has_errors and recent_use is not None:
            responses, question_labels = _create_responses(
                labels,
                recent_use,
                memory,
                antibiotic_name,
                source,
                other_source,
                reason,
                duration,
                completion,
                early_reason,
            )
            record = {
                "record_id": uuid4().hex[:12],
                "owner_user_id": user["user_id"],
                "submitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "ui_language": language,
                "responses": responses,
                "question_labels": question_labels,
                "summary": None,
                "summary_status": "pending",
                "summary_error": None,
            }
            add_patient_history_record(st.session_state, record)
            with st.spinner(labels["summary_loading"]):
                _request_summary(record)
            st.rerun()

    owned_records = [record for record in get_patient_history_records(st.session_state)
                     if record.get("owner_user_id") == user["user_id"]]
    _show_records(labels, owned_records)
