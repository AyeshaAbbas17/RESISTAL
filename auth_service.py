"""Session-scoped demo authentication for Resistal.

Accounts and salted password hashes live only in Streamlit session state. This
is suitable for a single-session prototype, not production authentication.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from typing import Any, MutableMapping
from uuid import uuid4


PASSWORD_ITERATIONS = 310_000
ACCOUNT_STATE_KEY = "_resistal_demo_accounts"
AUTH_USER_KEY = "_resistal_authenticated_user_id"
AUTH_ROLE_KEY = "_resistal_authenticated_role"
ROLES = frozenset({"doctor", "patient"})


class AuthError(ValueError):
    """Expected authentication or registration error with a stable code."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _accounts(state: MutableMapping[str, Any]) -> dict[str, dict[str, Any]]:
    accounts = state.get(ACCOUNT_STATE_KEY)
    if accounts is None:
        accounts = {}
        state[ACCOUNT_STATE_KEY] = accounts
    if not isinstance(accounts, dict):
        accounts = {}
        state[ACCOUNT_STATE_KEY] = accounts
    return accounts


def _password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)


def _safe_user(account: dict[str, Any]) -> dict[str, str]:
    return {key: str(account[key]) for key in ("user_id", "full_name", "email", "username", "role")}


def register_user(
    state: MutableMapping[str, Any], full_name: str, email: str,
    password: str, role: str,
) -> dict[str, str]:
    name = full_name.strip()
    normalized_email = email.strip().lower()
    if not name:
        raise AuthError("full_name_required")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized_email):
        raise AuthError("invalid_email")
    if role not in ROLES:
        raise AuthError("invalid_role")
    if len(password) < 8 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise AuthError("weak_password")
    accounts = _accounts(state)
    if any(account.get("email") == normalized_email for account in accounts.values()):
        raise AuthError("duplicate_email")
    base = re.sub(r"[^a-z0-9._-]", "", normalized_email.split("@", 1)[0]) or "user"
    used = {str(account.get("username", "")).lower() for account in accounts.values()}
    username = base
    suffix = 2
    while username in used:
        username = f"{base}{suffix}"
        suffix += 1
    salt = secrets.token_bytes(16)
    account = {
        "user_id": uuid4().hex,
        "full_name": name,
        "email": normalized_email,
        "username": username,
        "role": role,
        "password_salt": salt.hex(),
        "password_hash": _password_hash(password, salt).hex(),
    }
    accounts[account["user_id"]] = account
    return _safe_user(account)


def authenticate_user(
    state: MutableMapping[str, Any], identifier: str, password: str,
    expected_role: str | None = None,
) -> dict[str, str]:
    normalized = identifier.strip().lower()
    account = next(
        (item for item in _accounts(state).values()
         if normalized in (item.get("email", "").lower(), item.get("username", "").lower())),
        None,
    )
    if account is None:
        raise AuthError("invalid_credentials")
    try:
        salt = bytes.fromhex(account["password_salt"])
        expected = bytes.fromhex(account["password_hash"])
    except (KeyError, ValueError):
        raise AuthError("invalid_credentials") from None
    if not hmac.compare_digest(_password_hash(password, salt), expected):
        raise AuthError("invalid_credentials")
    if expected_role and account.get("role") != expected_role:
        raise AuthError("role_mismatch")
    state[AUTH_USER_KEY] = account["user_id"]
    state[AUTH_ROLE_KEY] = account["role"]
    return _safe_user(account)


def get_current_user(state: MutableMapping[str, Any]) -> dict[str, str] | None:
    user_id = state.get(AUTH_USER_KEY)
    if not user_id:
        return None
    account = _accounts(state).get(user_id)
    if not account or state.get(AUTH_ROLE_KEY) != account.get("role"):
        return None
    return _safe_user(account)


def has_role(state: MutableMapping[str, Any], role: str) -> bool:
    user = get_current_user(state)
    return bool(user and user["role"] == role)


def is_authenticated(state: MutableMapping[str, Any]) -> bool:
    return get_current_user(state) is not None


def list_users_by_role(state: MutableMapping[str, Any], role: str) -> list[dict[str, str]]:
    return [_safe_user(item) for item in _accounts(state).values() if item.get("role") == role]


def logout(state: MutableMapping[str, Any]) -> None:
    state.pop(AUTH_USER_KEY, None)
    state.pop(AUTH_ROLE_KEY, None)
    for key in (
        "auth_login_password", "auth_register_password", "auth_register_confirmation",
        "_auth_login_message", "_auth_registration_message",
    ):
        state.pop(key, None)
    for key in tuple(state):
        if key.startswith(("history_", "prescription_", "patient_guidance_")):
            state.pop(key, None)
    state["navigation_page"] = "login"
