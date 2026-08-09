"""
Top navigation bar - a full-bleed white strip with the logo on the left,
pill-style links in the middle and the user's avatar on the right.
"""

import streamlit as st

from utils.state import go_to
from utils.theme import icon, avatar_html

NAV_LINKS = [
    ("Dashboard",       ":material/dashboard:",   1.05),
    ("Notes",           ":material/description:", 0.80),
    ("Flashcards",      ":material/credit_card:", 1.05),
    ("Quiz",            ":material/help:",        0.72),
    ("AI Chat",         ":material/chat_bubble:", 0.92),
    ("Analytics",       ":material/bar_chart:",   1.00),
    ("Recommendations", ":material/lightbulb:",   1.50),
    ("Profile",         ":material/person:",      0.85),
]


def render_navbar():
    with st.container(key="navbar"):
        widths = [1.75] + [w for _, _, w in NAV_LINKS] + [0.45]
        logo_col, *nav_cols, avatar_col = st.columns(widths, vertical_alignment="center")

        with logo_col:
            st.markdown(
                f'<div class="sm-logo-row">'
                f'  <div class="sm-logo-badge">{icon("book", "#ffffff", 19)}</div>'
                f'  <div class="sm-logo-text">StudyMate AI</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        active = st.session_state.active_page
        for col, (label, micon, _) in zip(nav_cols, NAV_LINKS):
            with col:
                if st.button(
                    f"{micon} {label}",
                    key=f"nav_{label}",
                    width="stretch",
                    type="primary" if active == label else "secondary",
                ):
                    go_to(label)
                    st.rerun()

        with avatar_col:
            st.markdown(avatar_html(st.session_state.user, "sm-avatar"), unsafe_allow_html=True)
