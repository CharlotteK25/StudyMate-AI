"""
Firebase Authentication + Firestore wrapper.

Real Firebase is used automatically once you add credentials to
.streamlit/secrets.toml (see SETUP.md). Until then, every function
transparently falls back to services/local_store.py (a local JSON file)
so the whole app is fully usable for development/demoing without any
external account.

Auth strategy:
- Sign up / sign in / password reset go through the Firebase Identity
  Toolkit REST API using the project's Web API Key (this is the standard
  way to do email/password auth from a Python backend - the firebase-admin
  SDK deliberately does NOT expose password sign-in, only admin-level
  user management and token verification).
- Firestore reads/writes use the firebase-admin SDK with a service-account
  key for full server-side access to notes, flashcards, quiz results,
  chat history and study plans.
"""

import hashlib
import os
import uuid
import requests
import streamlit as st

from services import local_store as ls

def _get_secret(key, default=None):
    """Read a value from st.secrets, safely returning `default` if no
    secrets.toml file exists at all (st.secrets raises in that case
    instead of behaving like a normal empty dict)."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


FIREBASE_WEB_API_KEY = _get_secret("FIREBASE_WEB_API_KEY", "")
FIREBASE_SERVICE_ACCOUNT = _get_secret("firebase_service_account", None)

_auth_section = _get_secret("auth", None)


def _auth_has_client_id(section) -> bool:
    if not section:
        return False
    if section.get("client_id"):
        return True
    google = section.get("google")
    return bool(google and google.get("client_id"))


GOOGLE_LOGIN_CONFIGURED = _auth_has_client_id(_auth_section)

INIT_ERROR = ""
LAST_ERROR = ""

USE_FIREBASE = bool(FIREBASE_WEB_API_KEY) and bool(FIREBASE_SERVICE_ACCOUNT)

_firestore_client = None

if USE_FIREBASE:
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            cred = credentials.Certificate(dict(FIREBASE_SERVICE_ACCOUNT))
            firebase_admin.initialize_app(cred)
        _firestore_client = firestore.client()
    except Exception as e:
        INIT_ERROR = f"{type(e).__name__}: {e}"
        USE_FIREBASE = False


def _friendly_error(e) -> str:
    """Turn a Firestore/Identity Toolkit failure into something actionable."""
    text = str(e)
    project = (FIREBASE_SERVICE_ACCOUNT or {}).get("project_id", "your project")
    if "SERVICE_DISABLED" in text or "has not been used in project" in text:
        return (f"Cloud Firestore is not enabled for project '{project}'. In the Firebase "
                f"Console open Build > Firestore Database > Create database, then reload. "
                f"Saving to the local JSON store meanwhile.")
    if "PERMISSION_DENIED" in text or "Missing or insufficient permissions" in text:
        return (f"Firestore denied the write for project '{project}' - check the database "
                f"security rules. Saving to the local JSON store meanwhile.")
    if "NOT_FOUND" in text and "database" in text.lower():
        return (f"No Firestore database exists in project '{project}' yet. Create one in "
                f"Build > Firestore Database. Saving to the local JSON store meanwhile.")
    return f"Firestore call failed ({type(e).__name__}): {text[:200]}. Using the local store."


def _auth_error(message: str) -> str:
    """Map Identity Toolkit error codes to plain English."""
    return {
        "CONFIGURATION_NOT_FOUND": (
            "Firebase Authentication has not been enabled for this project. In the Firebase "
            "Console open Build > Authentication > Get started and enable the Email/Password "
            "provider, then try again."),
        "EMAIL_EXISTS": "An account with that email already exists.",
        "EMAIL_NOT_FOUND": "No account found with that email.",
        "INVALID_PASSWORD": "Incorrect password.",
        "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
        "WEAK_PASSWORD : Password should be at least 6 characters":
            "Password must be at least 6 characters.",
        "OPERATION_NOT_ALLOWED":
            "Email/password sign-in is disabled for this Firebase project. Enable it under "
            "Authentication > Sign-in method.",
        "API_KEY_INVALID": "FIREBASE_WEB_API_KEY is invalid - copy it again from "
                           "Project Settings > General > Web API Key.",
        "INVALID_EMAIL": "That email address doesn't look valid.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Wait a moment and try again.",
    }.get(message, message or "Request failed")


_INFRA_AUTH_ERRORS = {"CONFIGURATION_NOT_FOUND", "API_KEY_INVALID", "OPERATION_NOT_ALLOWED"}


def render_notice():
    """Show, once, any Firestore failure recorded since the last render.
    Stashed in session_state because the callers st.rerun() straight after,
    which would wipe a warning drawn inline."""
    try:
        msg = st.session_state.pop("_db_notice", None)
    except Exception:
        return
    if msg:
        st.warning(msg, icon=":material/cloud_off:")


def _remember(msg: str):
    """Queue a warning, but only the first time this session. Firestore being
    disabled fails on every single save, and repeating the same banner after
    every click just becomes wallpaper - Profile > Service connections is the
    place to check it on demand."""
    try:
        seen = st.session_state.setdefault("_db_notice_seen", set())
        if msg in seen:
            return
        seen.add(msg)
        st.session_state["_db_notice"] = msg
    except Exception:
        pass


def _try_firestore(op, fallback):
    """Run a Firestore operation, degrading to the local JSON store if it fails
    (API disabled, rules denied, no network). Keeps the app usable end-to-end."""
    global LAST_ERROR
    if not USE_FIREBASE:
        return fallback()
    try:
        result = op()
        LAST_ERROR = ""
        return result
    except Exception as e:
        LAST_ERROR = _friendly_error(e)
        _remember(LAST_ERROR)
        return fallback()


_PROBED = False
_PROBE_ERROR = ""


def _probe_firestore():
    global _PROBED, _PROBE_ERROR
    if _PROBED or not USE_FIREBASE:
        return
    _PROBED = True
    try:
        _firestore_client.collection("_diagnostic").document("probe").get()
    except Exception as e:
        _PROBE_ERROR = _friendly_error(e)


def status() -> tuple:
    """(ok: bool, message: str) - what to show the user about Firebase right now."""
    if not FIREBASE_WEB_API_KEY and not FIREBASE_SERVICE_ACCOUNT:
        return False, "No Firebase credentials in secrets.toml - using the local demo store."
    if not FIREBASE_WEB_API_KEY:
        return False, "FIREBASE_WEB_API_KEY is missing - sign-in falls back to local accounts."
    if not FIREBASE_SERVICE_ACCOUNT:
        return False, "[firebase_service_account] is missing - data saves to the local store."
    if INIT_ERROR:
        return False, f"Firebase could not start: {INIT_ERROR}"
    if LAST_ERROR:
        return False, LAST_ERROR
    _probe_firestore()
    if _PROBE_ERROR:
        return False, _PROBE_ERROR
    return True, f"Firebase connected (project {FIREBASE_SERVICE_ACCOUNT.get('project_id')})."


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def _identity_toolkit(endpoint: str, payload: dict):
    """POST to the Identity Toolkit REST API.
    Returns (data, error_code). error_code is "" on success, or the raw
    Firebase error code, or "NETWORK" when the request never landed."""
    global LAST_ERROR
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={FIREBASE_WEB_API_KEY}"
    try:
        resp = requests.post(url, json=payload, timeout=20)
    except requests.RequestException as e:
        LAST_ERROR = f"Could not reach Firebase Authentication: {e}"
        return {}, "NETWORK"
    data = resp.json() if resp.content else {}
    if resp.status_code != 200:
        return data, data.get("error", {}).get("message", "REQUEST_FAILED")
    return data, ""


def _local_signup(name: str, email: str, password: str):
    if ls.get_user_by_email(email):
        return False, "An account with that email already exists"
    uid = uuid.uuid4().hex
    salt = uuid.uuid4().hex
    ls.save_user(email, {
        "uid": uid, "name": name, "email": email,
        "salt": salt, "password_hash": _hash_password(password, salt)
    })
    return True, {"uid": uid, "name": name, "email": email}


def _public_user(record: dict) -> dict:
    user = {"uid": record["uid"], "name": record["name"], "email": record["email"]}
    if record.get("photo"):
        user["photo"] = record["photo"]
    return user


def _local_signin(email: str, password: str):
    record = ls.get_user_by_email(email)
    if not record:
        return False, "No account found with that email"
    if not record.get("salt"):
        return False, "That account signs in with Google - use the Google button above."
    if _hash_password(password, record["salt"]) != record["password_hash"]:
        return False, "Incorrect password"
    return True, _public_user(record)


def get_or_create_oidc_user(name: str, email: str):
    """Find-or-create a user profile for someone who signed in via an OIDC
    provider (e.g. Google, through Streamlit's native st.login()). These
    users have no password on our side - identity was already verified by
    the provider. Returns (True, user_dict)."""
    doc_id = "oidc_" + hashlib.sha256(email.lower().encode()).hexdigest()[:24]

    def from_firestore():
        doc_ref = _firestore_client.collection("users").document(doc_id)
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({"name": name, "email": email, "provider": "google"})
            return True, {"uid": doc_id, "name": name, "email": email}
        stored = doc.to_dict()
        return True, _public_user({"uid": doc_id, "name": stored.get("name", name),
                                   "email": email, "photo": stored.get("photo")})

    def from_local():
        record = ls.get_user_by_email(email)
        if record:
            return True, _public_user(record)
        uid = uuid.uuid4().hex
        ls.save_user(email, {"uid": uid, "name": name, "email": email, "provider": "google"})
        return True, {"uid": uid, "name": name, "email": email}

    return _try_firestore(from_firestore, from_local)


def sign_up(name: str, email: str, password: str):
    """Returns (success: bool, message_or_user: str|dict)"""
    global LAST_ERROR
    if not USE_FIREBASE:
        return _local_signup(name, email, password)

    data, err = _identity_toolkit("signUp", {
        "email": email, "password": password, "returnSecureToken": True
    })
    if err:
        if err in _INFRA_AUTH_ERRORS or err == "NETWORK":
            LAST_ERROR = _auth_error(err) if err != "NETWORK" else LAST_ERROR
            return _local_signup(name, email, password)
        return False, _auth_error(err)

    uid = data["localId"]
    _try_firestore(
        lambda: _firestore_client.collection("users").document(uid).set(
            {"name": name, "email": email}),
        lambda: ls.save_user(email, {"uid": uid, "name": name, "email": email}),
    )
    return True, {"uid": uid, "name": name, "email": email}


def sign_in(email: str, password: str):
    global LAST_ERROR
    if not USE_FIREBASE:
        return _local_signin(email, password)

    data, err = _identity_toolkit("signInWithPassword", {
        "email": email, "password": password, "returnSecureToken": True
    })
    if err:
        if err in _INFRA_AUTH_ERRORS or err == "NETWORK":
            LAST_ERROR = _auth_error(err) if err != "NETWORK" else LAST_ERROR
            return _local_signin(email, password)
        return False, _auth_error(err)

    uid = data["localId"]
    fallback_name = email.split("@")[0]

    def lookup_profile():
        profile = _firestore_client.collection("users").document(uid).get()
        data = profile.to_dict() if profile.exists else {}
        return {"name": data.get("name", fallback_name), "photo": data.get("photo")}

    def local_profile():
        record = ls.get_user_by_email(email) or {}
        return {"name": record.get("name", fallback_name), "photo": record.get("photo")}

    extra = _try_firestore(lookup_profile, local_profile)
    return True, _public_user({"uid": uid, "email": email, **extra})


def update_profile(uid: str, email: str, fields: dict):
    """Merge extra profile fields (e.g. photo) into the user's record."""
    def remote():
        _firestore_client.collection("users").document(uid).set(fields, merge=True)

    def local():
        record = ls.get_user_by_email(email) or {"uid": uid, "name": "", "email": email}
        record.update(fields)
        ls.save_user(email, record)

    return _try_firestore(remote, local)


def send_password_reset(email: str):
    if USE_FIREBASE:
        _, err = _identity_toolkit("sendOobCode", {
            "requestType": "PASSWORD_RESET", "email": email
        })
        if not err:
            return True
        if err not in _INFRA_AUTH_ERRORS and err != "NETWORK":
            return False
    return ls.get_user_by_email(email) is not None


def _user_col(uid: str, name: str):
    return _firestore_client.collection("users").document(uid).collection(name)


def save_note(uid: str, note: dict):
    def local():
        ls.append_item("notes", uid, note)
    return _try_firestore(lambda: _user_col(uid, "notes").document(note["id"]).set(note), local)


def update_note(uid: str, note_id: str, updates: dict):
    def local():
        notes = ls.get_collection("notes", uid)
        for n in notes:
            if n["id"] == note_id:
                n.update(updates)
        ls.set_collection_item("notes", uid, notes)
    return _try_firestore(lambda: _user_col(uid, "notes").document(note_id).update(updates), local)


def delete_note(uid: str, note_id: str):
    def local():
        notes = [n for n in ls.get_collection("notes", uid) if n["id"] != note_id]
        ls.set_collection_item("notes", uid, notes)
    return _try_firestore(lambda: _user_col(uid, "notes").document(note_id).delete(), local)


def get_notes(uid: str):
    return _try_firestore(
        lambda: [d.to_dict() for d in _user_col(uid, "notes").stream()],
        lambda: ls.get_collection("notes", uid),
    )


def save_flashcard_deck(uid: str, deck_name: str, cards: list):
    def local():
        decks = ls.get_collection("flashcards", uid)
        if not isinstance(decks, dict):
            decks = {}
        decks[deck_name] = cards
        ls.set_collection_item("flashcards", uid, decks)
    return _try_firestore(
        lambda: _user_col(uid, "flashcards").document(deck_name).set({"cards": cards}), local)


def delete_flashcard_deck(uid: str, deck_name: str):
    def local():
        decks = ls.get_collection("flashcards", uid)
        if isinstance(decks, dict) and deck_name in decks:
            del decks[deck_name]
        ls.set_collection_item("flashcards", uid, decks)
    return _try_firestore(
        lambda: _user_col(uid, "flashcards").document(deck_name).delete(), local)


def get_flashcard_decks(uid: str):
    def local():
        decks = ls.get_collection("flashcards", uid)
        return decks if isinstance(decks, dict) else {}
    return _try_firestore(
        lambda: {d.id: d.to_dict().get("cards", []) for d in _user_col(uid, "flashcards").stream()},
        local,
    )


def save_quiz_result(uid: str, result: dict):
    return _try_firestore(
        lambda: _user_col(uid, "quiz_results").add(result),
        lambda: ls.append_item("quiz_results", uid, result),
    )


def get_quiz_results(uid: str):
    return _try_firestore(
        lambda: [d.to_dict() for d in _user_col(uid, "quiz_results").stream()],
        lambda: ls.get_collection("quiz_results", uid),
    )


def save_chat_message(uid: str, session_name: str, message: dict):
    def remote():
        doc_ref = _user_col(uid, "chat_sessions").document(session_name)
        doc = doc_ref.get()
        history = doc.to_dict().get("messages", []) if doc.exists else []
        history.append(message)
        doc_ref.set({"messages": history})

    def local():
        chats = ls.get_collection("chat_history", uid)
        if not isinstance(chats, dict):
            chats = {}
        chats.setdefault(session_name, [])
        chats[session_name].append(message)
        ls.set_collection_item("chat_history", uid, chats)

    return _try_firestore(remote, local)


def get_chat_sessions(uid: str):
    def local():
        chats = ls.get_collection("chat_history", uid)
        return chats if isinstance(chats, dict) else {}
    return _try_firestore(
        lambda: {d.id: d.to_dict().get("messages", []) for d in _user_col(uid, "chat_sessions").stream()},
        local,
    )


def save_study_plan(uid: str, plan: dict):
    return _try_firestore(
        lambda: _user_col(uid, "meta").document("study_plan").set(plan),
        lambda: ls.set_collection_item("study_plans", uid, plan),
    )


def get_study_plan(uid: str):
    def remote():
        doc = _user_col(uid, "meta").document("study_plan").get()
        return doc.to_dict() if doc.exists else {}

    def local():
        plan = ls.get_collection("study_plans", uid)
        return plan if isinstance(plan, dict) else {}

    return _try_firestore(remote, local)
