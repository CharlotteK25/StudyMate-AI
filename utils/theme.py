"""
Central theming for the StudyMate AI Streamlit app.

Reproduces the Figma design (mint-green / white, rounded cards, pill nav,
soft shadows) using CSS injected into Streamlit, plus small HTML helpers
for the pieces that need pixel-level control beyond native widgets.

Everything the UI needs lives in this file - no external .css/.html assets
are required any more, so the app is pure Python.
"""

import html as _html
import re
import streamlit as st
from contextlib import contextmanager

PRIMARY = "#4ade80"
PRIMARY_MID = "#22c55e"
PRIMARY_DARK = "#16a34a"
PRIMARY_DEEP = "#15803d"
PRIMARY_SOFT = "#f0fdf4"
PRIMARY_PILL = "#dcfce7"

BLUE = "#3b82f6"
BLUE_SOFT = "#dbeafe"
PURPLE = "#a78bfa"
PURPLE_SOFT = "#f3e8ff"
ORANGE = "#fb923c"
ORANGE_SOFT = "#ffedd5"
PINK = "#f472b6"

INK = "#111827"
BODY = "#4b5563"
TEXT_MUTED = "#9ca3af"
BG = "#f7f8f9"
LINE = "rgba(0,0,0,0.07)"

def _svg(paths: str, color: str, size: int = 19, fill: str = "none") -> str:
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{paths}</svg>'
    )


ICON_PATHS = {
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/>'
            '<polyline points="15 2 15 7 20 7"/><line x1="8" y1="13" x2="16" y2="13"/>'
            '<line x1="8" y1="17" x2="13" y2="17"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/>'
            '<line x1="2" y1="10" x2="22" y2="10"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
              '<polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
    "brain": '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>'
             '<path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/>'
              '<polyline points="2 12 12 17 22 12"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/>'
              '<circle cx="12" cy="12" r="2"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "trend": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "sparkle": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/>',
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
            '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/>'
            '<path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "arrow": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    "copy": '<rect x="9" y="9" width="13" height="13" rx="2"/>'
            '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    "thumb_up": '<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8'
                'A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 '
                '1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>',
    "thumb_down": '<path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8'
                  'A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 '
                  '1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"/>',
    "rotate": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
    "menu": '<line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="12" y2="12"/>'
            '<line x1="4" x2="20" y1="18" y2="18"/>',
    "chevron_down": '<path d="m6 9 6 6 6-6"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z" '
            'opacity="0"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 '
            '2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 '
            '0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-'
            '2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09'
            'a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83'
            'l.06.06a1.65 1.65 0 0 0 1.82.33h.01a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09'
            'a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83'
            'l-.06.06a1.65 1.65 0 0 0-.33 1.82v.01a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4'
            'h-.09a1.65 1.65 0 0 0-1.51 1Z"/>',
}


def icon(name: str, color: str = INK, size: int = 19) -> str:
    """Return an inline SVG string for one of the named icons."""
    return _svg(ICON_PATHS[name], color, size)


OWL_SVG = """<svg width="104" height="104" viewBox="0 0 100 100" fill="none">
  <ellipse cx="50" cy="62" rx="28" ry="30" fill="#4ade80"/>
  <ellipse cx="50" cy="68" rx="16" ry="18" fill="#f0fdf4"/>
  <circle cx="50" cy="38" r="24" fill="#4ade80"/>
  <polygon points="32,20 26,6 38,14" fill="#22c55e"/>
  <polygon points="68,20 74,6 62,14" fill="#22c55e"/>
  <circle cx="40" cy="36" r="9" fill="white"/>
  <circle cx="60" cy="36" r="9" fill="white"/>
  <circle cx="41" cy="37" r="5.5" fill="#1e293b"/>
  <circle cx="61" cy="37" r="5.5" fill="#1e293b"/>
  <circle cx="43" cy="34.5" r="2" fill="white"/>
  <circle cx="63" cy="34.5" r="2" fill="white"/>
  <polygon points="50,44 45,49 55,49" fill="#fb923c"/>
  <ellipse cx="24" cy="62" rx="10" ry="16" fill="#22c55e" transform="rotate(-15 24 62)"/>
  <ellipse cx="76" cy="62" rx="10" ry="16" fill="#22c55e" transform="rotate(15 76 62)"/>
  <ellipse cx="40" cy="91" rx="8" ry="3.5" fill="#22c55e"/>
  <ellipse cx="60" cy="91" rx="8" ry="3.5" fill="#22c55e"/>
  <rect x="32" y="16" width="36" height="5" rx="2" fill="#1e293b"/>
  <polygon points="50,8 68,18 32,18" fill="#1e293b"/>
  <line x1="68" y1="18" x2="72" y2="28" stroke="#1e293b" stroke-width="2"/>
  <circle cx="72" cy="30" r="3" fill="#fb923c"/>
</svg>
"""

GOOGLE_G_SVG = """
<svg width="18" height="18" viewBox="0 0 18 18">
  <path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 01-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z"/>
  <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 009 18z"/>
  <path fill="#FBBC05" d="M3.97 10.72A5.4 5.4 0 013.68 9c0-.6.1-1.17.28-1.71V4.96H.96A9 9 0 000 9c0 1.45.35 2.83.96 4.04l3.01-2.32z"/>
  <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.59C13.46.89 11.43 0 9 0A9 9 0 00.96 4.96l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z"/>
</svg>
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp,
.stApp p, .stApp span, .stApp div, .stApp label,
.stApp input, .stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}
/* ...but never override the icon font, or ligatures render as raw words */
.stApp [data-testid="stIconMaterial"],
.stApp span[translate="no"],
.stApp [class*="material-symbols"],
.stApp .material-symbols-rounded {
    font-family: 'Material Symbols Rounded' !important;
}

.stApp { background-color: #f7f8f9; overflow-x: hidden; }

#MainMenu, footer { visibility: hidden; height: 0; }
header[data-testid="stHeader"] { display: none !important; }

div.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem;
    max-width: 1340px;
}

/* Tighten Streamlit's default vertical rhythm so cards sit close together */
div[data-testid="stVerticalBlock"] { gap: 0.75rem; }
div[data-testid="stElementContainer"] { margin-bottom: 0 !important; }

/* ══ Cards ══════════════════════════════════════════════════════════
   Any st.container(key="card_xxx") becomes a real white rounded card.
   A plain <div> from st.markdown cannot wrap widgets - only a genuine
   container can - which is why every card uses the card() helper.      */
[class*="st-key-card_"] {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 1px 2px rgba(16,24,40,0.04);
}

/* ══ Typography helpers ═════════════════════════════════════════════ */
.sm-title       { font-weight: 700 !important; color: #111827; font-size: 2rem !important; margin: 0 !important; letter-spacing: -0.02em; line-height: 1.2 !important; }
.sm-subtitle    { color: #9ca3af; font-size: 0.95rem !important; margin: 6px 0 0 0 !important; }
.sm-card-title  { font-weight: 700 !important; color: #111827; font-size: 1.15rem !important; margin: 0 !important; letter-spacing: -0.01em; }
.sm-card-sub    { color: #9ca3af; font-size: 0.83rem !important; margin: 2px 0 16px 0 !important; }
.sm-row         { display: flex; align-items: center; justify-content: space-between; }
.sm-row-tight   { display: flex; align-items: center; gap: 9px; }

.sm-badge {
    display: inline-block; padding: 4px 13px; border-radius: 999px;
    font-size: 12px; font-weight: 600; background: #dcfce7; color: #16a34a;
}
.sm-badge-blue {
    display: inline-block; padding: 4px 13px; border-radius: 999px;
    font-size: 12px; font-weight: 600; background: #dbeafe; color: #2563eb;
}

/* Date pill (top-right of dashboard) */
.sm-date-pill {
    background: #ffffff; border: 1px solid rgba(0,0,0,0.08); border-radius: 999px;
    padding: 9px 18px; font-size: 13.5px; font-weight: 500; color: #374151;
    display: inline-flex; align-items: center; gap: 9px; float: right;
}
.sm-dot { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; display: inline-block; }

/* ══ Buttons (base) ═════════════════════════════════════════════════ */
div.stButton > button {
    border-radius: 11px; font-weight: 600; border: 1px solid rgba(0,0,0,0.08);
    background: #ffffff; color: #374151; transition: all .15s ease;
}
div.stButton > button:hover { border-color: #4ade80; color: #16a34a; }
div.stButton > button:focus:not(:active) { border-color: #4ade80; color: #16a34a; box-shadow: none; }
div.stButton > button[kind="primary"] { background: #111827; color: #fff; border: none; }
div.stButton > button[kind="primary"]:hover { background: #1f2937; color: #fff; }

/* ══ Top navigation bar ═════════════════════════════════════════════ */
.st-key-navbar {
    position: relative;
    padding: 14px 0 12px 0;
    margin: 0 0 26px 0;
}
.st-key-navbar::before {
    content: "";
    position: absolute;
    top: 0; bottom: 0; left: 50%;
    width: 100vw;
    transform: translateX(-50%);
    background: #ffffff;
    border-bottom: 1px solid rgba(0,0,0,0.07);
    box-shadow: 0 1px 2px rgba(16,24,40,0.03);
    z-index: 0;
}
.st-key-navbar > div { position: relative; z-index: 1; }
.st-key-navbar div[data-testid="stHorizontalBlock"] { align-items: center; gap: 0.2rem; }
.st-key-navbar div.stButton > button {
    border: none; background: transparent; color: #4b5563;
    font-weight: 500; font-size: 13.5px; padding: 9px 8px; border-radius: 999px;
    box-shadow: none; white-space: nowrap;
}
.st-key-navbar div.stButton > button:hover { background: #f3f4f6; color: #111827; }
.st-key-navbar div.stButton > button[kind="primary"] {
    background: #dcfce7; color: #16a34a; font-weight: 600;
}
.st-key-navbar div.stButton > button[kind="primary"]:hover { background: #bbf7d0; color: #15803d; }

.sm-logo-row { display: flex; align-items: center; gap: 10px; }
.sm-logo-badge {
    width: 36px; height: 36px; border-radius: 11px; background: #4ade80;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.sm-logo-text { font-weight: 700; color: #111827; font-size: 1.02rem; letter-spacing: -0.01em; }
.sm-avatar {
    width: 38px; height: 38px; border-radius: 50%; background: #4ade80; color: #ffffff;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; float: right;
}

/* ══ Stat cards ═════════════════════════════════════════════════════ */
.sm-stat-card {
    background: #ffffff; border: 1px solid rgba(0,0,0,0.07); border-radius: 18px;
    padding: 20px 22px; box-shadow: 0 1px 2px rgba(16,24,40,0.04);
}
.sm-stat-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 18px; }
.sm-stat-icon {
    width: 42px; height: 42px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
}
.sm-stat-change {
    font-size: 11.5px; font-weight: 600; padding: 3px 10px; border-radius: 999px;
    background: #dcfce7; color: #16a34a;
}
.sm-stat-value { font-size: 32px; font-weight: 700; color: #111827; line-height: 1.05; letter-spacing: -0.03em; }
.sm-stat-label { font-size: 13.5px; color: #4b5563; font-weight: 500; margin-top: 8px; }
.sm-stat-sub   { font-size: 12px; color: #b0b6be; margin-top: 3px; }

/* ══ Progress bars ══════════════════════════════════════════════════ */
.sm-progress-row {
    display: flex; justify-content: space-between; align-items: baseline;
    font-size: 13.5px; color: #374151; font-weight: 500; margin-bottom: 7px;
}
.sm-progress-row b { color: #111827; font-weight: 600; }
.sm-progress-track {
    width: 100%; height: 8px; background: #eef1f0; border-radius: 999px;
    overflow: hidden; margin-bottom: 18px;
}
.sm-progress-fill { height: 100%; border-radius: 999px; }

/* ══ Streak chips ═══════════════════════════════════════════════════ */
.sm-streak-row { display: flex; gap: 6px; margin-top: 14px; }
.sm-streak-chip {
    flex: 1; text-align: center; border-radius: 9px; padding: 9px 0;
    font-size: 12.5px; font-weight: 600;
}
.sm-big-number { font-size: 40px; font-weight: 700; color: #111827; letter-spacing: -0.03em; }
.sm-big-unit   { font-size: 15px; font-weight: 500; color: #9ca3af; margin-left: 6px; }

/* ══ Upcoming tasks ═════════════════════════════════════════════════ */
.sm-task-item { display: flex; align-items: center; gap: 11px; padding: 8px 0; font-size: 13.5px; color: #374151; }
.sm-task-done-icon {
    width: 18px; height: 18px; border-radius: 50%; background: #dcfce7; color: #16a34a;
    display: flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0;
}
.sm-task-todo-icon { width: 16px; height: 16px; border: 2px solid #e5e7eb; border-radius: 50%; flex-shrink: 0; }
.sm-task-done-label { color: #b0b6be; text-decoration: line-through; }

/* Upcoming Tasks - real checkboxes, struck through once ticked */
.st-key-tasklist [data-testid="stCheckbox"] { margin-bottom: 3px; }
.st-key-tasklist label { gap: 11px !important; align-items: center !important; }
.st-key-tasklist label p {
    font-size: 13.5px !important; color: #374151 !important; margin: 0 !important;
}
.st-key-tasklist label:has(input:checked) p {
    text-decoration: line-through; color: #b0b6be !important;
}

/* ══ Quick action tiles ═════════════════════════════════════════════ */
[class*="st-key-qa_"] div.stButton > button {
    border: none; border-radius: 14px; height: 84px; font-weight: 600;
    font-size: 12.5px; white-space: pre-line; line-height: 1.7; box-shadow: none;
}
.st-key-qa_0 div.stButton > button { background:#dcfce7; color:#15803d; }
.st-key-qa_1 div.stButton > button { background:#f3e8ff; color:#7e22ce; }
.st-key-qa_2 div.stButton > button { background:#dbeafe; color:#1d4ed8; }
.st-key-qa_3 div.stButton > button { background:#ffedd5; color:#c2410c; }
.st-key-qa_4 div.stButton > button { background:#cffafe; color:#0e7490; }
.st-key-qa_5 div.stButton > button { background:#fce7f3; color:#be185d; }
[class*="st-key-qa_"] div.stButton > button:hover { filter: brightness(0.96); }

/* ══ AI recommendation card ═════════════════════════════════════════ */
.st-key-card_ai_rec {
    background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%);
    border: 1px solid rgba(74,222,128,0.22);
}
.sm-rec-icon {
    width: 34px; height: 34px; border-radius: 10px; background: #f3e8ff;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.st-key-recrefresh div.stButton > button {
    background: #fff !important; border: 1px solid rgba(0,0,0,0.07) !important;
    border-radius: 9px !important; width: 34px !important; height: 34px !important;
    padding: 0 !important; min-height: 34px !important; float: right; color: #6b7280 !important;
}
.st-key-apply_tip div.stButton > button {
    background: #16a34a; color: #fff; border: none; border-radius: 10px; font-size: 13px;
}
.st-key-apply_tip div.stButton > button:hover { background: #15803d; color: #fff; }
.st-key-dismiss_tip div.stButton > button {
    background: transparent; border: none; color: #6b7280; font-weight: 500;
    box-shadow: none; font-size: 13px;
}

a { color: #16a34a; text-decoration: none; }
</style>
"""


def avatar_html(user, cls: str = "sm-avatar-lg") -> str:
    """Photo avatar if the user has one, otherwise their initials."""
    user = user or {}
    photo = user.get("photo")
    if photo:
        return f'<img class="{cls}" src="{photo}" alt="avatar">'
    name = user.get("name", "")
    initials = "".join(p[0] for p in name.split()[:2]).upper() or "?"
    return f'<div class="{cls}">{initials}</div>'


def flat(html: str) -> str:
    """Collapse HTML onto one line before handing it to st.markdown.

    Streamlit parses the string as Markdown first, and Markdown turns any
    line indented by 4+ spaces into a code block - which is exactly what
    mangles multi-line nested markup like the owl panel.
    """
    return re.sub(r"\s*\n\s*", " ", html).strip()


_MD_CODE = re.compile(r"`([^`]+)`")
_MD_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_MD_ITALIC = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", re.DOTALL)
_MD_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
_MD_BULLET = re.compile(r"^\s*(?:[-*+]|&#x27;|•|●)\s+(.*)$")
_MD_NUMBER = re.compile(r"^\s*\d+[.)]\s+(.*)$")


def _md_inline(text: str) -> str:
    text = _MD_CODE.sub(r"<code>\1</code>", text)
    text = _MD_BOLD.sub(r"<strong>\1</strong>", text)
    text = _MD_ITALIC.sub(r"<em>\1</em>", text)
    return text


def md_to_html(text: str) -> str:
    """Render a Markdown-ish string as safe inline HTML for a custom bubble."""
    escaped = _html.escape(text or "")
    parts, open_list = [], None

    for line in escaped.splitlines():
        line = line.rstrip()
        if not line.strip():
            if open_list:
                parts.append(f"</{open_list}>")
                open_list = None
            continue

        bullet = _MD_BULLET.match(line)
        number = None if bullet else _MD_NUMBER.match(line)
        if bullet or number:
            wanted = "ul" if bullet else "ol"
            if open_list != wanted:
                if open_list:
                    parts.append(f"</{open_list}>")
                parts.append(f"<{wanted}>")
                open_list = wanted
            parts.append(f"<li>{_md_inline((bullet or number).group(1))}</li>")
            continue

        if open_list:
            parts.append(f"</{open_list}>")
            open_list = None

        heading = _MD_HEADING.match(line)
        if heading:
            parts.append(f"<p><strong>{_md_inline(heading.group(1))}</strong></p>")
        else:
            parts.append(f"<p>{_md_inline(line)}</p>")

    if open_list:
        parts.append(f"</{open_list}>")
    return "".join(parts)


def inject_theme():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@contextmanager
def card(key: str):
    """A real white rounded card that genuinely wraps the widgets inside it."""
    with st.container(key=f"card_{key}"):
        yield


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<p class="sm-title">{title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="sm-subtitle">{subtitle}</p>', unsafe_allow_html=True)
    st.write("")


def card_heading(title: str, subtitle: str = "", icon_name: str = "", icon_color: str = PRIMARY_DARK):
    """Card title on the left, optional icon on the right - matches the mock."""
    right = f'<div>{icon(icon_name, icon_color, 20)}</div>' if icon_name else ""
    sub = f'<p class="sm-card-sub">{subtitle}</p>' if subtitle else '<div style="height:14px"></div>'
    st.markdown(
        flat(f'<div class="sm-row"><p class="sm-card-title">{title}</p>{right}</div>{sub}'),
        unsafe_allow_html=True,
    )


def stat_card_html(icon_name, icon_color, icon_bg, change, value, label, sub) -> str:
    return flat(f"""
    <div class="sm-stat-card">
        <div class="sm-stat-top">
            <div class="sm-stat-icon" style="background:{icon_bg};">{icon(icon_name, icon_color, 20)}</div>
            <div class="sm-stat-change">{change}</div>
        </div>
        <div class="sm-stat-value">{value}</div>
        <div class="sm-stat-label">{label}</div>
        <div class="sm-stat-sub">{sub}</div>
    </div>
    """)


def progress_row_html(label: str, percent: int, color: str = PRIMARY, right: str = None) -> str:
    right_label = right if right is not None else f"{percent}%"
    return flat(f"""
    <div class="sm-progress-row"><span>{label}</span><b>{right_label}</b></div>
    <div class="sm-progress-track">
        <div class="sm-progress-fill" style="width:{min(max(percent,0),100)}%;background:{color};"></div>
    </div>
    """)


def streak_chip_html(day_letter: str, active: bool, is_today: bool = False) -> str:
    if active:
        bg, fg = PRIMARY, "#ffffff"
    elif is_today:
        bg, fg = PRIMARY_PILL, PRIMARY_DARK
    else:
        bg, fg = "#f3f4f6", TEXT_MUTED
    return f'<div class="sm-streak-chip" style="background:{bg};color:{fg};">{day_letter}</div>'


def task_item_html(label: str, done: bool) -> str:
    if done:
        return (
            f'<div class="sm-task-item"><span class="sm-task-done-icon">&#10003;</span>'
            f'<span class="sm-task-done-label">{label}</span></div>'
        )
    return (
        f'<div class="sm-task-item"><span class="sm-task-todo-icon"></span>'
        f'<span>{label}</span></div>'
    )


PAGE_CSS = """
<style>
/* ── Section + page headers ─────────────────────────────────────── */
.sm-sec-title { font-size: 1.3rem !important; font-weight: 700 !important; color: #111827; margin: 0 !important; }
.sm-sec-sub   { font-size: 0.83rem !important; color: #9ca3af; margin: 3px 0 0 0 !important; }
.sm-label     { font-size: 11.5px; letter-spacing: 0.06em; text-transform: uppercase;
                color: #9ca3af; font-weight: 600; margin: 0 0 6px 0; }

/* ── Generic pills ──────────────────────────────────────────────── */
.sm-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 11px; border-radius: 999px;
    font-size: 11.5px; font-weight: 600; white-space: nowrap;
}
.sm-pill-outline { border: 1px solid rgba(0,0,0,0.10); background: #fff; color: #374151; }

/* ── Trend badges (Analytics) ───────────────────────────────────── */
.sm-trend { font-size: 11.5px; font-weight: 600; display: inline-flex; align-items: center; gap: 3px; }
.sm-trend-up   { color: #16a34a; }
.sm-trend-down { color: #dc2626; }
.sm-trend-flat { color: #9ca3af; }

/* ── Upload dropzone (Notes) ────────────────────────────────────── */
.st-key-dropzone [data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border: 2px dashed #d7dcd9 !important;
    border-radius: 18px !important;
    min-height: 250px;
    flex-direction: column; justify-content: center; align-items: center;
    padding: 40px 20px !important;
}
.st-key-dropzone [data-testid="stFileUploaderDropzone"]:hover { border-color: #4ade80 !important; }
.st-key-dropzone [data-testid="stFileUploaderDropzoneInstructions"] { color: #6b7280; text-align: center; }
.st-key-dropzone [data-testid="stFileUploaderDropzone"] button {
    background: #f0fdf4 !important; color: #15803d !important;
    border: 1px solid #86efac !important; border-radius: 10px !important;
    font-weight: 600 !important; padding: 10px 22px !important;
}
.sm-drop-icon {
    width: 66px; height: 66px; border-radius: 18px; background: #f0fdf4;
    display: flex; align-items: center; justify-content: center; margin: 0 auto 18px auto;
}

/* ── Data table (Notes) ─────────────────────────────────────────── */
.sm-thead {
    display: flex; align-items: center; padding: 12px 0;
    border-top: 1px solid #f1f3f4; border-bottom: 1px solid #f1f3f4;
    font-size: 11.5px; letter-spacing: 0.05em; text-transform: uppercase;
    color: #9ca3af; font-weight: 600; margin-top: 16px;
}
.sm-file-icon {
    width: 34px; height: 34px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
}
.sm-file-name { font-size: 14px; color: #111827; font-weight: 500; margin: 0; }
.sm-file-size { font-size: 12px; color: #9ca3af; margin: 2px 0 0 0; }
.st-key-notes_table div[data-testid="stHorizontalBlock"] {
    border-bottom: 1px solid #f1f3f4; padding: 10px 0; align-items: center;
}

/* ── Button variants, opt-in per container key ──────────────────── */
[class*="st-key-btn_dark_"] div.stButton > button {
    background: #111827 !important; color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important; font-size: 13px !important;
}
[class*="st-key-btn_dark_"] div.stButton > button:hover { background: #1f2937 !important; }

[class*="st-key-btn_green_"] div.stButton > button {
    background: #f0fdf4 !important; color: #15803d !important;
    border: 1px solid #bbf7d0 !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 13px !important;
}
[class*="st-key-btn_orange_"] div.stButton > button {
    background: #fff7ed !important; color: #c2410c !important;
    border: 1px solid #fed7aa !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 13px !important;
}
[class*="st-key-btn_ghost_"] div.stButton > button {
    background: #fff !important; color: #374151 !important;
    border: 1px solid #e5e7eb !important; border-radius: 999px !important;
    font-weight: 600 !important; font-size: 13px !important;
}
[class*="st-key-btn_red_"] div.stButton > button {
    background: #fef2f2 !important; color: #dc2626 !important;
    border: 1px solid #fecaca !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 13px !important;
}

/* Segmented / filter pill rows */
[class*="st-key-seg_"] div.stButton > button {
    border-radius: 999px !important; font-size: 13px !important;
    font-weight: 600 !important; padding: 8px 4px !important;
    border: 1px solid #e5e7eb !important; background: #fff !important; color: #4b5563 !important;
}
[class*="st-key-seg_"] div.stButton > button[kind="primary"] {
    background: #111827 !important; color: #fff !important; border-color: #111827 !important;
}

/* ── Flashcards ─────────────────────────────────────────────────── */
.st-key-card_flash { min-height: 320px; }
.sm-flash-q     { font-size: 1.9rem !important; font-weight: 500 !important; color: #111827;
                  text-align: center; margin: 44px 0 !important; line-height: 1.4; }
.sm-flash-meta  { font-size: 12px; color: #9ca3af; }
[class*="st-key-cardsel_"] div.stButton > button {
    border-radius: 11px !important; font-size: 13px !important; font-weight: 600 !important;
    padding: 16px 0 !important; border: 1px solid #e5e7eb !important;
    background: #fff !important; color: #4b5563 !important;
}
[class*="st-key-cardsel_"] div.stButton > button[kind="primary"] {
    background: #f0fdf4 !important; color: #15803d !important; border-color: #86efac !important;
}

/* ── Quiz ───────────────────────────────────────────────────────── */
.sm-center-title { text-align: center; }
.st-key-card_quiz_setup { max-width: 700px; margin: 0 auto; }

/* ── Chat ───────────────────────────────────────────────────────── */
.st-key-card_chat_side { padding: 16px 14px !important; }
[class*="st-key-chatsel_"] div.stButton > button {
    border: none !important; background: transparent !important; box-shadow: none !important;
    text-align: left !important; font-weight: 500 !important; font-size: 13.5px !important;
    color: #4b5563 !important; border-radius: 10px !important; padding: 9px 12px !important;
}
[class*="st-key-chatsel_"] div.stButton > button:hover { background: #f3f4f6 !important; }
[class*="st-key-chatsel_"] div.stButton > button[kind="primary"] {
    background: #f0fdf4 !important; color: #15803d !important; font-weight: 600 !important;
}
.sm-chat-group { font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase;
                 color: #9ca3af; font-weight: 600; margin: 16px 0 4px 4px; }
.sm-msg-user {
    background: #111827; color: #fff; border-radius: 16px 16px 4px 16px;
    padding: 13px 18px; font-size: 14px; float: right; max-width: 78%; line-height: 1.55;
}
.sm-msg-ai {
    background: #fff; color: #111827; border: 1px solid rgba(0,0,0,0.07);
    border-radius: 16px 16px 16px 4px; padding: 14px 18px; font-size: 14px;
    max-width: 88%; line-height: 1.6; box-shadow: 0 1px 2px rgba(16,24,40,0.04);
}
.sm-chat-foot { text-align: center; font-size: 11.5px; color: #b0b6be; margin-top: 10px; }

/* ── Analytics ──────────────────────────────────────────────────── */
.sm-mastery-row { display: flex; align-items: center; gap: 9px; font-size: 13.5px;
                  color: #374151; padding: 5px 0; }
.sm-mastery-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.st-key-card_insight {
    background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%);
    border: 1px solid rgba(74,222,128,0.22);
}
.sm-insight-item {
    background: #fff; border: 1px solid rgba(0,0,0,0.05); border-radius: 12px;
    padding: 13px 15px; margin-bottom: 10px; display: flex; gap: 12px; align-items: flex-start;
}
.sm-insight-item h5 { font-size: 13.5px; font-weight: 600; color: #111827; margin: 0 0 3px 0; }
.sm-insight-item p  { font-size: 12.5px; color: #6b7280; margin: 0; line-height: 1.5; }

/* ── Recommendations ────────────────────────────────────────────── */
.sm-alert-red {
    background: #fef2f2; border: 1px solid #fecaca; border-radius: 14px;
    padding: 16px 20px; margin-bottom: 20px;
}
.sm-alert-red h5 { color: #b91c1c; font-size: 14px; font-weight: 700; margin: 0 0 4px 0; }
.sm-alert-red p  { color: #dc2626; font-size: 12.5px; margin: 0; line-height: 1.55; }
.sm-protip {
    background: #fffbeb; border: 1px solid #fde68a; border-radius: 11px;
    padding: 12px 15px; font-size: 12.5px; color: #92400e; line-height: 1.55; margin: 14px 0 10px 0;
}
.sm-schedule {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 11px;
    padding: 12px 15px; font-size: 13px; color: #1d4ed8; font-weight: 600;
    display: flex; justify-content: space-between; align-items: center;
}
.sm-rec-desc { font-size: 13.5px; color: #4b5563; line-height: 1.65; margin: 14px 0; }

/* ── Profile ────────────────────────────────────────────────────── */
.sm-avatar-lg {
    width: 84px; height: 84px; border-radius: 20px;
    background: linear-gradient(135deg,#6ee7a8,#4ade80);
    color: #fff; display: flex; align-items: center; justify-content: center;
    font-size: 27px; font-weight: 700; margin: 0 auto;
}
img.sm-avatar-lg, img.sm-avatar { object-fit: cover; display: block; }
.sm-field-box {
    background: #f8fafc; border: 1px solid #eef1f4; border-radius: 11px;
    padding: 13px 17px; display: flex; justify-content: space-between; align-items: center;
    font-size: 14px; color: #111827; margin-bottom: 4px;
}
.sm-field-box span.edit { color: #9ca3af; font-size: 13px; font-weight: 500; }
[class*="st-key-pnav_"] div.stButton > button {
    border: none !important; background: transparent !important; box-shadow: none !important;
    text-align: left !important; border-radius: 12px !important;
    padding: 13px 15px !important; font-weight: 600 !important; font-size: 14px !important;
    color: #374151 !important;
}
[class*="st-key-pnav_"] div.stButton > button:hover { background: #f3f4f6 !important; }
[class*="st-key-pnav_"] div.stButton > button[kind="primary"] {
    background: #f0fdf4 !important; color: #15803d !important;
    border: 1px solid #bbf7d0 !important;
}
.sm-danger-row {
    background: #fef2f2; border: 1px solid #fecaca; border-radius: 12px;
    padding: 15px 18px; display: flex; justify-content: space-between; align-items: center;
}
.sm-danger-row h5 { color: #dc2626; font-size: 14px; font-weight: 700; margin: 0 0 2px 0; }
.sm-danger-row p  { color: #ef4444; font-size: 12.5px; margin: 0; }
</style>
"""


def inject_page_css():
    st.markdown(PAGE_CSS, unsafe_allow_html=True)


def pill(text: str, bg: str = PRIMARY_PILL, fg: str = PRIMARY_DARK, icon_name: str = "") -> str:
    glyph = icon(icon_name, fg, 13) if icon_name else ""
    return flat(f'<span class="sm-pill" style="background:{bg};color:{fg};">{glyph}{text}</span>')


def trend_badge(value: str, direction: str = "up") -> str:
    arrow = {"up": "&#8599;", "down": "&#8600;", "flat": "&mdash;"}[direction]
    return flat(f'<span class="sm-trend sm-trend-{direction}">{arrow} {value}</span>')


def metric_card_html(icon_name, icon_color, icon_bg, value, label, sub,
                     trend_value="", trend_dir="up") -> str:
    """Analytics-style stat card: icon chip left, trend right, value, label, sub."""
    trend = trend_badge(trend_value, trend_dir) if trend_value else ""
    return flat(f"""
    <div class="sm-stat-card">
        <div class="sm-stat-top">
            <div class="sm-stat-icon" style="background:{icon_bg};">{icon(icon_name, icon_color, 20)}</div>
            {trend}
        </div>
        <div class="sm-stat-value">{value}</div>
        <div class="sm-stat-label">{label}</div>
        <div class="sm-stat-sub">{sub}</div>
    </div>
    """)


def section_title(title: str, subtitle: str = "", right_html: str = ""):
    right = f'<div style="text-align:right;">{right_html}</div>' if right_html else ""
    sub = f'<p class="sm-sec-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        flat(f'<div class="sm-row"><div><p class="sm-sec-title">{title}</p>{sub}</div>{right}</div>'),
        unsafe_allow_html=True,
    )
