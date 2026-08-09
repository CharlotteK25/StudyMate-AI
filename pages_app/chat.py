"""AI Chat - grouped thread sidebar plus the conversation pane."""

import html

import streamlit as st

from services import firebase_service as fb
from services import gemini_service as gem
from services import demo_seed
from utils.state import new_id
from utils.theme import flat, icon, OWL_SVG, card, md_to_html

SUGGESTIONS = ["Summarise Chapter 3", "Explain this concept", "Quiz me on Biology",
               "Create flashcards", "What are key formulas?", "Help me study tonight"]

CHAT_CSS = """
<style>
.st-key-card_chatside { padding: 18px 16px !important; }
.st-key-card_chatmain { padding: 0 !important; overflow: hidden; }

/* Header */
.sm-chat-header {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 20px; border-bottom: 1px solid #f1f3f4;
}
.sm-chat-burger { color: #6b7280; display: flex; }
.sm-chat-avatar {
    width: 38px; height: 38px; border-radius: 50%; background: #f0fdf4;
    border: 1px solid #dcfce7;
    display: flex; align-items: center; justify-content: center; overflow: hidden;
}
.sm-chat-avatar svg { width: 27px; height: 27px; }
.sm-chat-title  { font-size: 14.5px; font-weight: 700; color: #111827; margin: 0; }
.sm-chat-status { font-size: 11.5px; color: #16a34a; margin: 1px 0 0 0; }
.st-key-newchat_top div.stButton > button {
    background: none !important; border: none !important; box-shadow: none !important;
    color: #6b7280 !important; font-weight: 500 !important; font-size: 13px !important;
    float: right;
}
.st-key-newchat_top div.stButton > button:hover { color: #16a34a !important; }

/* Sidebar */
.st-key-newchat div.stButton > button {
    background: #111827 !important; color: #fff !important; border: none !important;
    border-radius: 10px !important; width: 36px !important; height: 36px !important;
    padding: 0 !important; min-height: 36px !important; float: right;
}
.st-key-newchat div.stButton > button:hover { background: #1f2937 !important; }
.sm-chat-group {
    display: flex; align-items: center; gap: 4px;
    font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase;
    color: #9ca3af; font-weight: 600; margin: 16px 0 4px 4px;
}
[class*="st-key-chatsel_"] div.stButton > button {
    border: 1px solid transparent !important; background: transparent !important;
    box-shadow: none !important; text-align: left !important;
    font-weight: 500 !important; font-size: 13.5px !important;
    color: #4b5563 !important; border-radius: 12px !important; padding: 10px 12px !important;
}
[class*="st-key-chatsel_"] div.stButton > button:hover { background: #f3f4f6 !important; }
[class*="st-key-chatsel_"] div.stButton > button[kind="primary"] {
    background: #f0fdf4 !important; color: #15803d !important;
    border: 1px solid #bbf7d0 !important; font-weight: 600 !important;
}
.sm-side-foot {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 18px; padding-top: 14px; border-top: 1px solid #f1f3f4;
}
.sm-side-ava {
    width: 30px; height: 30px; border-radius: 50%; background: #bbf7d0; color: #15803d;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700;
}

/* Messages */
.st-key-chatbody { padding: 24px 22px 14px 22px; }
[class*="st-key-sugg"] button {
    border-radius: 999px !important; border: none !important;
    background: #f3f4f6 !important; color: #374151 !important;
    font-size: 12.5px !important; font-weight: 500 !important;
    padding: 7px 14px !important;
}
[class*="st-key-sugg"] button:hover { background: #e5e7eb !important; color: #111827 !important; }
[class*="st-key-sugg"] [data-testid="stBaseButton-pillsActive"],
[class*="st-key-sugg"] button[aria-checked="true"] {
    background: #dcfce7 !important; color: #15803d !important;
}
[class*="st-key-sugg"] [data-testid="stElementContainer"] { margin: 0 !important; }
.sm-msg-row-r { display: flex; justify-content: flex-end; align-items: flex-start;
                gap: 10px; margin-bottom: 20px; }
.sm-msg-row-l { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 6px; }
.sm-msg-user {
    background: #111827; color: #fff; border-radius: 18px 18px 4px 18px;
    padding: 13px 18px; font-size: 14px; max-width: 72%; line-height: 1.55;
}
.sm-msg-ai {
    background: #fff; color: #111827; border: 1px solid rgba(0,0,0,0.07);
    border-radius: 4px 18px 18px 18px; padding: 15px 19px; font-size: 14px;
    max-width: 88%; line-height: 1.7; box-shadow: 0 1px 2px rgba(16,24,40,0.04);
}
/* AI reply formatting */
.sm-msg-ai p           { margin: 0 0 9px 0; font-size: 14px; line-height: 1.7; }
.sm-msg-ai p:last-child { margin-bottom: 0; }
.sm-msg-ai strong      { font-weight: 700; color: #111827; }
.sm-msg-ai em          { font-style: italic; }
.sm-msg-ai ul,
.sm-msg-ai ol          { margin: 0 0 9px 0; padding-left: 22px; }
.sm-msg-ai ul:last-child,
.sm-msg-ai ol:last-child { margin-bottom: 0; }
.sm-msg-ai li          { margin: 3px 0; line-height: 1.65; }
.sm-msg-ai li::marker  { color: #22c55e; }
.sm-msg-ai code {
    background: #f3f4f6; border-radius: 5px; padding: 1px 5px;
    font-family: ui-monospace, "Cascadia Code", Consolas, monospace; font-size: 12.5px;
}
.sm-msg-ava {
    width: 30px; height: 30px; border-radius: 50%; background: #bbf7d0; color: #15803d;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; flex-shrink: 0; margin-top: 4px;
}
.sm-msg-owl {
    width: 30px; height: 30px; border-radius: 50%; background: #f0fdf4;
    border: 1px solid #dcfce7; display: flex; align-items: center; justify-content: center;
    overflow: hidden; flex-shrink: 0; margin-top: 4px;
}
.sm-msg-owl svg { width: 21px; height: 21px; }
.sm-msg-actions { display: flex; align-items: center; gap: 12px;
                  margin: 8px 0 20px 42px; color: #9ca3af; }
.sm-msg-actions span { display: inline-flex; align-items: center; gap: 4px;
                       font-size: 12px; cursor: default; }
.sm-dot-li { color: #22c55e; margin-right: 7px; }

/* Suggested chips */
.sm-sugg-label { font-size: 12.5px; color: #9ca3af; margin: 0; white-space: nowrap; }
.sm-chat-foot { text-align: center; font-size: 11.5px; color: #b0b6be; margin-top: 8px; }
</style>
"""

CHAT_GROUPS = ["Today", "Yesterday", "This week"]


def _group_of(index: int) -> str:
    return CHAT_GROUPS[min(index // 2, 2)]


def _new_chat(uid, sessions):
    name = f"New Chat {new_id()[:4]}"
    fb.save_chat_message(uid, name, {
        "role": "assistant",
        "content": "Hi! I'm StudyMate AI. What are you studying today?"})
    st.session_state.active_chat = name


def render_chat():
    uid = st.session_state.user["uid"]
    st.markdown(CHAT_CSS, unsafe_allow_html=True)
    demo_seed.seed_chats(uid)

    sessions = fb.get_chat_sessions(uid) or {"New Chat": []}
    active = st.session_state.get("active_chat", list(sessions)[0])
    if active not in sessions:
        active = list(sessions)[0]
        st.session_state.active_chat = active
    history = sessions.get(active, [])

    user_initials = "".join(p[0] for p in st.session_state.user["name"].split()[:2]).upper() or "?"

    side, main = st.columns([1, 3.1], gap="medium")

    with side:
        with card("chatside"):
            h_l, h_r = st.columns([2, 1], vertical_alignment="center")
            with h_l:
                st.markdown('<p class="sm-label" style="margin:0;">Chats</p>', unsafe_allow_html=True)
            with h_r:
                with st.container(key="newchat"):
                    if st.button("", key="new_chat_btn", icon=":material/add:"):
                        _new_chat(uid, sessions)
                        st.rerun()

            query = st.text_input("Search", placeholder="Search chats...", key="chat_search",
                                  label_visibility="collapsed", icon=":material/search:")

            names = [n for n in sessions if not query or query.lower() in n.lower()]
            last_group = None
            for i, name in enumerate(names):
                group = _group_of(i)
                if group != last_group:
                    st.markdown(flat(f'<div class="sm-chat-group">'
                                     f'{icon("chevron_down", "#9ca3af", 12)} {group}</div>'),
                                unsafe_allow_html=True)
                    last_group = group
                with st.container(key=f"chatsel_{i}"):
                    if st.button(name, key=f"cs_{name}", width="stretch",
                                 icon=":material/chat_bubble:",
                                 type="primary" if name == active else "secondary"):
                        st.session_state.active_chat = name
                        st.rerun()

            st.markdown('<div style="height:1px;background:#f1f3f4;margin:16px 0 10px 0;"></div>',
                        unsafe_allow_html=True)
            st.markdown('<p class="sm-label" style="margin:0 0 6px 0;">Context</p>',
                        unsafe_allow_html=True)
            notes = [n for n in fb.get_notes(uid) if n.get("text")]
            context = st.selectbox("Ground answers in a note",
                                   ["None"] + [n["name"] for n in notes],
                                   key="chat_context_note", label_visibility="collapsed")

            st.markdown(flat(f'<div class="sm-side-foot">'
                             f'<div class="sm-side-ava">{user_initials}</div>'
                             f'{icon("gear", "#9ca3af", 17)}</div>'), unsafe_allow_html=True)

    with main:
        with card("chatmain"):
            head_l, head_r = st.columns([4, 1], vertical_alignment="center")
            with head_l:
                st.markdown(flat(
                    f'<div class="sm-chat-header" style="border-bottom:none;padding-bottom:0;">'
                    f'  <span class="sm-chat-burger">{icon("menu", "#6b7280", 19)}</span>'
                    f'  <div class="sm-chat-avatar">{OWL_SVG}</div>'
                    f'  <div><p class="sm-chat-title">{active}</p>'
                    f'  <p class="sm-chat-status">&#9679; StudyMate AI &middot; Online</p></div>'
                    f'</div>'), unsafe_allow_html=True)
            with head_r:
                with st.container(key="newchat_top"):
                    if st.button("New chat", key="new_chat_top", icon=":material/add:"):
                        _new_chat(uid, sessions)
                        st.rerun()
            st.markdown('<div style="height:1px;background:#f1f3f4;"></div>', unsafe_allow_html=True)

            with st.container(key="chatbody"):
                if not history:
                    st.markdown('<p style="color:#9ca3af;font-size:14px;text-align:center;'
                                'padding:90px 0;">Ask a question to start the conversation.</p>',
                                unsafe_allow_html=True)

                for msg in history:
                    if msg["role"] == "user":
                        safe = html.escape(msg["content"])
                        st.markdown(flat(
                            f'<div class="sm-msg-row-r">'
                            f'<div class="sm-msg-user">{safe}</div>'
                            f'<div class="sm-msg-ava">{user_initials}</div></div>'),
                            unsafe_allow_html=True)
                    else:
                        actions = flat(
                            f'<div class="sm-msg-actions">'
                            f'<span>{icon("copy", "#9ca3af", 13)} Copy</span>'
                            f'<span>{icon("thumb_up", "#9ca3af", 13)}</span>'
                            f'<span>{icon("thumb_down", "#9ca3af", 13)}</span>'
                            f'<span>{icon("rotate", "#9ca3af", 13)}</span></div>')
                        st.markdown(flat(
                            f'<div class="sm-msg-row-l">'
                            f'<div class="sm-msg-owl">{OWL_SVG}</div>'
                            f'<div class="sm-msg-ai">{md_to_html(msg["content"])}</div></div>')
                            + actions, unsafe_allow_html=True)

        lab_col, pill_col = st.columns([0.5, 8], vertical_alignment="center")
        with lab_col:
            st.markdown('<p class="sm-sugg-label">Suggested:</p>', unsafe_allow_html=True)
        with pill_col:
            with st.container(key="suggpills"):
                picked = st.pills("Suggested", SUGGESTIONS, selection_mode="single",
                                  key="chat_sugg", label_visibility="collapsed")

        prompt = st.chat_input("Ask StudyMate anything...")

        if picked is None:
            st.session_state._last_sugg = None
        elif not prompt and picked != st.session_state.get("_last_sugg"):
            prompt = picked
            st.session_state._last_sugg = picked

        st.markdown('<p class="sm-chat-foot">StudyMate AI &middot; Press Enter to send, '
                    'Shift+Enter for a new line</p>', unsafe_allow_html=True)

        if prompt:
            fb.save_chat_message(uid, active, {"role": "user", "content": prompt})
            ctx = next((n["text"] for n in notes if n["name"] == context), "") \
                if context != "None" else ""
            with st.spinner("Thinking..."):
                reply = gem.chat_response(history + [{"role": "user", "content": prompt}],
                                          prompt, ctx)
            fb.save_chat_message(uid, active, {"role": "assistant", "content": reply})
            st.rerun()
