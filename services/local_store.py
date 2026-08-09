"""
Lightweight local JSON-file 'database' used as a drop-in fallback for
Firebase Firestore when the app is run without Firebase credentials
(e.g. during development, demos, or marking). Lets every feature of the
app work out of the box.

Swap this out entirely once Firebase is configured — firebase_service.py
automatically prefers real Firestore when secrets are present.
"""

import json
import os
import threading
from pathlib import Path

_LOCK = threading.Lock()
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DB_FILE = _DATA_DIR / "local_db.json"

_DEFAULT_DB = {
    "users": {},
    "notes": {},
    "flashcards": {},
    "quiz_results": {},
    "chat_history": {},
    "study_plans": {},
}


def _ensure_db():
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _DB_FILE.exists():
        _DB_FILE.write_text(json.dumps(_DEFAULT_DB, indent=2))


def _read() -> dict:
    _ensure_db()
    with _LOCK:
        with open(_DB_FILE, "r") as f:
            return json.load(f)


def _write(db: dict):
    _ensure_db()
    with _LOCK:
        with open(_DB_FILE, "w") as f:
            json.dump(db, f, indent=2)


def get_collection(name: str, uid: str = None):
    db = _read()
    coll = db.get(name, {})
    if uid is None:
        return coll
    return coll.get(uid, [] if name != "study_plans" else {})


def set_collection_item(name: str, uid: str, value):
    db = _read()
    if name not in db:
        db[name] = {}
    db[name][uid] = value
    _write(db)


def append_item(name: str, uid: str, item):
    db = _read()
    if name not in db:
        db[name] = {}
    db[name].setdefault(uid, [])
    db[name][uid].append(item)
    _write(db)


def get_user_by_email(email: str):
    db = _read()
    return db["users"].get(email.lower())


def save_user(email: str, record: dict):
    db = _read()
    db["users"][email.lower()] = record
    _write(db)
