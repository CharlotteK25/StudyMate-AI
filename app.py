"""
StudyMate AI — Final Year Project
Entry point for the Streamlit application (serves as both the "website"
and, when opened in a mobile browser or wrapped by a tool like PWABuilder/
Streamlit's own mobile-friendly layout, the "app").

Run with:
    streamlit run app.py
"""

import streamlit as st

from utils.state import init_session_state, go_to
from utils.theme import inject_theme, inject_page_css
from utils.navbar import render_navbar
from services import firebase_service as fb
from services import gemini_service as gem

from pages_app.auth import render_auth
from pages_app.dashboard import render_dashboard
from pages_app.notes import render_notes
from pages_app.flashcards import render_flashcards
from pages_app.quiz import render_quiz
from pages_app.chat import render_chat
from pages_app.analytics import render_analytics
from pages_app.recommendations import render_recommendations
from pages_app.profile import render_profile

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="🦉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session_state()
inject_theme()
inject_page_css()

PAGE_RENDERERS = {
    "Dashboard": render_dashboard,
    "Notes": render_notes,
    "Flashcards": render_flashcards,
    "Quiz": render_quiz,
    "AI Chat": render_chat,
    "Analytics": render_analytics,
    "Recommendations": render_recommendations,
    "Profile": render_profile,
}


def _sync_google_login():
    """If the person just completed Streamlit's native Google OIDC login
    (st.login("google")), st.user.is_logged_in becomes True in a fresh
    session. Bridge that into our own app-level session state/user record."""
    try:
        logged_in = st.user.is_logged_in
    except Exception:
        logged_in = False

    if logged_in and not st.session_state.authed:
        email = st.user.get("email", "")
        name = st.user.get("name") or (email.split("@")[0] if email else "Google User")
        ok, result = fb.get_or_create_oidc_user(name, email)
        if ok:
            st.session_state.authed = True
            st.session_state.user = result
            go_to("Dashboard")


def main():
    _sync_google_login()

    if not st.session_state.authed:
        render_auth()
        return

    render_navbar()
    gem.render_notice()
    fb.render_notice()
    renderer = PAGE_RENDERERS.get(st.session_state.active_page, render_dashboard)
    renderer()


if __name__ == "__main__":
    main()
