"""Bilingual login and registration screens for the demo auth service."""

import streamlit as st

from auth_service import AuthError, authenticate_user, register_user


COPY = {
    "English": {
        "login": "Sign in", "register": "Create account", "identifier": "Email or username",
        "password": "Password", "show_password": "Show password", "full_name": "Full name",
        "email": "Email", "confirm_password": "Confirm password", "role": "Account type",
        "doctor": "Doctor", "patient": "Patient", "forgot": "Forgot password?",
        "forgot_note": "Password recovery is not available in this session-only demo.",
        "login_action": "Sign in", "register_action": "Create account", "no_account": "New to Resistal?",
        "have_account": "Already registered?", "created": "Account created. Sign in with your email or username: {username}",
        "demo_note": "Demo accounts and records are stored only in this Streamlit session. They are not production-secure and are not shared across sessions. A Doctor role is not professional verification.",
        "full_name_required": "Enter your full name.", "invalid_email": "Enter a valid email address.",
        "weak_password": "Use at least 8 characters with at least one letter and one number.",
        "duplicate_email": "An account with this email already exists in this session.",
        "invalid_role": "Choose Doctor or Patient.", "invalid_credentials": "The email/username or password is incorrect.",
        "role_mismatch": "This account does not have the selected role.", "password_mismatch": "Passwords do not match.",
    },
    "اردو": {
        "login": "لاگ اِن", "register": "اکاؤنٹ بنائیں", "identifier": "ای میل یا صارف نام",
        "password": "پاس ورڈ", "show_password": "پاس ورڈ دکھائیں", "full_name": "پورا نام",
        "email": "ای میل", "confirm_password": "پاس ورڈ کی تصدیق", "role": "اکاؤنٹ کی قسم",
        "doctor": "ڈاکٹر", "patient": "مریض", "forgot": "پاس ورڈ بھول گئے؟",
        "forgot_note": "اس سیشن پر مبنی ڈیمو میں پاس ورڈ بحالی دستیاب نہیں۔",
        "login_action": "لاگ اِن", "register_action": "اکاؤنٹ بنائیں", "no_account": "Resistal پر نئے ہیں؟",
        "have_account": "پہلے سے اکاؤنٹ ہے؟", "created": "اکاؤنٹ بن گیا۔ اس ای میل یا صارف نام سے لاگ اِن کریں: {username}",
        "demo_note": "ڈیمو اکاؤنٹس اور ریکارڈ صرف اسی Streamlit سیشن میں محفوظ ہیں۔ یہ پیداواری استعمال کے لیے محفوظ نہیں اور دوسرے سیشنز میں مشترک نہیں ہوتے۔ ڈاکٹر کا کردار پیشہ ورانہ تصدیق نہیں ہے۔",
        "full_name_required": "اپنا پورا نام درج کریں۔", "invalid_email": "درست ای میل درج کریں۔",
        "weak_password": "کم از کم 8 حروف، ایک حرف اور ایک عدد استعمال کریں۔",
        "duplicate_email": "اس سیشن میں اس ای میل کا اکاؤنٹ پہلے سے موجود ہے۔",
        "invalid_role": "ڈاکٹر یا مریض منتخب کریں۔", "invalid_credentials": "ای میل/صارف نام یا پاس ورڈ درست نہیں۔",
        "role_mismatch": "اس اکاؤنٹ کا منتخب کردہ کردار نہیں ہے۔", "password_mismatch": "پاس ورڈ ایک جیسے نہیں ہیں۔",
    },
}


def _login_submit() -> None:
    state = st.session_state
    copy = COPY.get(state.get("language", "English"), COPY["English"])
    role_label = state.get("auth_login_role", copy["doctor"])
    role = "doctor" if role_label == copy["doctor"] else "patient"
    try:
        authenticate_user(
            state, state.get("auth_identifier", ""), state.get("auth_login_password", ""),
            expected_role=role,
        )
    except AuthError as error:
        state["_auth_login_message"] = ("error", copy.get(error.code, copy["invalid_credentials"]))
    else:
        state["_auth_login_message"] = None
        state["navigation_page"] = "overview"
    state.pop("auth_login_password", None)


def _register_submit() -> None:
    state = st.session_state
    copy = COPY.get(state.get("language", "English"), COPY["English"])
    password = state.get("auth_register_password", "")
    confirmation = state.get("auth_register_confirmation", "")
    if password != confirmation:
        state["_auth_registration_message"] = ("error", copy["password_mismatch"])
    else:
        role = "doctor" if state.get("auth_register_role", copy["doctor"]) == copy["doctor"] else "patient"
        try:
            user = register_user(
                state, state.get("auth_register_full_name", ""),
                state.get("auth_register_email", ""), password, role,
            )
        except AuthError as error:
            state["_auth_registration_message"] = ("error", copy.get(error.code, copy["invalid_role"]))
        else:
            state["_auth_registration_message"] = (
                "success", copy["created"].format(username=user["username"])
            )
    state.pop("auth_register_password", None)
    state.pop("auth_register_confirmation", None)


def render_auth_page(language: str) -> None:
    c = COPY[language]
    tab_login, tab_register = st.tabs((c["login"], c["register"]))
    with tab_login:
        role_label = st.radio(c["role"], (c["doctor"], c["patient"]), horizontal=True, key="auth_login_role")
        role = "doctor" if role_label == c["doctor"] else "patient"
        identifier = st.text_input(c["identifier"], key="auth_identifier")
        show = st.checkbox(c["show_password"], key="auth_login_show_password")
        password = st.text_input(c["password"], type="default" if show else "password", key="auth_login_password")
        st.button(c["login_action"], type="primary", key="auth_login_submit", on_click=_login_submit)
        login_message = st.session_state.pop("_auth_login_message", None)
        if login_message:
            st.error(login_message[1])
        if st.button(c["forgot"], key="auth_forgot_password"):
            st.info(c["forgot_note"])

    with tab_register:
        full_name = st.text_input(c["full_name"], key="auth_register_full_name")
        email = st.text_input(c["email"], key="auth_register_email")
        role_label = st.radio(c["role"], (c["doctor"], c["patient"]), horizontal=True, key="auth_register_role")
        show = st.checkbox(c["show_password"], key="auth_register_show_password")
        password = st.text_input(c["password"], type="default" if show else "password", key="auth_register_password")
        confirmation = st.text_input(c["confirm_password"], type="default" if show else "password", key="auth_register_confirmation")
        st.button(c["register_action"], type="primary", key="auth_register_submit", on_click=_register_submit)
    registration_message = st.session_state.pop("_auth_registration_message", None)
    if registration_message:
        if registration_message[0] == "success":
            st.success(registration_message[1])
        else:
            st.error(registration_message[1])
    st.caption(c["demo_note"])
