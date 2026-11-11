"""Small session-state storage helpers for prototype records."""

from typing import Any, MutableMapping


def add_patient_history_record(state: MutableMapping[str, Any], record: dict[str, Any]) -> None:
    """Append a submitted history record to the current Streamlit session."""
    records = list(state.get("patient_history_records", []))
    records.append(record)
    state["patient_history_records"] = records


def get_patient_history_records(state: MutableMapping[str, Any]) -> list[dict[str, Any]]:
    """Return session records newest first without changing their contents."""
    return list(reversed(state.get("patient_history_records", [])))


def update_patient_history_record(
    state: MutableMapping[str, Any], record_id: str, updates: dict[str, Any]
) -> dict[str, Any] | None:
    """Update one saved record by ID, preserving its original patient responses."""
    records = list(state.get("patient_history_records", []))
    for index, record in enumerate(records):
        if record.get("record_id") == record_id:
            updated = {**record, **updates}
            records[index] = updated
            state["patient_history_records"] = records
            return updated
    return None


def add_prescription_audit_record(
    state: MutableMapping[str, Any], record: dict[str, Any]
) -> None:
    """Append a prescription audit record to the current Streamlit session."""
    records = list(state.get("prescription_audit_records", []))
    records.append(record)
    state["prescription_audit_records"] = records


def get_prescription_audit_records(
    state: MutableMapping[str, Any],
) -> list[dict[str, Any]]:
    """Return prescription audit records newest first."""
    return list(reversed(state.get("prescription_audit_records", [])))


def update_prescription_audit_record(
    state: MutableMapping[str, Any], record_id: str, updates: dict[str, Any]
) -> dict[str, Any] | None:
    """Update a prescription record by ID, preserving its original upload and extraction."""
    records = list(state.get("prescription_audit_records", []))
    for index, record in enumerate(records):
        if record.get("record_id") == record_id:
            updated = {**record, **updates}
            records[index] = updated
            state["prescription_audit_records"] = records
            return updated
    return None
