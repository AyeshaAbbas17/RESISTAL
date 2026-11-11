# RESISTAL
### AI-Powered Antibiotic Stewardship Platform

RESISTAL is an AI-powered antibiotic stewardship platform designed to promote responsible antibiotic use and address antibiotic misuse in Pakistan. It connects patients and healthcare professionals through AI-assisted patient history collection, prescription auditing, patient guidance, and institutional analytics.

By combining Artificial Intelligence with rule-based validation, RESISTAL helps organize antibiotic-related information, highlight missing prescription details, and support informed review by healthcare professionals.

---

## Problem Statement

Antibiotic misuse is a significant public health concern. Practices such as self-medication, using leftover antibiotics, incomplete treatment courses, and inadequate prescription information can contribute to inappropriate antibiotic use.

Patients may also struggle to understand prescription instructions, particularly when medical information is not communicated in accessible language.

RESISTAL aims to address these challenges through a unified platform that supports patients and healthcare professionals throughout the antibiotic-use process.

## Key Features

### 1. Role-Based Authentication

RESISTAL provides separate experiences for two types of users:

**Doctor Dashboard**
- Access to Patient Antibiotic History.
- Prescription Audit and prescription completeness checks.
- Patient Guidance generation.
- Institutional Analytics.

**Patient Dashboard**
- Submit and view personal antibiotic history.
- Access available patient prescription guidance.
- Access only their own patient records.

The current demonstration authentication system includes:
- User registration and login.
- Doctor and Patient role selection.
- Password validation and hashing.
- Role-based navigation and access restrictions.
- Logout functionality.

*Note: Authentication is currently session-based for demonstration purposes. Doctor registration does not verify professional credentials.*

### 2. Patient Antibiotic History

- Collects information about patients' previous antibiotic usage.
- Identifies reported self-medication, leftover antibiotic use, and early discontinuation.
- Supports English, Urdu, and Roman Urdu responses.
- Uses Gemini AI to generate structured, doctor-facing summaries.
- Preserves patient-reported information and uncertainty.

### 3. Prescription Audit

- Allows healthcare professionals to upload prescription images.
- Uses Gemini AI to extract relevant prescription information.
- Provides editable fields for professional verification.
- Uses a Python-based rule engine to identify missing or unclear information, including:
  - Antibiotic name
  - Strength or dosage
  - Frequency
  - Duration
- Displays review flags without independently declaring a prescription clinically incorrect.

### 4. Patient Guidance

- Generates easy-to-understand patient guidance in English and Urdu.
- Uses doctor-confirmed prescription details as its source.
- Helps patients understand their recorded medication instructions.
- Highlights missing or unclear information that should be confirmed with a healthcare professional.

### 5. Institutional Analytics

- Provides aggregated insights based on available records.
- Highlights patterns such as self-medication, leftover antibiotic use, and early discontinuation.
- Summarizes prescription completeness findings.
- Displays monthly trends when sufficient data is available.
- Deduplicates records and findings to avoid inflated metrics.
- Keeps patient-reported information separate from professionally confirmed prescription findings.
- Avoids exposing individual patient names, IDs, or answers in dashboard metrics and charts.

### 6. Antibiotic Compatibility Checker — In Development

We are implementing an Antibiotic Compatibility Checker to extend RESISTAL's prescription-review capabilities.

The intended functionality is to identify potential antibiotic compatibility concerns using predefined, evidence-based checks and present relevant findings for healthcare professional review.

This feature is currently under development and is not yet part of the completed functionality.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Web application interface |
| Google Gemini API | AI-powered extraction, summaries, and patient guidance |
| Pandas | Data handling and analytics |
| Git & GitHub | Version control and team collaboration |
| Google Antigravity | AI-assisted development environment |

## System Architecture

RESISTAL combines AI-powered processing with deterministic Python-based validation.

- **Gemini AI:** Processes patient responses, extracts prescription information, and generates patient-friendly guidance.
- **Python Rule Engine:** Applies predefined checks to identify missing or unclear prescription information.
- **Authentication Service:** Handles demonstration registration, login, password hashing, and role-based access.
- **Streamlit:** Provides the interactive application interface and separate dashboards.
- **Session-Based Storage:** Maintains demonstration accounts and application records during the active session.

Healthcare professionals remain responsible for reviewing information and making clinical decisions.

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/AyeshaAbbas17/RESISTAL.git
cd RESISTAL
```

### 2. Create a Virtual Environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project's root directory.

Add your Gemini API configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_configured_gemini_model
```

Use `.env.example` as a reference if provided.

**Important:** Never upload your actual `.env` file or API key to GitHub.

### 5. Run the Application

```bash
streamlit run app.py
```

Open the application in your browser:

```text
http://localhost:8501
```

### 6. Register and Log In

- Open the registration page.
- Enter your name, email, password, and select Doctor or Patient.
- Log in using the registered credentials and matching role.
- You will be redirected to the corresponding dashboard.

Demo accounts are maintained within the active Streamlit session.

---

## Project Structure

```text
RESISTAL/
│
├── app.py
├── auth_service.py
├── auth_ui.py
├── patient_history.py
├── prescription_audit.py
├── patient_guidance.py
├── audit_rules.py
├── analytics.py
├── data_store.py
├── gemini_service.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Safety and Responsible Use

RESISTAL is a prototype intended to support antibiotic stewardship and healthcare professionals.

- It does not diagnose medical conditions or prescribe antibiotics.
- It does not independently recommend changing or discontinuing treatment.
- Prescription extraction must be reviewed and confirmed by a healthcare professional.
- Automated flags indicate missing or unclear information, not definitive clinical errors.
- Patient guidance is based on doctor-confirmed prescription information.
- AI-generated outputs may contain errors and require appropriate review.
- Doctor registration does not establish or verify medical credentials.
- Demonstration records should be synthetic and must not contain identifiable real patient information.

## Current Limitations

- User accounts and records are maintained in Streamlit session state and are not permanently stored.
- Separate sessions do not share demonstration accounts or records.
- Authentication is a demonstration implementation, not production-grade authentication.
- No persistent institutional database is currently integrated.
- The Antibiotic Compatibility Checker is under development.
- Live Gemini API availability may vary.
- The prototype is not intended for independent clinical decision-making or production healthcare deployment.

## Future Enhancements

- Complete the Antibiotic Compatibility Checker using appropriate evidence-based checks.
- Introduce secure, persistent user authentication.
- Integrate a secure database for long-term record management.
- Introduce verified healthcare professional accounts and appropriate role-based permissions.
- Expand evidence-based prescription review capabilities.
- Improve institutional analytics with larger datasets.
- Further enhance Urdu and Roman Urdu accessibility.

## Development

RESISTAL was developed collaboratively using **Google Antigravity** as the AI-assisted development environment, alongside Python, Streamlit, and the Google Gemini API.

GitHub is used for source-code management and team collaboration.

---

**RESISTAL — Promoting Responsible Antibiotic Use Through AI.**
