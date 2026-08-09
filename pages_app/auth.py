"""
Sign in / Sign up / Forgot password.

Self-contained: all styling and markup for this page lives here in Python
(no external .css/.html files needed), so the layout matches the Figma
mock - white form card on the left, mint promo panel with the owl on the
right, joined into a single rounded shell.
"""

import streamlit as st

from services import firebase_service as fb
from utils.state import go_to
from utils.theme import OWL_SVG, icon, flat

AUTH_CSS = """
<style>
/* Auth page background - soft mint-to-blue wash */
.stApp { background: linear-gradient(135deg, #f0fdf4 0%, #f7fbf9 45%, #eef5fb 100%); }

/* Shell that holds the two halves, centred and capped in width */
.st-key-auth_shell { max-width: 1080px !important; margin: 3vh auto 0 auto !important; }
.st-key-auth_shell div[data-testid="stHorizontalBlock"] { gap: 0 !important; align-items: stretch; }
.st-key-auth_shell div[data-testid="stVerticalBlock"] { gap: 0.4rem; }
/* nested rows inside the card still need breathing room */
.st-key-login_card div[data-testid="stHorizontalBlock"] { gap: 1rem !important; }

/* Left half - the white form card */
.st-key-login_card {
    background: #ffffff;
    border-radius: 22px 0 0 22px;
    padding: 42px 46px 38px 46px;
    box-shadow: 0 18px 45px rgba(16,24,40,0.07);
    min-height: 660px;
}

/* Right half - mint promo panel */
.sm-promo {
    background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%);
    border-radius: 0 22px 22px 0;
    padding: 46px 34px;
    min-height: 660px;
    position: relative;
    overflow: hidden;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 30px;
    box-shadow: 0 18px 45px rgba(16,24,40,0.05);
}
.sm-promo-blob { position: absolute; border-radius: 50%; }
.sm-promo-blob.a { top: 30px;  right: 34px; width: 140px; height: 140px; background: rgba(74,222,128,0.13); }
.sm-promo-blob.b { bottom: 46px; left: 26px; width: 92px;  height: 92px;  background: rgba(96,165,250,0.13); }
.sm-promo-blob.c { top: 36%;   right: 16px; width: 34px;  height: 34px;  background: rgba(244,114,182,0.16); }

.sm-owl-wrap { position: relative; z-index: 2; }
.sm-owl-tile {
    width: 178px; height: 178px; border-radius: 26px; background: #ffffff;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 14px 34px rgba(74,222,128,0.22);
}
.sm-float-badge {
    position: absolute; background: #ffffff; border-radius: 11px;
    padding: 6px 10px; box-shadow: 0 6px 16px rgba(16,24,40,0.12);
    border: 1px solid rgba(0,0,0,0.06);
    display: flex; align-items: center; gap: 6px;
    font-size: 10.5px; font-weight: 600; color: #374151; white-space: nowrap;
}
.sm-float-badge.top    { top: -12px; right: -30px; }
.sm-float-badge.bottom { bottom: -12px; left: -34px; }

.sm-promo-copy { text-align: center; max-width: 300px; position: relative; z-index: 2; }
.sm-promo-copy h2 { color: #1f2937; font-size: 1.42rem; font-weight: 700; margin: 0; letter-spacing: -0.01em; }
.sm-promo-copy p  { color: #6b7280; font-size: 0.88rem; margin-top: 9px; line-height: 1.6; }

.sm-proof { display: flex; flex-direction: column; align-items: center; gap: 8px; position: relative; z-index: 2; }
.sm-proof-avatars { display: flex; }
.sm-proof-avatars div {
    width: 28px; height: 28px; border-radius: 50%; border: 2px solid #ffffff;
    display: flex; align-items: center; justify-content: center;
    font-size: 9px; font-weight: 700; color: #ffffff; margin-left: -7px;
}
.sm-proof-avatars div:first-child { margin-left: 0; }
.sm-proof p { font-size: 10.5px; color: #9ca3af; margin: 0; }
.sm-proof p b { color: #4b5563; }

/* Logo lockup */
.sm-auth-logo-row { display: flex; align-items: center; gap: 11px; margin-bottom: 26px; }
.sm-auth-logo-badge {
    width: 44px; height: 44px; border-radius: 13px; background: #4ade80;
    display: flex; align-items: center; justify-content: center;
}
.sm-auth-logo-text { font-weight: 700; color: #111827; font-size: 1.18rem; letter-spacing: -0.01em; }

/* Headings + field labels */
.sm-auth-title    { font-size: 1.78rem !important; font-weight: 700 !important; color: #111827;
                    margin: 0 !important; letter-spacing: -0.025em; line-height: 1.25 !important; }
.sm-auth-subtitle { color: #9ca3af; font-size: 0.95rem !important; margin: 10px 0 26px 0 !important; }
.st-key-login_card label p {
    font-size: 11.5px !important; letter-spacing: 0.06em; text-transform: uppercase;
    color: #6b7280 !important; font-weight: 600 !important;
}

/* Inputs */
.st-key-login_card .stTextInput > div,
.st-key-login_card div[data-baseweb="input"],
.st-key-login_card [data-testid="stTextInputRootElement"] {
    border-radius: 11px !important;
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
}
.st-key-login_card .stTextInput input,
.st-key-login_card div[data-baseweb="base-input"] {
    background: #ffffff !important;
    border: none !important;
    padding: 10px 6px !important;
}
.st-key-login_card .stTextInput > div:focus-within,
.st-key-login_card div[data-baseweb="input"]:focus-within,
.st-key-login_card [data-testid="stTextInputRootElement"]:focus-within {
    border-color: #4ade80 !important;
    box-shadow: 0 0 0 3px rgba(74,222,128,0.16) !important;
}
/* icons sitting inside the field */
.st-key-login_card .stTextInput [data-testid="stIconMaterial"] { color: #9ca3af; font-size: 19px !important; }

/* Google button - white, bordered, same radius as the inputs */
.st-key-google_btn div.stButton > button {
    background: #ffffff; color: #111827; border: 1px solid #e5e7eb;
    border-radius: 11px; font-weight: 500; font-size: 14.5px; padding: 13px 0;
    box-shadow: none;
}
.st-key-google_btn div.stButton > button:hover { background: #f9fafb; border-color: #d1d5db; color: #111827; }

/* Primary submit - dark pill-rectangle */
.st-key-submit_btn div.stButton > button {
    background: #111827; color: #ffffff; border: none; border-radius: 11px;
    font-weight: 600; font-size: 15px; padding: 14px 0;
}
.st-key-submit_btn div.stButton > button:hover { background: #1f2937; color: #ffffff; }

/* Ghost text links */
[class*="st-key-link_"] div.stButton > button {
    background: none; border: none; box-shadow: none; padding: 0;
    color: #6b7280; font-weight: 500; font-size: 13px;
}
[class*="st-key-link_"] div.stButton > button:hover { color: #16a34a; background: none; }
.st-key-link_switch div.stButton > button { color: #16a34a; font-weight: 700; font-size: 14.5px; }

/* "or continue with email" divider */
.sm-divider { display: flex; align-items: center; gap: 14px; margin: 22px 0 20px 0; }
.sm-divider span { color: #6b7280; font-size: 13px; font-weight: 500; white-space: nowrap; }
.sm-divider i { flex: 1; height: 1px; background: #e5e7eb; }

.sm-footer-text { text-align: right; font-size: 14px; color: #6b7280; margin: 0 !important; }

/* Google's multi-colour G, painted into the button label */
.st-key-google_btn div.stButton > button p::before {
    content: ""; display: inline-block; width: 18px; height: 18px;
    margin-right: 10px; vertical-align: -4px;
    background-size: contain; background-repeat: no-repeat;
    background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 18 18'%3E%3Cpath fill='%234285F4' d='M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 01-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z'/%3E%3Cpath fill='%2334A853' d='M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 009 18z'/%3E%3Cpath fill='%23FBBC05' d='M3.97 10.72A5.4 5.4 0 013.68 9c0-.6.1-1.17.28-1.71V4.96H.96A9 9 0 000 9c0 1.45.35 2.83.96 4.04l3.01-2.32z'/%3E%3Cpath fill='%23EA4335' d='M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.59C13.46.89 11.43 0 9 0A9 9 0 00.96 4.96l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z'/%3E%3C/svg%3E");
}
</style>
"""

PROMO_COPY = {
    "signin": ("Welcome back!",
               "Pick up where you left off. Your notes, flashcards, and progress are all waiting."),
    "signup": ("Start learning smarter.",
               "Join thousands of students using AI to study faster and score higher."),
    "forgot": ("No worries!",
               "It happens to the best of us. We'll send a reset link to your inbox in seconds."),
}

PROOF_AVATARS = [("JA", "#4ade80"), ("KM", "#60a5fa"), ("PL", "#f472b6"),
                 ("RS", "#fb923c"), ("TW", "#a78bfa")]


def _promo_panel(mode: str) -> str:
    headline, body = PROMO_COPY[mode]
    avatars = "".join(
        f'<div style="background:{color};">{initials}</div>' for initials, color in PROOF_AVATARS
    )
    return flat(f"""
    <div class="sm-promo">
        <div class="sm-promo-blob a"></div>
        <div class="sm-promo-blob b"></div>
        <div class="sm-promo-blob c"></div>

        <div class="sm-owl-wrap">
            <div class="sm-owl-tile">{OWL_SVG}</div>
            <div class="sm-float-badge top">&#127942; 44-day streak</div>
            <div class="sm-float-badge bottom">&#128218; 1,031 sessions</div>
        </div>

        <div class="sm-promo-copy">
            <h2>{headline}</h2>
            <p>{body}</p>
        </div>

        <div class="sm-proof">
            <div class="sm-proof-avatars">{avatars}</div>
            <p>Joined by <b>12,000+</b> students</p>
        </div>
    </div>
    """)


def _google_button():
    """White 'Continue with Google' button - the multi-colour G is drawn by CSS."""
    with st.container(key="google_btn"):
        return st.button("Continue with Google", key="google_login_btn", width="stretch")


def _handle_google_click():
    if fb.GOOGLE_LOGIN_CONFIGURED:
        st.login("google")
    else:
        st.warning(
            "Google Sign-In isn't configured yet. Add an `[auth]` block with your Google "
            "OAuth client credentials to `.streamlit/secrets.toml` - see SETUP.md.",
            icon=":material/warning:",
        )


def render_auth():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    mode = st.session_state.auth_mode

    with st.container(key="auth_shell"):
        left, right = st.columns([1.12, 1])

        with left:
            with st.container(key="login_card"):
                st.markdown(
                    f'<div class="sm-auth-logo-row">'
                    f'  <div class="sm-auth-logo-badge">{icon("book", "#ffffff", 22)}</div>'
                    f'  <div class="sm-auth-logo-text">StudyMate AI</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if mode == "forgot":
                    _render_forgot()
                elif mode == "signup":
                    _render_signup()
                else:
                    _render_signin()

        with right:
            st.markdown(_promo_panel(mode), unsafe_allow_html=True)


def _render_signin():
    st.markdown('<p class="sm-auth-title">Sign in to your account</p>', unsafe_allow_html=True)
    st.markdown('<p class="sm-auth-subtitle">Welcome back &mdash; your dashboard is waiting.</p>',
                unsafe_allow_html=True)

    if _google_button():
        _handle_google_click()

    st.markdown('<div class="sm-divider"><i></i><span>or continue with email</span><i></i></div>',
                unsafe_allow_html=True)

    email = st.text_input("Email address", placeholder="you@university.edu",
                          key="auth_email", icon=":material/mail:")
    password = st.text_input("Password", type="password", placeholder="Enter your password",
                             key="auth_password", icon=":material/lock:")

    _, link_col = st.columns([1, 0.42])
    with link_col:
        with st.container(key="link_forgot"):
            if st.button("Forgot password?", key="forgot_link", width="stretch"):
                st.session_state.auth_mode = "forgot"
                st.rerun()

    with st.container(key="submit_btn"):
        if st.button("Sign In  :material/arrow_forward:", type="primary",
                     width="stretch", key="signin_submit"):
            if not email or not password:
                st.error("Enter your email and password to continue.")
            else:
                ok, result = fb.sign_in(email, password)
                if ok:
                    st.session_state.authed = True
                    st.session_state.user = result
                    go_to("Dashboard")
                    st.rerun()
                else:
                    st.error(result)

    _mode_switch_row("Don't have an account?", "Sign Up", "signup", "go_signup")
    _local_mode_note()


def _render_signup():
    st.markdown('<p class="sm-auth-title">Create your account</p>', unsafe_allow_html=True)
    st.markdown('<p class="sm-auth-subtitle">Free forever. No credit card required.</p>',
                unsafe_allow_html=True)

    if _google_button():
        _handle_google_click()

    st.markdown('<div class="sm-divider"><i></i><span>or continue with email</span><i></i></div>',
                unsafe_allow_html=True)

    name = st.text_input("Full name", placeholder="Jamie Anderson",
                         key="signup_name", icon=":material/person:")
    email = st.text_input("Email address", placeholder="you@university.edu",
                          key="auth_email", icon=":material/mail:")
    password = st.text_input("Password", type="password", placeholder="Min. 8 characters",
                             key="auth_password", icon=":material/lock:")
    st.write("")

    with st.container(key="submit_btn"):
        if st.button("Create Account  :material/arrow_forward:", type="primary",
                     width="stretch", key="signup_submit"):
            if not name or not email or not password:
                st.error("Fill in every field to create your account.")
            elif len(password) < 8:
                st.error("Passwords need at least 8 characters.")
            else:
                ok, result = fb.sign_up(name, email, password)
                if ok:
                    st.session_state.authed = True
                    st.session_state.user = result
                    go_to("Dashboard")
                    st.rerun()
                else:
                    st.error(result)

    _mode_switch_row("Already have an account?", "Sign In", "signin", "go_signin")
    _local_mode_note()


def _render_forgot():
    st.markdown('<p class="sm-auth-title">Reset your password</p>', unsafe_allow_html=True)
    st.markdown('<p class="sm-auth-subtitle">Enter your email and we\'ll send you a reset link.</p>',
                unsafe_allow_html=True)

    email = st.text_input("Email address", placeholder="you@university.edu",
                          key="forgot_email", icon=":material/mail:")
    st.write("")

    with st.container(key="submit_btn"):
        if st.button("Send Reset Link  :material/arrow_forward:", type="primary",
                     width="stretch", key="forgot_submit"):
            if not email:
                st.error("Enter the email address on your account.")
            elif fb.send_password_reset(email):
                st.success(f"Reset link sent to {email}. Check your inbox.")
            else:
                st.error("No account found with that email address.")

    st.write("")
    with st.container(key="link_back"):
        if st.button(":material/arrow_back: Back to sign in", key="back_signin",
                     width="stretch"):
            st.session_state.auth_mode = "signin"
            st.rerun()


def _mode_switch_row(prompt: str, action: str, target_mode: str, key: str):
    st.write("")
    text_col, btn_col = st.columns([1.35, 1], vertical_alignment="center")
    with text_col:
        st.markdown(f'<div class="sm-footer-text">{prompt}</div>', unsafe_allow_html=True)
    with btn_col:
        with st.container(key="link_switch"):
            if st.button(action, key=key):
                st.session_state.auth_mode = target_mode
                st.rerun()


def _local_mode_note():
    ok, message = fb.status()
    if not ok:
        st.caption(f"Local demo mode - accounts save to this machine. {message}")
