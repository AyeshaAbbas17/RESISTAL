# RESISTAL
### AI-Powered Antibiotic Stewardship Platform

**RESISTAL** is an AI-powered antibiotic stewardship platform designed to promote responsible antibiotic use and address antibiotic misuse in Pakistan. It aims to bridge the gap between patients and healthcare professionals through AI-assisted patient history collection, prescription auditing, and accessible medication guidance.

By combining Artificial Intelligence with rule-based validation, RESISTAL helps organize relevant antibiotic information, highlight missing prescription details, and support informed review by healthcare professionals.

---

## Problem Statement

Antibiotic misuse is a significant public health concern. Practices such as self-medication, using leftover antibiotics, incomplete treatment courses, and inadequate prescription information can contribute to inappropriate antibiotic use.

Patients may also struggle to understand prescription instructions, particularly when medical information is not communicated in accessible language.

RESISTAL aims to address these challenges through a unified platform that supports patients and healthcare professionals throughout the antibiotic-use process.

## Key Features

### 1. Patient Antibiotic History
- Collects information about patients' previous antibiotic usage.
- Identifies reported self-medication, leftover antibiotic use, and early discontinuation.
- Supports English, Urdu, and Roman Urdu responses.
- Uses Gemini AI to generate structured, doctor-facing summaries.
- Preserves patient-reported information and uncertainty.

### 2. Prescription Audit
- Allows healthcare professionals to upload prescription images.
- Uses Gemini AI to extract relevant prescription information.
- Provides editable fields for professional verification.
- Uses a Python-based rule engine to identify missing or unclear information, including:
  - Antibiotic name
  - Strength or dosage
  - Frequency
  - Duration
- Displays review flags without independently declaring a prescription clinically incorrect.

### 3. Patient Guidance
- Generates easy-to-understand patient guidance in English and Urdu.
- Uses doctor-confirmed prescription details as its source.
- Helps patients understand their recorded medication instructions.
- Highlights missing or unclear information that should be confirmed with a healthcare professional.

### 4. Institutional Analytics
- Provides aggregated insights based on available records.
- Highlights patterns such as self-medication, leftover antibiotic use, and early discontinuation.
- Summarizes prescription completeness findings.
- Displays trends when sufficient data is available.
- Avoids exposing individual patient information in aggregate visualizations.

### 5. Antibiotic Compatibility Checker — In Development
We are also implementing an Antibiotic Compatibility Checker to extend RESISTAL's prescription-review capabilities.

The intended functionality is to help identify potential antibiotic compatibility concerns using predefined, evidence-based checks and present them for healthcare professional review.

This feature is currently under development and is not yet part of the completed functionality.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Web application interface |
| Google Gemini API | AI-powered extraction, summaries, and patient guidance |
| Pandas | Data handling and analytics |
| Git & GitHub | Version control and collaboration |
| Google Antigravity | AI-assisted development environment |

## System Architecture

RESISTAL combines AI-powered processing with deterministic Python-based validation.

- **Gemini AI:** Processes patient responses, extracts prescription information, and generates patient-friendly guidance.
- **Python Rule Engine:** Applies predefined checks to identify missing or unclear prescription information.
- **Streamlit:** Provides the interactive application interface.
- **Session-Based Storage:** Maintains demonstration records during the active application session.

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

The application should open in your browser at:

```text
http://localhost:8501
```

---

## Project Structure

The main project files include:

```text
RESISTAL/
│
├── app.py
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
- Demonstration records should be synthetic and must not contain identifiable real patient information.

## Current Limitations

- Records are maintained in Streamlit session state and are not permanently stored.
- Production-grade authentication and role-based access controls are not yet established.
- The Antibiotic Compatibility Checker is under development.
- Live Gemini API availability may vary.
- The prototype is not intended for independent clinical decision-making or production healthcare deployment.

## Future Enhancements

- Complete the Antibiotic Compatibility Checker.
- Introduce secure authentication with separate doctor and patient dashboards.
- Implement a secure, persistent database.
- Introduce appropriate role-based access and patient-record privacy controls.
- Expand evidence-based prescription review capabilities.
- Improve institutional analytics with larger datasets.
- Further enhance Urdu and Roman Urdu accessibility.

## Development

RESISTAL was developed collaboratively using **Google Antigravity** as the AI-assisted development environment, alongside Python, Streamlit, and the Google Gemini API.

The project is maintained through GitHub for version control and team collaboration.

---

**RESISTAL — Promoting Responsible Antibiotic Use Through AI.**
