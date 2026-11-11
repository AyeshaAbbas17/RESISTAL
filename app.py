"""Streamlit shell for Resistal's bilingual prototype."""

import streamlit as st
from dotenv import load_dotenv

from analytics import render_analytics, render_overview
from gemini_service import GeminiServiceError, test_gemini_connection
from patient_history import render_patient_history
from patient_guidance import render_patient_guidance
from prescription_audit import render_prescription_audit

load_dotenv()

TEXT = {
    "English": {
        "language": "Language / زبان", "navigation": "Navigation",
        "overview": "Overview",
        "patient_history": "Patient History", "prescription_audit": "Prescription Audit",
        "patient_guidance": "Patient Guidance", "analytics": "Analytics",
        "connection_scope": "Configuration check only. No patient information is sent.",
        "connection_title": "Gemini connection",
        "connection_description": "Send a harmless test prompt to check your Gemini API setup. No patient information is sent.",
        "test_button": "Test Gemini Connection", "testing": "Contacting Gemini…",
        "success": "Gemini connection succeeded. Response:",
        "missing_key": "Gemini API key is not configured. Add GEMINI_API_KEY to your local .env file, then restart the app.",
        "connection_error": "Could not complete the Gemini connection test. Check your API key, model name, and network connection.",
        "connection_timeout": "Gemini did not respond within the time limit. Please try again.",
        "connection_unavailable": "Gemini is temporarily unavailable. Please try again shortly.",
        "connection_failed": "Could not connect to Gemini. Check your connection and try again.",
        "placeholder": "This section will be available in a future development task.",
        "history_title": "Patient Antibiotic History",
        "history_intro": "Answer what you remember about antibiotic use during the last 3 months. You may answer in English, Urdu, or Roman Urdu. Do not guess if you are unsure.",
        "ai_notice": "When you submit, your answers are sent to Gemini to prepare an English summary for a healthcare professional. Your answers remain patient-reported and unverified.",
        "q_recent": "Have you taken any antibiotics during the last 3 months?",
        "q_name": "Do you remember the name of the antibiotic?",
        "name_input": "Enter the name if you remember it",
        "q_source": "How did you obtain the antibiotic?",
        "q_other_source": "Please describe the other source",
        "q_reason": "What was the reason for taking the antibiotic?",
        "reason_hint": "Examples to help describe your experience: fever, cough, sore throat, dental problem, or another reason. These are examples, not diagnoses.",
        "q_duration": "About how long did you take it?",
        "duration_hint": "For example: 2 days, 5 days, or unknown",
        "q_completion": "Which best describes how you took it?",
        "q_early_reason": "If you stopped early, would you like to explain why? (Optional)",
        "required_hint": "Required: recent antibiotic use, name recall choice, source, and course status when follow-up questions apply.",
        "submit_history": "Submit history",
        "choice_yes": "Yes", "choice_no": "No", "choice_not_sure": "Not sure",
        "choice_remember": "Yes, I remember the name", "choice_dont_remember": "I don't remember",
        "choice_doctor": "Prescribed by a doctor",
        "choice_bought_without_prescription": "Bought without a prescription",
        "choice_leftover": "Used leftover antibiotics",
        "choice_someone_else": "Recommended by someone else",
        "choice_other": "Other", "choice_completed": "Completed as prescribed",
        "choice_stopped_early": "Stopped earlier than instructed",
        "choice_still_taking": "Still taking it", "choice_no_instructions": "No instructions were given",
        "validation_recent": "Please choose an answer for recent antibiotic use.",
        "validation_memory": "Please choose whether you remember the antibiotic name.",
        "validation_name": "Enter the name if you remember it, or choose “I don't remember.”",
        "validation_source": "Please choose how you obtained the antibiotic.",
        "validation_other_source": "Please describe the other source, or select another option.",
        "validation_completion": "Please choose the course status that best describes your experience.",
        "summary_loading": "Preparing the English summary…",
        "summary_unavailable": "Gemini is temporarily busy. Your answers are saved. Please retry in a little while.",
        "summary_timeout": "Gemini took too long to respond. Your answers are saved; you can retry.",
        "summary_connection_failed": "Could not connect to Gemini right now. Your answers are saved; please retry.",
        "summary_invalid": "Gemini returned a summary that could not be safely read. Your answers are saved; please retry.",
        "summary_missing_key": "Gemini is not configured. Your answers are saved; ask the project administrator to configure the API.",
        "summary_failed": "The summary could not be generated. Your answers are saved; please retry.",
        "summary_caveat": "AI-generated from patient-reported information. This is not a verified medical record; a healthcare professional must review it.",
        "original_answers": "Original patient answers",
        "not_reported": "Not reported",
        "submission": "Submission",
        "submitted_at": "Submitted (UTC)",
        "retry_summary": "Retry English summary",
    },
    "اردو": {
        "language": "زبان / Language", "navigation": "صفحہ منتخب کریں",
        "overview": "جائزہ",
        "patient_history": "مریض کی سابقہ معلومات", "prescription_audit": "نسخے کا جائزہ",
        "patient_guidance": "مریض کے لیے رہنمائی", "analytics": "اعداد و شمار",
        "connection_scope": "صرف ترتیب کی جانچ۔ مریض کی کوئی معلومات نہیں بھیجی جائیں گی۔",
        "connection_title": "Gemini کنکشن",
        "connection_description": "Gemini API کی ترتیب جانچنے کے لیے ایک سادہ ٹیسٹ بھیجیں۔ مریض کی کوئی معلومات نہیں بھیجی جائیں گی۔",
        "test_button": "Gemini کنکشن چیک کریں", "testing": "Gemini سے رابطہ کیا جا رہا ہے…",
        "success": "Gemini کنکشن کامیاب ہوگیا۔ جواب:",
        "missing_key": "Gemini API key ترتیب نہیں دی گئی۔ اپنی مقامی .env فائل میں GEMINI_API_KEY شامل کریں، پھر ایپ دوبارہ شروع کریں۔",
        "connection_error": "Gemini کنکشن ٹیسٹ مکمل نہیں ہوسکا۔ اپنی API key، ماڈل کے نام اور انٹرنیٹ کنکشن کو چیک کریں۔",
        "connection_timeout": "Gemini نے مقررہ وقت میں جواب نہیں دیا۔ براہِ کرم دوبارہ کوشش کریں۔",
        "connection_unavailable": "Gemini عارضی طور پر دستیاب نہیں۔ کچھ دیر بعد دوبارہ کوشش کریں۔",
        "connection_failed": "اس وقت Gemini سے رابطہ نہیں ہو سکا۔ اپنا انٹرنیٹ کنکشن چیک کرکے دوبارہ کوشش کریں۔",
        "placeholder": "یہ حصہ آئندہ مرحلے میں دستیاب ہوگا۔",
        "history_title": "اینٹی بایوٹک کے استعمال کی سابقہ معلومات",
        "history_intro": "گزشتہ 3 ماہ میں اینٹی بایوٹک کے استعمال کے بارے میں جو کچھ یاد ہو، بتائیں۔ آپ اردو، رومن اردو یا انگریزی میں جواب دے سکتے ہیں۔ اگر یقین نہ ہو تو اندازہ نہ لگائیں۔",
        "ai_notice": "جمع کرانے پر آپ کے جوابات Gemini کو بھیجے جائیں گے تاکہ صحت کے ماہر کے لیے انگریزی خلاصہ تیار ہو۔ آپ کے جوابات مریض کی بتائی ہوئی غیر تصدیق شدہ معلومات رہیں گے۔",
        "q_recent": "کیا آپ نے گزشتہ 3 ماہ کے دوران کوئی اینٹی بایوٹک استعمال کی ہے؟",
        "q_name": "کیا آپ کو اینٹی بایوٹک کا نام یاد ہے؟",
        "name_input": "اگر نام یاد ہے تو درج کریں",
        "q_source": "آپ نے یہ اینٹی بایوٹک کیسے حاصل کی؟",
        "q_other_source": "براہِ کرم کوئی اور ذریعہ بتائیں",
        "q_reason": "آپ نے اینٹی بایوٹک کس وجہ سے استعمال کی؟",
        "reason_hint": "اپنا تجربہ بیان کرنے کے لیے مثالیں: بخار، کھانسی، گلے کی خراش، دانت کا مسئلہ یا کوئی اور وجہ۔ یہ صرف مثالیں ہیں، تشخیص نہیں۔",
        "q_duration": "آپ نے اسے تقریباً کتنے عرصے تک استعمال کیا؟",
        "duration_hint": "مثال: 2 دن، 5 دن، یا یاد نہیں",
        "q_completion": "آپ کے استعمال کی صورتِ حال کے لیے کون سا جواب درست ہے؟",
        "q_early_reason": "اگر آپ نے ہدایت سے پہلے چھوڑ دی تھی تو کیا آپ وجہ بتانا چاہیں گے؟ (اختیاری)",
        "required_hint": "ضروری: حالیہ استعمال، نام یاد ہونے کا جواب، ذریعہ، اور جہاں مزید سوالات ہوں وہاں کورس کی صورتِ حال۔",
        "submit_history": "معلومات جمع کریں",
        "choice_yes": "جی ہاں", "choice_no": "نہیں", "choice_not_sure": "یقین نہیں",
        "choice_remember": "جی ہاں، نام یاد ہے", "choice_dont_remember": "مجھے یاد نہیں",
        "choice_doctor": "ڈاکٹر کے نسخے پر",
        "choice_bought_without_prescription": "بغیر نسخے کے خریدی",
        "choice_leftover": "پہلے سے بچی ہوئی اینٹی بایوٹک استعمال کی",
        "choice_someone_else": "کسی دوسرے شخص کے مشورے پر",
        "choice_other": "دیگر", "choice_completed": "ڈاکٹر کی ہدایت کے مطابق مکمل کیا",
        "choice_stopped_early": "ہدایت سے پہلے چھوڑ دی",
        "choice_still_taking": "ابھی استعمال کر رہا/رہی ہوں", "choice_no_instructions": "کوئی ہدایت نہیں دی گئی",
        "validation_recent": "براہِ کرم حالیہ اینٹی بایوٹک کے استعمال کے بارے میں جواب منتخب کریں۔",
        "validation_memory": "براہِ کرم بتائیں کہ اینٹی بایوٹک کا نام یاد ہے یا نہیں۔",
        "validation_name": "اگر نام یاد ہے تو درج کریں یا “مجھے یاد نہیں” منتخب کریں۔",
        "validation_source": "براہِ کرم بتائیں کہ اینٹی بایوٹک کیسے حاصل کی۔",
        "validation_other_source": "براہِ کرم دوسرا ذریعہ بتائیں یا کوئی اور انتخاب کریں۔",
        "validation_completion": "براہِ کرم اپنے تجربے کے مطابق کورس کی صورتِ حال منتخب کریں۔",
        "summary_loading": "انگریزی خلاصہ تیار کیا جا رہا ہے…",
        "summary_unavailable": "Gemini عارضی طور پر مصروف ہے۔ آپ کے جوابات محفوظ ہیں۔ کچھ دیر بعد دوبارہ کوشش کریں۔",
        "summary_timeout": "Gemini کو جواب دینے میں بہت وقت لگا۔ آپ کے جوابات محفوظ ہیں؛ دوبارہ کوشش کر سکتے ہیں۔",
        "summary_connection_failed": "اس وقت Gemini سے رابطہ نہیں ہو سکا۔ آپ کے جوابات محفوظ ہیں؛ براہِ کرم دوبارہ کوشش کریں۔",
        "summary_invalid": "Gemini کا خلاصہ محفوظ طریقے سے پڑھا نہیں جا سکا۔ آپ کے جوابات محفوظ ہیں؛ دوبارہ کوشش کریں۔",
        "summary_missing_key": "Gemini ترتیب نہیں دیا گیا۔ آپ کے جوابات محفوظ ہیں؛ منتظم سے API ترتیب دینے کو کہیں۔",
        "summary_failed": "خلاصہ تیار نہیں ہو سکا۔ آپ کے جوابات محفوظ ہیں؛ دوبارہ کوشش کریں۔",
        "summary_caveat": "یہ اے آئی کا تیار کردہ خلاصہ مریض کی بتائی ہوئی معلومات پر مبنی ہے۔ یہ تصدیق شدہ طبی ریکارڈ نہیں؛ صحت کے ماہر کو اس کا جائزہ لینا چاہیے۔",
        "original_answers": "مریض کے اصل جوابات",
        "not_reported": "نہیں بتایا گیا",
        "submission": "جمع کرائی گئی معلومات",
        "submitted_at": "جمع کرانے کا وقت (UTC)",
        "retry_summary": "انگریزی خلاصے کے لیے دوبارہ کوشش کریں",
    },
}

PAGES = ("overview", "patient_history", "prescription_audit", "patient_guidance", "analytics")
NAV_ICONS = {
    "overview": ":material/dashboard:",
    "patient_history": ":material/history:",
    "prescription_audit": ":material/fact_check:",
    "patient_guidance": ":material/menu_book:",
    "analytics": ":material/analytics:",
}


def apply_language_styles(language: str) -> None:
    """Set text direction for the app and sidebar based on the selected language."""
    direction = "rtl" if language == "اردو" else "ltr"
    alignment = "right" if language == "اردو" else "left"
    st.markdown(
        f"""<style>
        :root {{ --navy:#163A5F; --royal:#2864A5; --soft-blue:#E8F0F7; --ivory:#FAF8F1; --paper:#FFFFFF; --charcoal:#283442; --slate:#5C6B7D; --line:#DDE3E8; --success:#32836A; --warning:#D69A3A; --critical:#C65B5B; }}
        html, body, .stApp {{ font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
        [data-testid="stIconMaterial"] {{ font-family:"Material Symbols Rounded" !important; font-weight:normal; font-style:normal; letter-spacing:normal; text-transform:none; direction:ltr; -webkit-font-feature-settings:"liga"; -webkit-font-smoothing:antialiased; }}
        .stApp {{ direction:{direction}; text-align:{alignment}; background:var(--ivory); color:var(--charcoal); }}
        .stApp [data-testid="stAppViewContainer"] > .main {{ background:var(--ivory); }}
        .stApp [data-testid="stMainBlockContainer"] {{ max-width:1280px; padding:2.5rem clamp(1.25rem, 4vw, 3.5rem) 4rem; }}
        .stApp p, .stApp h1, .stApp h2, .stApp h3 {{ text-align:{alignment}; }}
        .stApp p {{ color:var(--charcoal); line-height:1.65; }}
        h1,h2,h3,h4 {{ color:var(--navy); letter-spacing:-.025em; }}
        h1 {{ font-size:2.15rem !important; font-weight:720 !important; margin-bottom:.45rem !important; }}
        h2 {{ font-size:1.5rem !important; font-weight:680 !important; }}
        h3 {{ font-size:1.22rem !important; font-weight:680 !important; }}
        [data-testid="stSidebar"] {{ background:var(--paper); border-right:1px solid var(--line); }}
        [data-testid="stSidebar"] > div:first-child {{ padding-top:1.2rem; }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color:var(--slate); }}
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"], [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{ width:100%; justify-content:flex-start; text-align:left; padding:.62rem .75rem; border-radius:9px; }}
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{ border-color:transparent; background:transparent; color:var(--charcoal); }}
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {{ border-color:transparent; background:var(--soft-blue); color:var(--navy); }}
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{ background:var(--soft-blue); color:var(--navy); border-color:transparent; box-shadow:inset 3px 0 0 var(--royal); }}
        [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {{ background:#DDEAF5; border-color:transparent; color:var(--navy); }}
        [data-testid="stBaseButton-primary"] {{ background:var(--royal); border:1px solid var(--royal); border-radius:9px; padding:.56rem 1.15rem; font-weight:650; transition:background .16s ease,transform .16s ease; }}
        [data-testid="stBaseButton-primary"]:hover {{ background:var(--navy); border-color:var(--navy); transform:translateY(-1px); }}
        [data-testid="stBaseButton-secondary"] {{ border:1px solid #B9C7D5; border-radius:9px; color:var(--navy); background:var(--paper); }}
        [data-testid="stBaseButton-secondary"]:hover {{ border-color:var(--royal); color:var(--royal); }}
        .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {{ background:var(--paper); border-color:#CBD5DF; border-radius:9px; color:var(--charcoal); }}
        .stTextInput input:focus, .stTextArea textarea:focus {{ border-color:var(--royal); box-shadow:0 0 0 2px #2864A526; }}
        [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] {{ color:var(--navy); font-weight:600; }}
        [data-testid="stMetric"] {{ background:var(--paper); border:1px solid var(--line); border-radius:13px; padding:1rem 1.1rem; box-shadow:0 2px 8px #163A5F08; }}
        [data-testid="stMetricLabel"] {{ color:var(--slate); }}
        [data-testid="stMetricValue"] {{ color:var(--navy); font-weight:720; }}
        [data-testid="stAlert"] {{ border-radius:11px; border-width:1px; }}
        [data-testid="stExpander"] {{ border:1px solid var(--line); border-radius:12px; background:var(--paper); }}
        [data-testid="stVerticalBlockBorderWrapper"] > div {{ border-color:var(--line); border-radius:14px; background:var(--paper); }}
        [data-testid="stFileUploaderDropzone"] {{ background:var(--soft-blue); border:1px dashed #A9BCD0; border-radius:12px; }}
        [data-testid="stDataFrame"], [data-testid="stTable"] {{ border:1px solid var(--line); border-radius:10px; overflow:hidden; }}
        [data-testid="stCaptionContainer"] p, .stCaption {{ color:var(--slate); }}
        [data-testid="stMarkdownContainer"] a {{ color:var(--royal); }}
        [data-testid="stMarkdownContainer"] hr {{ border-color:var(--line); }}
        [data-testid="stSpinner"] {{ color:var(--royal); }}
        *:focus-visible {{ outline-color:var(--royal) !important; }}
        .resistal-brand {{ display:flex; align-items:center; gap:.7rem; padding:.2rem .25rem .8rem; }}
        .resistal-brand-name {{ color:var(--navy); font-size:1.3rem; font-weight:730; letter-spacing:-.04em; }}
        .resistal-brand-tag {{ color:var(--slate); font-size:.61rem; font-weight:650; letter-spacing:.09em; margin-top:.06rem; }}
        .resistal-callout {{ background:var(--soft-blue); border-left:3px solid var(--royal); border-radius:0 10px 10px 0; padding:.85rem 1rem; }}
        @media(max-width:1000px) {{ .stApp [data-testid="stHorizontalBlock"]:has(>[data-testid="stColumn"]:nth-child(4)) {{ flex-wrap:wrap; }} .stApp [data-testid="stHorizontalBlock"]:has(>[data-testid="stColumn"]:nth-child(4)) > [data-testid="stColumn"] {{ flex:1 1 calc(50% - .6rem) !important; min-width:calc(50% - .6rem) !important; }} }}
        @media(max-width:560px) {{ .stApp [data-testid="stHorizontalBlock"]:has(>[data-testid="stColumn"]:nth-child(4)) > [data-testid="stColumn"] {{ flex:1 1 100% !important; min-width:100% !important; }} }}
        @media(max-width:760px) {{ .stApp [data-testid="stMainBlockContainer"] {{ padding:1.35rem 1rem 3rem; }} h1 {{ font-size:1.75rem !important; }} }}
        </style>""",
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Resistal", page_icon="assets/resistal-favicon.svg", layout="wide")
    if "language" not in st.session_state:
        st.session_state.language = "English"
    if "navigation_page" not in st.session_state:
        st.session_state.navigation_page = "overview"

    with st.sidebar:
        st.markdown(
            """<div class="resistal-brand"><svg width="42" height="42" viewBox="0 0 96 96" aria-hidden="true"><path d="M25 74V22h25c18 0 21 26 2 29H25" fill="none" stroke="#163A5F" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/><path d="m46 51 25 23" fill="none" stroke="#2864A5" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/><circle cx="25" cy="22" r="6" fill="#2864A5"/></svg><div><div class="resistal-brand-name">Resistal</div><div class="resistal-brand-tag">CARE · REVIEW · STEWARDSHIP</div></div></div>""",
            unsafe_allow_html=True,
        )
        language = st.selectbox(
            TEXT[st.session_state.language]["language"],
            options=("English", "اردو"), key="language",
        )
        labels = TEXT[language]
        st.divider()
        st.markdown(f"**{labels['navigation']}**")
        for nav_key in PAGES:
            if st.button(
                labels[nav_key],
                key=f"nav_{nav_key}",
                type="primary" if st.session_state.navigation_page == nav_key else "secondary",
                icon=NAV_ICONS[nav_key],
                use_container_width=True,
            ):
                st.session_state.navigation_page = nav_key
                st.rerun()
        page_key = st.session_state.navigation_page

    apply_language_styles(language)
    labels = TEXT[language]
    st.title(labels[page_key])

    if page_key == "overview":
        render_overview(language)
    elif page_key == "patient_history":
        render_patient_history(labels, language)
    elif page_key == "prescription_audit":
        render_prescription_audit(language)
    elif page_key == "patient_guidance":
        render_patient_guidance(language)
    elif page_key == "analytics":
        render_analytics(language)
    st.divider()
    with st.expander(labels["connection_title"]):
        st.write(labels["connection_description"])
        st.caption(labels["connection_scope"])
        if st.button(labels["test_button"], type="secondary", key="gemini_connection_test"):
            with st.spinner(labels["testing"]):
                try:
                    response = test_gemini_connection()
                    st.success(labels["success"])
                    st.write(response)
                except GeminiServiceError as error:
                    if error.code == "missing_key":
                        st.error(labels["missing_key"])
                    elif error.code == "timeout":
                        st.error(labels["connection_timeout"])
                    elif error.code == "unavailable":
                        st.error(labels["connection_unavailable"])
                    elif error.code == "connection_failed":
                        st.error(labels["connection_failed"])
                    else:
                        st.error(labels["connection_error"])


if __name__ == "__main__":
    main()
