"""Quiz - setup, question flow, and results review."""

from datetime import datetime

import streamlit as st

from services import firebase_service as fb
from services import gemini_service as gem
from utils.theme import flat, pill, card, PRIMARY, PRIMARY_DARK

TOPIC_TYPES = ["Multiple Choice", "True or False", "Mixed Review"]

QUICK_SUBJECTS = ["Biology", "Chemistry", "Physics", "Mathematics", "History"]

PILL_CSS = """
<style>
/* Selected quick-select chip is dark, matching the mock (Streamlit would
   otherwise paint it with the green primaryColor from config.toml) */
.st-key-quickpick [data-testid="stBaseButton-pillsActive"],
.st-key-quickpick button[kind="pillsActive"],
.st-key-quickpick button[aria-checked="true"] {
    background: #111827 !important; color: #ffffff !important;
    border-color: #111827 !important; font-weight: 600 !important;
}
.st-key-quickpick button {
    border-radius: 999px !important; font-size: 13px !important;
    border: 1px solid #e5e7eb !important; padding: 8px 16px !important;
}
.st-key-quickpick [data-testid="stElementContainer"] { margin: 0 !important; }
</style>
"""

QUIZ_CSS = """
<style>
.st-key-card_quizsetup { max-width: 720px; margin: 0 auto; }
.sm-quiz-head { text-align: center; margin-bottom: 26px; }
.sm-quiz-head h1 { font-size: 2rem !important; font-weight: 700 !important; color: #111827; margin: 0 !important; }
.sm-quiz-head p  { color: #9ca3af; font-size: 0.95rem !important; margin: 8px 0 0 0 !important; }
.sm-opt-row { font-size: 14.5px; color: #374151; }
.st-key-card_quizsetup hr { margin: 18px 0 14px 0; border-color: #f1f3f4; }
</style>
"""


def _start(questions, subject):
    st.session_state.quiz_state = {
        "questions": questions, "subject": subject, "current": 0,
        "answers": [None] * len(questions), "submitted": False,
        "started_at": datetime.now().isoformat(),
    }


def render_quiz():
    uid = st.session_state.user["uid"]
    st.markdown(QUIZ_CSS, unsafe_allow_html=True)
    st.markdown(PILL_CSS, unsafe_allow_html=True)
    state = st.session_state.quiz_state

    if not state:
        _render_setup(uid)
    elif not state["submitted"]:
        _render_question(uid, state)
    else:
        _render_results(state)


def _render_setup(uid):
    st.markdown('<div class="sm-quiz-head"><h1>Study Quiz</h1>'
                '<p>Select a subject and topic to generate AI-powered questions</p></div>',
                unsafe_allow_html=True)

    notes = [n for n in fb.get_notes(uid) if n.get("text")]
    bank_subjects = QUICK_SUBJECTS
    extra = [k for k in gem.DEFAULT_QUESTION_BANK if k not in bank_subjects]
    subjects = bank_subjects + extra + [n["name"] for n in notes]

    if "quiz_subject" not in st.session_state:
        st.session_state.quiz_subject = subjects[0]

    with card("quizsetup"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<p class="sm-label">Subject</p>', unsafe_allow_html=True)
            subject = st.selectbox("Subject", subjects, label_visibility="collapsed",
                                   index=subjects.index(st.session_state.quiz_subject)
                                   if st.session_state.quiz_subject in subjects else 0,
                                   key="quiz_subject_sel")
        with c2:
            st.markdown('<p class="sm-label">Topic</p>', unsafe_allow_html=True)
            topic = st.selectbox("Topic", TOPIC_TYPES, label_visibility="collapsed", key="quiz_topic")

        st.markdown('<p class="sm-sec-sub" style="margin:20px 0 8px 0 !important;">'
                    'Quick select subject</p>', unsafe_allow_html=True)
        with st.container(key="quickpick"):
            picked = st.pills("Quick select subject", bank_subjects,
                              selection_mode="single",
                              default=subject if subject in bank_subjects else None,
                              key="quiz_quickpick", label_visibility="collapsed")
        if picked and picked != st.session_state.quiz_subject:
            st.session_state.quiz_subject = picked
            st.rerun()

        num_q = 6 if topic == "Mixed Review" else 4
        st.markdown('<div style="height:1px;background:#f1f3f4;margin:22px 0 14px 0;"></div>',
                    unsafe_allow_html=True)
        m_l, m_r = st.columns([2, 1], vertical_alignment="center")
        with m_l:
            st.markdown(f'<p class="sm-sec-sub" style="margin:0 !important;">{num_q} questions '
                        f'&middot; {topic}</p>', unsafe_allow_html=True)
        with m_r:
            st.markdown(f'<p class="sm-sec-sub" style="margin:0 !important;text-align:right;">'
                        f'{subject}</p>', unsafe_allow_html=True)

        st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
        with st.container(key="btn_dark_genquiz"):
            if st.button("Generate Quiz", width="stretch", icon=":material/auto_awesome:"):
                note_text = next((n["text"] for n in notes if n["name"] == subject), "")
                with st.spinner("Building your quiz..."):
                    qs = gem.generate_quiz(note_text, subject=subject,
                                           num_questions=num_q, difficulty="Medium")
                _start(qs, subject)
                st.rerun()

    history = fb.get_quiz_results(uid)
    if history:
        st.write("")
        with card("quizhist"):
            st.markdown('<p class="sm-sec-title">Past Results</p>', unsafe_allow_html=True)
            st.write("")
            for r in sorted(history, key=lambda x: x.get("date", ""), reverse=True)[:6]:
                pct = r.get("percent", 0)
                tone = ("#f0fdf4", "#16a34a") if pct >= 70 else ("#fff7ed", "#c2410c")
                score_label = "{}/{} &middot; {}%".format(r.get("score", 0), r.get("total", 0), pct)
                subj = r.get("subject", "Quiz")
                when = r.get("date", "")
                st.markdown(flat(
                    f'<div class="sm-row" style="padding:10px 0;border-bottom:1px solid #f1f3f4;">'
                    f'<div><p class="sm-file-name">{subj}</p>'
                    f'<p class="sm-file-size">{when}</p></div>'
                    f'{pill(score_label, tone[0], tone[1])}</div>'),
                    unsafe_allow_html=True)


def _render_question(uid, state):
    qs, i = state["questions"], state["current"]
    q = qs[i]
    percent = round((i + 1) / len(qs) * 100)

    st.markdown('<div class="sm-quiz-head"><h1>Study Quiz</h1></div>', unsafe_allow_html=True)

    with card("quizsetup"):
        st.markdown(flat(f'<div class="sm-row"><span class="sm-sec-sub" style="margin:0 !important;">'
                         f'Question {i+1} of {len(qs)}</span>{pill(state["subject"][:24])}</div>'),
                    unsafe_allow_html=True)
        st.markdown(flat(f'<div class="sm-progress-track" style="margin:12px 0 20px 0;">'
                         f'<div class="sm-progress-fill" style="width:{percent}%;'
                         f'background:{PRIMARY};"></div></div>'), unsafe_allow_html=True)

        st.markdown(f'<p style="font-size:1.25rem;font-weight:600;color:#111827;'
                    f'line-height:1.5;margin-bottom:18px;">{q["question"]}</p>',
                    unsafe_allow_html=True)

        chosen = st.radio("Answer", q["options"], label_visibility="collapsed",
                          index=state["answers"][i], key=f"quiz_q_{i}")
        if chosen is not None:
            state["answers"][i] = q["options"].index(chosen)

        st.write("")
        b1, b2, b3 = st.columns(3)
        with b1:
            if i > 0:
                with st.container(key="btn_ghost_qprev"):
                    if st.button("Previous", width="stretch", icon=":material/chevron_left:"):
                        state["current"] -= 1
                        st.rerun()
        with b2:
            with st.container(key="btn_ghost_qcancel"):
                if st.button("Cancel", width="stretch"):
                    st.session_state.quiz_state = {}
                    st.rerun()
        with b3:
            last = i == len(qs) - 1
            with st.container(key="btn_dark_qnext"):
                if st.button("Submit Quiz" if last else "Next", width="stretch",
                             icon=":material/check:" if last else ":material/chevron_right:"):
                    if not last:
                        state["current"] += 1
                    else:
                        score = sum(1 for j, qq in enumerate(qs)
                                    if state["answers"][j] == qq["correct_index"])
                        result = {"subject": state["subject"], "score": score, "total": len(qs),
                                  "percent": round(score / len(qs) * 100),
                                  "date": datetime.now().strftime("%b %d, %Y")}
                        fb.save_quiz_result(uid, result)
                        state["submitted"] = True
                        state["result"] = result
                    st.rerun()


def _render_results(state):
    r, qs = state["result"], state["questions"]
    tone = PRIMARY_DARK if r["percent"] >= 70 else "#c2410c"

    st.markdown('<div class="sm-quiz-head"><h1>Quiz Complete</h1></div>', unsafe_allow_html=True)

    with card("quizsetup"):
        st.markdown(flat(f'<div style="text-align:center;padding:10px 0 4px 0;">'
                         f'<span class="sm-big-number" style="color:{tone};">{r["percent"]}</span>'
                         f'<span class="sm-big-unit">%</span></div>'), unsafe_allow_html=True)
        st.markdown(f'<p class="sm-sec-sub" style="text-align:center;margin-bottom:16px !important;">'
                    f'{r["score"]} of {r["total"]} correct</p>', unsafe_allow_html=True)
        st.markdown(flat(f'<div class="sm-progress-track"><div class="sm-progress-fill" '
                         f'style="width:{r["percent"]}%;background:{PRIMARY};"></div></div>'),
                    unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            with st.container(key="btn_ghost_retake"):
                if st.button("Retake Quiz", width="stretch", icon=":material/refresh:"):
                    _start(qs, state["subject"])
                    st.rerun()
        with b2:
            with st.container(key="btn_dark_newquiz"):
                if st.button("New Quiz", width="stretch", icon=":material/add:"):
                    st.session_state.quiz_state = {}
                    st.rerun()

    st.write("")
    with card("quizreview"):
        st.markdown('<p class="sm-sec-title">Review</p>', unsafe_allow_html=True)
        st.write("")
        for i, q in enumerate(qs):
            picked, correct = state["answers"][i], q["correct_index"]
            ok = picked == correct
            badge = pill("Correct", "#f0fdf4", "#16a34a") if ok else pill("Missed", "#fef2f2", "#dc2626")
            with st.expander(f"Q{i+1}. {q['question']}"):
                st.markdown(badge, unsafe_allow_html=True)
                for oi, opt in enumerate(q["options"]):
                    if oi == correct:
                        st.markdown(f'<p class="sm-opt-row" style="color:#16a34a;font-weight:600;">'
                                    f'&#10003; {opt}</p>', unsafe_allow_html=True)
                    elif oi == picked:
                        st.markdown(f'<p class="sm-opt-row" style="color:#dc2626;">'
                                    f'&#10007; {opt}</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p class="sm-opt-row" style="color:#9ca3af;">{opt}</p>',
                                    unsafe_allow_html=True)
                if q.get("explanation"):
                    st.markdown(f'<p class="sm-file-size" style="margin-top:10px;">'
                                f'{q["explanation"]}</p>', unsafe_allow_html=True)
