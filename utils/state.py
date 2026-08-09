"""
Central session-state initialisation, mirroring the React app's useState hooks
(authed, activeLink, uploaded files, flashcards, quiz progress, chat history).
"""

import streamlit as st
import uuid
from datetime import date


def init_session_state():
    defaults = {
        "authed": False,
        "auth_mode": "signin",
        "user": None,
        "active_page": "Dashboard",
        "notes": [],
        "flashcard_decks": {},
        "quiz_state": {},
        "quiz_history": [],
        "chat_sessions": {"New Chat": []},
        "active_chat": "New Chat",
        "recommendations_cache": [],
        "study_goal_hours": 3,
        "study_hours_today": 2,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def new_id() -> str:
    return uuid.uuid4().hex[:10]


def today_str() -> str:
    return date.today().strftime("%b %d, %Y")


def go_to(page_label: str):
    """Navigate to a page - used by every nav button/link in the app."""
    st.session_state.active_page = page_label
