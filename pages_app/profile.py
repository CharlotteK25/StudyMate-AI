"""Profile - account sidebar, editable fields, goals, notifications, danger zone."""

import base64
import io

import streamlit as st

from services import firebase_service as fb
from services import gemini_service as gem
from utils.theme import flat, icon, pill, card, card_heading, avatar_html, PRIMARY_DARK

NAV = [
    ("Account",       "Profile & security", ":material/person:"),
    ("Goals",         "Study targets",      ":material/target:"),
    ("Notifications", "Alerts & reminders", ":material/notifications:"),
]

PROFILE_CSS = """
<style>
.sm-prof-name  { font-size: 1.05rem !important; font-weight: 700 !important; color: #111827;
                 margin: 12px 0 2px 0 !important; text-align: center; }
.sm-prof-email { font-size: 12.5px !important; color: #9ca3af; margin: 0 0 10px 0 !important;
                 text-align: center; }
.st-key-card_profnav { padding: 18px 14px !important; }
.sm-cam {
    position: absolute; right: -4px; bottom: -4px; width: 26px; height: 26px;
    border-radius: 50%; background: #22c55e; border: 2px solid #fff;
    display: flex; align-items: center; justify-content: center;
}
.st-key-photo_upl [data-testid="stFileUploaderDropzone"] {
    padding: 7px 12px !important; min-height: auto !important;
    background: #f8fafc !important; border: 1px dashed #d1d5db !important;
    border-radius: 10px !important;
}
.st-key-photo_upl [data-testid="stFileUploaderDropzoneInstructions"] small { display: none; }
.st-key-photo_upl [data-testid="stFileUploaderDropzone"] button {
    padding: 5px 14px !important; font-size: 12.5px !important;
    background: #ffffff !important; border: 1px solid #e5e7eb !important;
    border-radius: 8px !important; color: #374151 !important;
}
.st-key-btn_ghost_rmphoto div.stButton > button {
    background: none !important; border: none !important; box-shadow: none !important;
    color: #9ca3af !important; font-size: 12px !important; padding: 0 !important;
}
.st-key-btn_ghost_rmphoto div.stButton > button:hover { color: #dc2626 !important; }
</style>
"""


def _process_photo(f):
    # crop to a centred square, shrink to 256px and re-encode as jpeg so the
    # stored data URI stays small enough for a Firestore document
    try:
        from PIL import Image, ImageOps
        img = Image.open(f)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        side = min(img.size)
        left = (img.width - side) // 2
        top = (img.height - side) // 2
        img = img.crop((left, top, left + side, top + side)).resize((256, 256), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=85)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def _field(label: str, value: str, key: str, secret: bool = False):
    editing = st.session_state.get(f"edit_{key}", False)
    st.markdown(f'<p class="sm-label" style="margin-top:16px;">{label}</p>', unsafe_allow_html=True)

    if editing:
        col_a, col_b = st.columns([4, 1], vertical_alignment="bottom")
        with col_a:
            new = st.text_input(label, value="" if secret else value, key=f"in_{key}",
                                label_visibility="collapsed",
                                type="password" if secret else "default")
        with col_b:
            with st.container(key=f"btn_green_save_{key}"):
                if st.button("Save", key=f"sv_{key}", width="stretch"):
                    if new and not secret:
                        st.session_state.user[key] = new
                    st.session_state[f"edit_{key}"] = False
                    st.rerun()
    else:
        col_a, col_b = st.columns([4, 1], vertical_alignment="center")
        with col_a:
            shown = "&#8226;" * 8 if secret else value
            st.markdown(flat(f'<div class="sm-field-box"><span>{shown}</span></div>'),
                        unsafe_allow_html=True)
        with col_b:
            with st.container(key=f"btn_ghost_edit_{key}"):
                if st.button("Edit", key=f"ed_{key}", width="stretch"):
                    st.session_state[f"edit_{key}"] = True
                    st.rerun()


def render_profile():
    user = st.session_state.user
    st.markdown(PROFILE_CSS, unsafe_allow_html=True)

    initials = "".join(p[0] for p in user["name"].split()[:2]).upper() or "?"
    active = st.session_state.setdefault("profile_tab", "Account")

    side, main = st.columns([1, 3], gap="medium")

    with side:
        with card("profnav"):
            st.markdown(flat(avatar_html(user)), unsafe_allow_html=True)
            st.markdown(f'<p class="sm-prof-name">{user["name"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="sm-prof-email">{user["email"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center;">{pill("Student")}</div>',
                        unsafe_allow_html=True)
            st.markdown('<div style="height:1px;background:#f1f3f4;margin:16px 0;"></div>',
                        unsafe_allow_html=True)

            for label, sub, micon in NAV:
                with st.container(key=f"pnav_{label}"):
                    if st.button(f"{micon} {label}", key=f"pn_{label}", width="stretch",
                                 type="primary" if active == label else "secondary"):
                        st.session_state.profile_tab = label
                        st.rerun()
                st.markdown(f'<p class="sm-file-size" style="margin:-8px 0 6px 44px;">{sub}</p>',
                            unsafe_allow_html=True)

            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
            with st.container(key="btn_red_logout"):
                if st.button("Log Out", width="stretch", icon=":material/logout:"):
                    st.session_state.authed = False
                    st.session_state.user = None
                    st.session_state.auth_mode = "signin"
                    st.rerun()

    with main:
        sub = next(s for l, s, _ in NAV if l == active)
        st.markdown(f'<p class="sm-title">{active}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="sm-subtitle">{sub}</p>', unsafe_allow_html=True)
        st.write("")

        if active == "Account":
            _account_panel(user, initials)
            st.write("")
            _connection_panel()
        elif active == "Goals":
            _goals_panel()
        else:
            _notifications_panel()


def _account_panel(user, initials):
    with card("profile"):
        st.markdown('<p class="sm-sec-title">Profile</p>', unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:#f1f3f4;margin:14px 0 18px 0;"></div>',
                    unsafe_allow_html=True)

        a_l, a_r = st.columns([1, 5], vertical_alignment="center")
        with a_l:
            st.markdown(flat(f'<div style="position:relative;width:84px;">'
                             f'{avatar_html(user)}'
                             f'<div class="sm-cam">{icon("upload", "#ffffff", 13)}</div></div>'),
                        unsafe_allow_html=True)
        with a_r:
            st.markdown(f'<p class="sm-file-name" style="font-size:15px;font-weight:600;">'
                        f'{user["name"]}</p>', unsafe_allow_html=True)
            with st.container(key="photo_upl"):
                up = st.file_uploader("Profile photo", type=["png", "jpg", "jpeg", "webp"],
                                      key="profile_photo", label_visibility="collapsed")
            if up is not None:
                sig = (up.name, up.size)
                if st.session_state.get("_photo_sig") != sig:
                    st.session_state["_photo_sig"] = sig
                    data_uri = _process_photo(up)
                    if data_uri:
                        st.session_state.user["photo"] = data_uri
                        fb.update_profile(user["uid"], user["email"], {"photo": data_uri})
                        st.toast("Profile photo updated.")
                        st.rerun()
                    else:
                        st.error("Couldn't read that image - try a JPG or PNG.")
            if user.get("photo"):
                with st.container(key="btn_ghost_rmphoto"):
                    if st.button("Remove photo", key="rm_photo"):
                        st.session_state.user.pop("photo", None)
                        fb.update_profile(user["uid"], user["email"], {"photo": ""})
                        st.session_state.pop("_photo_sig", None)
                        st.rerun()

        _field("Full name", user["name"], "name")
        _field("Email address", user["email"], "email")
        _field("Password", "", "password", secret=True)

    st.write("")
    with card("danger"):
        st.markdown('<p class="sm-sec-title">Danger Zone</p>', unsafe_allow_html=True)
        st.markdown('<div style="height:1px;background:#f1f3f4;margin:14px 0 16px 0;"></div>',
                    unsafe_allow_html=True)
        st.markdown('<p class="sm-file-size" style="margin-bottom:14px;">Permanent actions that '
                    'cannot be undone. Please proceed with caution.</p>', unsafe_allow_html=True)

        d_l, d_r = st.columns([4, 1], vertical_alignment="center")
        with d_l:
            st.markdown(flat('<div class="sm-danger-row"><div><h5>Delete Account</h5>'
                             '<p>All data will be permanently removed</p></div></div>'),
                        unsafe_allow_html=True)
        with d_r:
            with st.container(key="btn_red_delete"):
                if st.button("Delete", width="stretch", icon=":material/delete:"):
                    st.session_state.confirm_del = True
        if st.session_state.get("confirm_del"):
            st.warning("Account deletion isn't wired to a backend in this build. "
                       "Implement `fb.delete_account(uid)` to complete it.")


def _connection_panel():
    """Live view of whether Gemini and Firebase are actually connected. Without
    this the app looks identical whether the keys work or not."""
    with card("connections"):
        card_heading("Service connections", "Gemini and Firebase status for this session")

        for label, (ok, message) in [("Google Gemini", gem.status()),
                                     ("Firebase", fb.status())]:
            st.markdown(
                f'<p style="margin:10px 0 2px 0;font-weight:600;color:#111827;">'
                f'{"🟢" if ok else "🟠"} {label}</p>',
                unsafe_allow_html=True,
            )
            st.caption(message)

        google_ok = fb.GOOGLE_LOGIN_CONFIGURED
        st.markdown(
            f'<p style="margin:10px 0 2px 0;font-weight:600;color:#111827;">'
            f'{"🟢" if google_ok else "🟠"} Sign in with Google</p>',
            unsafe_allow_html=True,
        )
        st.caption("OAuth client configured under [auth.google]." if google_ok
                   else "Add [auth.google] with client_id/client_secret to secrets.toml.")

        st.caption("Run `python check_setup.py` in the project folder for a full diagnosis.")


def _goals_panel():
    with card("goals"):
        card_heading("Study Targets", "Set the pace you want to keep")
        hours = st.slider("Daily study goal (hours)", 1, 8,
                          st.session_state.get("study_goal_hours", 3), key="goal_hours")
        weekly = st.slider("Quizzes per week", 1, 20, 5, key="goal_quizzes")
        with st.container(key="btn_dark_savegoals"):
            if st.button("Save goals", width="stretch"):
                st.session_state.study_goal_hours = hours
                st.toast(f"Goal set: {hours}h a day, {weekly} quizzes a week.")


def _notifications_panel():
    with card("notifs"):
        card_heading("Alerts & Reminders", "Choose what StudyMate tells you about")
        for label, default in [("Daily study reminder", True),
                               ("Streak at risk", True),
                               ("New AI recommendation", False),
                               ("Weekly progress summary", True)]:
            st.toggle(label, value=default, key=f"notif_{label}")
