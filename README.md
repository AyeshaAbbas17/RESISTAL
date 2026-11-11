# Resistal

**Antibiotic stewardship, made clearer** — a bilingual Streamlit workspace for organizing patient-reported history, reviewing prescription completeness, and preparing guidance from professionally confirmed details. Resistal does not diagnose, prescribe, or make treatment decisions. AI output is for professional review.

## Requirements

- Python 3.10 or later
- A Gemini API key for the live connection test (the rest of the interface works without it)

## Setup on macOS

From this project directory, create and activate a local virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set `GEMINI_API_KEY` to your key. Optionally change `GEMINI_MODEL`; the service default is `gemini-3.8-flash`. Keep `.env` private; it is excluded by `.gitignore`.

Alternatively, configure `GEMINI_API_KEY` and optionally `GEMINI_MODEL` in Streamlit secrets at `.streamlit/secrets.toml`.

Run the app:

```bash
streamlit run app.py
```

Use the language selector in the sidebar to switch between English and اردو. The Overview shows session-only aggregate counts and shortcuts into the existing workflows. The Gemini connection button sends only a harmless test prompt and displays Gemini's actual response.

## Patient Antibiotic History

The Patient History section asks about antibiotic use in the last three months. The interface switches between English and Urdu, while free-text answers may be in English, Urdu script, or Roman Urdu. On submission, the original answers are retained in the current Streamlit session and sent to Gemini to create a structured English summary for professional review. The form does not ask for personal identifiers.

If Gemini is unavailable, the submission remains in session state and the patient can retry summary generation without re-entering answers. Session records are temporary and are cleared when the Streamlit session ends. AI summaries are patient-reported, unverified information and must be reviewed by a healthcare professional.

## Prescription Audit

Healthcare staff can upload a PNG or JPEG prescription image. The image is validated and previewed, then Gemini extracts only visible text into structured fields. Extracted values are labeled unverified and can be edited before staff confirmation. Only confirmed details are passed to the Python completeness checks. Uploaded images and audit records are held in the current Streamlit session and are cleared when the session ends.

The audit checks only whether antibiotic name, strength/dosage, dose frequency, and treatment duration are missing or unclear. It does not apply clinical guidelines, judge treatment appropriateness, or recommend care. Results support professional review and do not replace clinical judgment.

## Patient Guidance

Patient Guidance is available for prescription records only after a healthcare professional confirms the extracted details in Prescription Audit. It uses only the confirmed medicine name, strength/dose, frequency, duration, route, and confirmed timing or special-instruction fields. The selected English or Urdu output is saved on that existing prescription record; retrying or generating the other language does not create another record.

Gemini is instructed to restate confirmed details without changing numbers or units or adding medical advice. The application validates the structured response, preserves missing/unclear markers locally, and supplies the general reminders separately. If generation fails or the output cannot be validated, no guidance fallback is shown. These session records are temporary and cleared when the session ends.

## Institutional Analytics

Analytics summarizes distinct Patient History and Prescription Audit records in the current Streamlit session. It keeps patient-reported, unverified use separate from completeness flags on prescriptions with healthcare-professional-confirmed details. Monthly charts are shown only when each of at least two months has at least five dated records; otherwise the page explains that there is not enough data for a trend chart. The dashboard reports use patterns and information completeness only; it does not measure antimicrobial resistance or assess clinical appropriateness. No names, record IDs, or individual responses are displayed.

## Project files

- `app.py` — bilingual Streamlit application shell and live connection test UI.
- `assets/resistal-symbol.svg`, `assets/resistal-logo.svg`, `assets/resistal-logo-dark.svg`, and `assets/resistal-favicon.svg` — custom brand assets.
- `.streamlit/config.toml` — application theme colors.
- `gemini_service.py` — API configuration, client initialization, and harmless test request.
- `audit_rules.py` — completeness-only prescription review checks; no clinical appropriateness rules are active.
- `analytics.py` — bilingual aggregate metrics and privacy-thresholded monthly trends for session records.
- `data_store.py` — session-state helpers for patient-history and prescription-audit records.
- `prescription_audit.py` — bilingual prescription image upload, extraction, confirmation, and completeness-review interface.
- `patient_guidance.py` — bilingual guidance generated only from confirmed prescription details.
- `requirements.txt` — Python dependencies.
- `.env.example` — environment variable template.
- `.gitignore` — excludes local secrets and generated files.
