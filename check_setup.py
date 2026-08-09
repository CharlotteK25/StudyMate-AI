"""
check_setup.py - verify every key in .streamlit/secrets.toml actually works.

Run it before a demo or after changing any credential:

    venv\\Scripts\\python check_setup.py      (Windows)
    venv/bin/python check_setup.py           (macOS/Linux)

It makes one real call per service and prints exactly what to fix. It does not
touch your app data - the Firestore test writes and deletes a single throwaway
document under the `_diagnostic` collection.
"""

import json
import pathlib
import sys

try:
    import tomllib
except ModuleNotFoundError:
    print("Python 3.11 or newer is required.")
    sys.exit(1)

SECRETS = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"

OK, WARN, BAD = "[ OK ]", "[WARN]", "[FAIL]"
problems = []


def report(level, service, message):
    print(f"{level} {service:26} {message}")
    if level != OK:
        problems.append(f"{service}: {message}")


def main():
    if not SECRETS.exists():
        print(f"{BAD} No {SECRETS} found.")
        print("      Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml "
              "and fill it in.")
        return 1

    secrets = tomllib.loads(SECRETS.read_text(encoding="utf-8"))
    print(f"Reading {SECRETS}\n")

    check_gemini(secrets)
    check_firebase_auth(secrets)
    check_firestore(secrets)
    check_google_login(secrets)

    print()
    if problems:
        print(f"{len(problems)} thing(s) need attention:")
        for p in problems:
            print(f"  - {p}")
        print("\nThe app still runs - it falls back to offline NLP and a local JSON "
              "database for anything unavailable.")
        return 1
    print("Everything checks out. Run: streamlit run app.py")
    return 0


def check_gemini(secrets):
    key = secrets.get("GEMINI_API_KEY", "")
    if not key:
        report(WARN, "Gemini", "No GEMINI_API_KEY set - AI features use offline NLP.")
        return
    try:
        from google import genai
    except ImportError:
        report(BAD, "Gemini", "google-genai not installed. Run: pip install -r requirements.txt")
        return

    from services.gemini_service import FALLBACK_MODELS
    configured = secrets.get("GEMINI_MODEL", "gemini-flash-latest")
    candidates = [configured] + [m for m in FALLBACK_MODELS if m != configured]

    client = genai.Client(api_key=key)
    failures = []
    for model in candidates:
        try:
            resp = client.models.generate_content(model=model, contents="Reply with the word OK")
            if model == configured:
                report(OK, "Gemini", f"model '{model}' responded: {resp.text.strip()[:30]!r}")
            else:
                report(WARN, "Gemini",
                       f"configured model '{configured}' is unusable ({failures[0]}), but the "
                       f"app auto-switches to '{model}', which works. AI features are fine; "
                       f"set GEMINI_MODEL = \"{model}\" to skip the wasted first call.")
            return
        except Exception as e:
            text = str(e)
            if "API_KEY_INVALID" in text or "API key not valid" in text:
                report(BAD, "Gemini", "GEMINI_API_KEY rejected. Get a new one at "
                                      "https://aistudio.google.com/apikey")
                return
            if "RESOURCE_EXHAUSTED" in text or "429" in text:
                failures.append(f"{model}: quota exhausted (free-tier limit of 0)")
            elif "NOT_FOUND" in text or "404" in text:
                failures.append(f"{model}: not available to this key")
            else:
                report(BAD, "Gemini", f"{type(e).__name__}: {text[:160]}")
                return

    report(BAD, "Gemini", "no working model. " + "; ".join(failures) +
                          ". Free-tier quota resets daily, or add billing to the key's project.")


def check_firebase_auth(secrets):
    key = secrets.get("FIREBASE_WEB_API_KEY", "")
    if not key:
        report(WARN, "Firebase Auth", "No FIREBASE_WEB_API_KEY - sign-in uses local accounts.")
        return
    import requests
    try:
        resp = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={key}",
            json={"email": "setup-probe-nonexistent@example.invalid",
                  "password": "not-a-real-password", "returnSecureToken": True},
            timeout=20)
    except requests.RequestException as e:
        report(BAD, "Firebase Auth", f"could not reach Google: {e}")
        return

    err = resp.json().get("error", {}).get("message", "")
    if err in ("EMAIL_NOT_FOUND", "INVALID_LOGIN_CREDENTIALS", "INVALID_PASSWORD"):
        report(OK, "Firebase Auth", "API key valid, Email/Password sign-in enabled.")
    elif err == "CONFIGURATION_NOT_FOUND":
        report(BAD, "Firebase Auth",
               "Authentication is not enabled for this project. Firebase Console > Build > "
               "Authentication > Get started, then enable the Email/Password provider.")
    elif err in ("OPERATION_NOT_ALLOWED", "PASSWORD_LOGIN_DISABLED"):
        report(BAD, "Firebase Auth",
               "Email/Password provider is disabled. Enable it under Authentication > "
               "Sign-in method.")
    elif "API_KEY" in err or "API key" in err:
        report(BAD, "Firebase Auth",
               "FIREBASE_WEB_API_KEY is invalid. Copy it from Project Settings > General > "
               "Web API Key.")
    else:
        report(BAD, "Firebase Auth", f"unexpected response: {err or resp.text[:160]}")


def check_firestore(secrets):
    sa = secrets.get("firebase_service_account")
    if not sa:
        report(WARN, "Firestore", "No [firebase_service_account] - data saves to "
                                  "data/local_db.json.")
        return
    project = sa.get("project_id", "?")
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        report(BAD, "Firestore", "firebase-admin not installed. Run: "
                                 "pip install -r requirements.txt")
        return

    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(dict(sa)))
        db = firestore.client()
        doc = db.collection("_diagnostic").document("setup_probe")
        doc.set({"ok": True})
        doc.delete()
        report(OK, "Firestore", f"read/write works on project '{project}'.")
    except Exception as e:
        text = str(e)
        if "SERVICE_DISABLED" in text or "has not been used in project" in text:
            report(BAD, "Firestore",
                   f"Cloud Firestore is not enabled for project '{project}'. Firebase Console "
                   f"> Build > Firestore Database > Create database (start in test mode).")
        elif "PERMISSION_DENIED" in text:
            report(BAD, "Firestore",
                   f"permission denied on '{project}' - check the database security rules.")
        elif "invalid_grant" in text or "Invalid JWT" in text:
            report(BAD, "Firestore",
                   "the service-account private_key is malformed. Re-copy it from the "
                   "downloaded JSON, keeping the \\n escapes intact.")
        else:
            report(BAD, "Firestore", f"{type(e).__name__}: {text[:200]}")


def check_google_login(secrets):
    auth = secrets.get("auth")
    if not auth:
        report(WARN, "Sign in with Google", "No [auth] block - the Google button is disabled.")
        return

    google = auth.get("google")
    client_id = (google or {}).get("client_id") or auth.get("client_id")
    if not client_id:
        report(BAD, "Sign in with Google",
               "[auth] has no client_id. The app calls st.login(\"google\"), so put "
               "client_id/client_secret under an [auth.google] section.")
        return
    if not google:
        report(WARN, "Sign in with Google",
               "client_id sits directly under [auth], but the app calls st.login(\"google\") "
               "which needs an [auth.google] section. Move it.")
        return

    missing = [f for f in ("redirect_uri", "cookie_secret") if not auth.get(f)]
    if missing:
        report(BAD, "Sign in with Google", f"[auth] is missing: {', '.join(missing)}")
        return
    if not google.get("client_secret"):
        report(BAD, "Sign in with Google", "[auth.google] is missing client_secret.")
        return
    try:
        import authlib
    except ImportError:
        report(BAD, "Sign in with Google", "Authlib not installed. Run: "
                                           "pip install -r requirements.txt")
        return
    report(OK, "Sign in with Google",
           f"configured; redirect_uri = {auth['redirect_uri']} "
           f"(this exact URI must be listed in Google Cloud Console).")


if __name__ == "__main__":
    sys.exit(main())
