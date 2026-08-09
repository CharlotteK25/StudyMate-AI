"""Study Recommendations - filterable technique cards."""

import streamlit as st

from services import firebase_service as fb
from utils.state import go_to, today_str
from utils.theme import flat, icon, pill, card

SUBJECT_SCORES = {"Biology": 82, "Chemistry": 67, "Physics": 74, "Mathematics": 91, "History": 58}

TAG_STYLES = {
    "High Priority":  ("#fff7ed", "#c2410c"),
    "New Technique":  ("#faf5ff", "#9333ea"),
    "Weak Subject":   ("#fef2f2", "#dc2626"),
    "Recommended":    ("#f0fdf4", "#16a34a"),
    "On Track":       ("#eff6ff", "#2563eb"),
}
DIFFICULTY = {"Easy": ("#f0fdf4", "#16a34a"),
              "Moderate": ("#fff7ed", "#c2410c"),
              "Advanced": ("#fef2f2", "#dc2626")}

TECHNIQUES = [
    {"title": "Pomodoro Technique", "level": "Easy", "accent": "#60a5fa",
     "icon": "clock", "icon_bg": "#eff6ff", "icon_fg": "#2563eb",
     "sub": "Boost focus with structured work intervals",
     "tags": ["High Priority", "New Technique"], "subjects": ["Chemistry", "History"],
     "stat": "Reduces mental fatigue by up to 40%",
     "body": "Break your study sessions into 25-minute focused sprints followed by a 5-minute break. "
             "After four rounds, take a longer 20-minute rest. Especially effective for Chemistry and "
             "History where sustained concentration is critical.",
     "tip": "Set a physical timer - it creates a stronger commitment than a phone app.",
     "target": "Quiz",
     "schedule": [("Mon", "Chemistry", "4 × 25 min", "Formula revision"),
                  ("Tue", "History", "4 × 25 min", "Essay planning"),
                  ("Wed", "Chemistry", "3 × 25 min", "Practice problems"),
                  ("Thu", "History", "4 × 25 min", "Timeline review"),
                  ("Fri", "Both", "2 × 25 min each", "Mixed revision")],
     "steps": ["Pick one task and set a timer for 25 minutes - nothing else exists until it rings",
               "Take a 5-minute break away from your desk (no phone scrolling)",
               "Repeat. After four pomodoros, take a longer 20-30 minute rest",
               "Log how many pomodoros each subject actually needs - it makes planning honest"],
     "why": "Your brain can only hold intense focus for so long before attention drifts. "
            "Short timed sprints stop the drift before it starts, and the visible countdown "
            "turns vague \"study for a few hours\" into a concrete, finishable unit."},
    {"title": "Spaced Repetition", "level": "Moderate", "accent": "#fb923c",
     "icon": "sparkle", "icon_bg": "#fff7ed", "icon_fg": "#c2410c",
     "sub": "Review material at optimally increasing intervals",
     "tags": ["Weak Subject", "Recommended"], "subjects": ["History", "Chemistry"],
     "stat": "Improves long-term retention by 80%",
     "body": "Instead of cramming, revisit concepts at growing intervals - 1 day, 3 days, 7 days, "
             "14 days. Your History and Chemistry scores show clear retention gaps that spaced "
             "repetition directly targets, reinforcing memory just before it fades.",
     "tip": "Use your Flashcards page - it's already set up for spaced review cycles.",
     "target": "Flashcards",
     "schedule": [("Day 1", "History", "20 min", "Initial learning"),
                  ("Day 2", "History", "10 min", "First recall"),
                  ("Day 4", "History", "10 min", "Second recall"),
                  ("Day 8", "Chemistry", "15 min", "Deep recall"),
                  ("Day 15", "Both", "20 min", "Final consolidation")],
     "steps": ["Learn the material properly once - notes, summary, flashcards",
               "Review it again the next day, briefly, from memory first",
               "Stretch the gap each time: 2 days, 4 days, a week, two weeks",
               "If you fail a recall, shrink the gap back down for that topic only"],
     "why": "Memory fades on a predictable curve, and reviewing just before you'd forget "
            "resets that curve with interest - each cycle makes the memory last longer. "
            "Cramming feels productive but skips exactly the step that makes things stick."},
    {"title": "Active Recall Practice", "level": "Moderate", "accent": "#a78bfa",
     "icon": "brain", "icon_bg": "#faf5ff", "icon_fg": "#7e22ce",
     "sub": "Test yourself instead of re-reading notes",
     "tags": ["Recommended", "High Priority"], "subjects": ["Mathematics", "Physics"],
     "stat": "2x more effective than re-reading",
     "body": "Close your notes and write down everything you remember on a blank page. This forces "
             "your brain to retrieve information - the single most powerful learning activity. Ideal "
             "for Mathematics where procedure recall matters most.",
     "tip": "After each lecture, write a 5-minute brain dump without looking at your notes.",
     "target": "Quiz",
     "schedule": [("Mon", "Mathematics", "15 min", "Brain dump after class"),
                  ("Tue", "Physics", "20 min", "Blank-page recall"),
                  ("Thu", "Mathematics", "25 min", "Past-paper questions"),
                  ("Fri", "Physics", "15 min", "Formula recall test"),
                  ("Sun", "Both", "30 min", "Weekly recall review")],
     "steps": ["Close the notes. Blank page. Write everything you remember about the topic",
               "Check against your notes and mark what you missed in a different colour",
               "Turn every gap into a question and quiz yourself on it tomorrow",
               "Do recall before re-reading, always - reading after recall sticks better"],
     "why": "Struggling to retrieve something is what strengthens it - far more than "
            "re-reading, which mostly builds false familiarity. The material feels harder "
            "this way precisely because it's working."},
    {"title": "Interleaved Practice", "level": "Advanced", "accent": "#fbbf24",
     "icon": "layers", "icon_bg": "#fff7ed", "icon_fg": "#c2410c",
     "sub": "Mix subjects within a single study session",
     "tags": ["New Technique", "On Track"], "subjects": ["Biology", "Physics", "Mathematics"],
     "stat": "43% better exam performance",
     "body": "Instead of studying one subject for hours, alternate between Biology, Physics and "
             "Mathematics in the same session. Interleaving feels harder but dramatically improves "
             "your ability to distinguish and apply different concepts under exam pressure.",
     "tip": "Start with 20-min blocks per subject, then reduce to 10 min as you improve.",
     "target": "Notes",
     "schedule": [("Mon", "Bio + Physics", "3 × 20 min", "Alternating blocks"),
                  ("Wed", "Physics + Math", "3 × 20 min", "Mixed problem sets"),
                  ("Fri", "Bio + Math", "3 × 15 min", "Shorter switches"),
                  ("Sun", "All three", "4 × 10 min", "Rapid rotation")],
     "steps": ["Pick 2-3 subjects and split your session into short blocks",
               "Switch subject every block even if you're mid-flow - that's the point",
               "Shuffle the order each session so no pairing becomes routine",
               "Shrink the blocks as switching gets easier"],
     "why": "Blocking one subject lets you coast on short-term context. Forcing switches "
            "makes your brain reload each subject from scratch, which is exactly the skill "
            "an exam paper full of mixed questions demands."},
    {"title": "Feynman Technique", "level": "Moderate", "accent": "#34d399",
     "icon": "book", "icon_bg": "#f0fdf4", "icon_fg": "#16a34a",
     "sub": "Explain the concept in plain language",
     "tags": ["Recommended"], "subjects": ["Physics", "Chemistry"],
     "stat": "Exposes knowledge gaps immediately",
     "body": "Pick a concept and explain it as if teaching a 12-year-old. Wherever you stumble or "
             "reach for jargon, you've found a gap. Go back to the source, then simplify again until "
             "the explanation flows without notes.",
     "tip": "Use the AI Chat to play student - ask it to question your explanation.",
     "target": "AI Chat",
     "schedule": [("Tue", "Physics", "20 min", "Explain one concept aloud"),
                  ("Wed", "Chemistry", "15 min", "Simplify the explanation"),
                  ("Thu", "Physics", "15 min", "Fill the gaps you found"),
                  ("Sat", "Both", "25 min", "Teach it to AI Chat")],
     "steps": ["Pick a concept and explain it out loud as if to a 12-year-old",
               "Notice every stumble or bit of jargon - each one is a gap",
               "Go back to the source and re-learn just those gaps",
               "Simplify again until it flows with no notes in front of you"],
     "why": "You can recognise material without actually understanding it. Teaching removes "
            "that hiding place - an explanation either flows in plain words or it exposes "
            "precisely where your understanding runs out."},
    {"title": "Dual Coding", "level": "Easy", "accent": "#f472b6",
     "icon": "trend", "icon_bg": "#fce7f3", "icon_fg": "#db2777",
     "sub": "Pair words with visuals to double encoding",
     "tags": ["New Technique", "On Track"], "subjects": ["Biology", "History"],
     "stat": "Boosts recall by up to 65%",
     "body": "Convert your written notes into diagrams, timelines and flowcharts. Your brain stores "
             "verbal and visual information along separate paths, so encoding both gives you two "
             "independent routes back to the same fact during an exam.",
     "tip": "Redraw one diagram from memory at the end of each study block.",
     "target": "Notes",
     "schedule": [("Mon", "Biology", "20 min", "Draw the process diagram"),
                  ("Wed", "History", "20 min", "Build a timeline"),
                  ("Fri", "Biology", "15 min", "Redraw from memory"),
                  ("Sun", "History", "15 min", "Flowchart from memory")],
     "steps": ["Take one section of notes and turn it into a diagram, timeline or flowchart",
               "Label it from memory first, then check and correct",
               "At the end of the week, redraw the whole thing on a blank page",
               "Keep the sketches - flipping through them is a fast pre-exam review"],
     "why": "Words and images are stored along separate paths in memory. Encoding both "
            "gives you two independent routes back to the same fact, so if one fails in "
            "the exam the other still gets you there."},
]

FILTERS = ["All", "Weak Subject", "High Priority", "Recommended", "New Technique", "On Track"]

REC_CSS = """
<style>
[class*="st-key-card_tech_"] { border-top-width: 3px !important; border-top-style: solid !important; }
.sm-tech-head { display: flex; gap: 13px; align-items: flex-start; }
.sm-tech-icon { width: 44px; height: 44px; border-radius: 13px;
                display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.sm-tech-title { font-size: 1.08rem !important; font-weight: 700 !important; color: #111827; margin: 0 !important; }
.sm-tech-sub   { font-size: 12.5px !important; color: #9ca3af; margin: 3px 0 0 0 !important; }

/* blue revision-schedule expander, styled to match the Figma panel */
[class*="st-key-card_tech_"] details {
    background: #eff6ff !important; border: 1px solid #bfdbfe !important;
    border-radius: 10px !important;
}
[class*="st-key-card_tech_"] summary {
    padding: 10px 14px !important;
}
[class*="st-key-card_tech_"] summary p,
[class*="st-key-card_tech_"] summary span {
    color: #2563eb !important; font-weight: 600 !important; font-size: 13.5px !important;
}
[class*="st-key-card_tech_"] summary svg { fill: #2563eb !important; color: #2563eb !important; }
[class*="st-key-card_tech_"] summary:hover { color: #1d4ed8 !important; }
[class*="st-key-card_tech_"] details [data-testid="stExpanderDetails"] {
    padding: 6px 10px 12px 10px !important;
}

.sm-sched { border: 1px solid #bfdbfe; border-radius: 10px; overflow: hidden; background: #ffffff; }
.sm-sched-head {
    display: flex; align-items: center; gap: 8px;
    background: #dbeafe; padding: 9px 14px;
    font-size: 13px; font-weight: 700; color: #1d4ed8;
}
.sm-sched-row {
    display: flex; align-items: center; gap: 12px;
    padding: 9px 14px; font-size: 13px;
}
.sm-sched-row:nth-child(even) { background: #eff6ff; }
.sm-sched-day  { color: #2563eb; font-weight: 700; min-width: 46px; }
.sm-sched-subj { color: #111827; font-weight: 500; flex: 1; }
.sm-sched-dur  {
    background: #ffffff; border: 1px solid #bfdbfe; border-radius: 999px;
    color: #2563eb; font-size: 11.5px; font-weight: 600;
    padding: 2px 10px; white-space: nowrap;
}
.sm-sched-note { color: #6b7280; font-size: 12px; min-width: 118px; text-align: right; }

.sm-learn-why {
    background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px;
    padding: 12px 16px; font-size: 13.5px; color: #374151; line-height: 1.65;
}
.sm-learn-step { display: flex; gap: 11px; align-items: flex-start; margin: 9px 0; }
.sm-learn-num {
    width: 22px; height: 22px; border-radius: 50%; background: #dcfce7; color: #15803d;
    font-size: 11.5px; font-weight: 700; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; margin-top: 1px;
}
.sm-learn-step p { margin: 0; font-size: 13.5px; color: #374151; line-height: 1.55; }
</style>
"""


def render_recommendations():
    uid = st.session_state.user["uid"]
    st.markdown(REC_CSS, unsafe_allow_html=True)

    h_l, h_r = st.columns([3, 1], vertical_alignment="center")
    with h_l:
        st.markdown('<p class="sm-title">Study Recommendations</p>', unsafe_allow_html=True)
        st.markdown('<p class="sm-subtitle">Personalised AI techniques based on your '
                    'performance data</p>', unsafe_allow_html=True)
    with h_r:
        st.markdown(flat(f'<div style="text-align:right;">'
                         f'{pill(f"{len(TECHNIQUES)} insights generated", "#eff6ff", "#2563eb", "sparkle")}'
                         f'</div>'), unsafe_allow_html=True)
    st.write("")

    s_col, *f_cols = st.columns([2.2] + [0.85] * len(FILTERS), vertical_alignment="center")
    with s_col:
        query = st.text_input("Search", placeholder="Search by title or subject...",
                              key="rec_search", label_visibility="collapsed",
                              icon=":material/search:")
    active = st.session_state.setdefault("rec_filter", "All")
    for col, name in zip(f_cols, FILTERS):
        label = f"All ({len(TECHNIQUES)})" if name == "All" else name
        with col:
            with st.container(key=f"seg_f_{name}"):
                if st.button(label, key=f"rf_{name}", width="stretch",
                             type="primary" if active == name else "secondary"):
                    st.session_state.rec_filter = name
                    st.rerun()

    st.write("")

    weak = sorted(SUBJECT_SCORES.items(), key=lambda kv: kv[1])[:2]
    weak_text = " and ".join(f"<b>{n} ({s}%)</b>" for n, s in weak)
    st.markdown(flat(f'<div class="sm-alert-red"><h5>Weak subjects detected</h5>'
                     f'<p>Based on your quiz history, {weak_text} need the most attention. '
                     f'The highlighted cards below are tailored for you.</p></div>'),
                unsafe_allow_html=True)

    shown = [
        t for t in TECHNIQUES
        if (active == "All" or active in t["tags"])
        and (not query or query.lower() in t["title"].lower()
             or any(query.lower() in s.lower() for s in t["subjects"]))
    ]
    if not shown:
        st.markdown('<p style="color:#9ca3af;text-align:center;padding:36px 0;">'
                    'Nothing matches that filter.</p>', unsafe_allow_html=True)
        return

    plan = fb.get_study_plan(uid)
    applied_name = plan.get("technique") if isinstance(plan, dict) else None

    for row in range(0, len(shown), 2):
        cols = st.columns(2, gap="medium")
        for offset, col in enumerate(cols):
            i = row + offset
            if i >= len(shown):
                continue
            with col:
                _technique_card(shown[i], i, uid, applied_name)


def _schedule_table(t):
    rows = "".join(
        f'<div class="sm-sched-row">'
        f'<span class="sm-sched-day">{day}</span>'
        f'<span class="sm-sched-subj">{subj}</span>'
        f'<span class="sm-sched-dur">{dur}</span>'
        f'<span class="sm-sched-note">{note}</span>'
        f'</div>'
        for day, subj, dur, note in t["schedule"]
    )
    return flat(
        f'<div class="sm-sched">'
        f'<div class="sm-sched-head">{icon("clock", "#1d4ed8", 15)} Revision Schedule</div>'
        f'{rows}</div>')


def _learn_more(t):
    @st.dialog(t["title"], width="large")
    def _dlg():
        st.markdown(f'<p class="sm-tech-sub" style="font-size:14px !important;">{t["sub"]}</p>',
                    unsafe_allow_html=True)
        st.markdown(flat(f'<div class="sm-learn-why"><b>Why it works:</b> {t["why"]}</div>'),
                    unsafe_allow_html=True)
        st.write("")
        st.markdown('<p style="font-weight:700;color:#111827;margin:0 0 2px 0;">How to do it</p>',
                    unsafe_allow_html=True)
        for n, step in enumerate(t["steps"], 1):
            st.markdown(flat(f'<div class="sm-learn-step"><div class="sm-learn-num">{n}</div>'
                             f'<p>{step}</p></div>'), unsafe_allow_html=True)
        st.write("")
        st.markdown(flat(f'<div class="sm-row">'
                         f'{pill("&#8599; " + t["stat"], "#f0fdf4", "#16a34a")}'
                         f'{pill(t["level"], *DIFFICULTY[t["level"]])}</div>'),
                    unsafe_allow_html=True)
        st.write("")
        if st.button(f"Practice now in {t['target']}", type="primary",
                     width="stretch", icon=":material/arrow_forward:",
                     key=f"dlg_go_{t['title']}"):
            go_to(t["target"])
            st.rerun()
    _dlg()


def _technique_card(t, i, uid, applied_name):
    st.markdown(f'<style>.st-key-card_tech_{i} {{ border-top-color: {t["accent"]} !important; }}</style>',
                unsafe_allow_html=True)
    with card(f"tech_{i}"):
        d_bg, d_fg = DIFFICULTY[t["level"]]
        st.markdown(flat(
            f'<div class="sm-tech-head">'
            f'  <div class="sm-tech-icon" style="background:{t["icon_bg"]};">'
            f'{icon(t["icon"], t["icon_fg"], 21)}</div>'
            f'  <div><div class="sm-row-tight"><p class="sm-tech-title">{t["title"]}</p>'
            f'{pill(t["level"], d_bg, d_fg)}</div>'
            f'  <p class="sm-tech-sub">{t["sub"]}</p></div>'
            f'</div>'), unsafe_allow_html=True)

        st.markdown(" ".join(pill(tag, *TAG_STYLES[tag]) for tag in t["tags"]),
                    unsafe_allow_html=True)
        st.markdown(f'<p class="sm-rec-desc">{t["body"]}</p>', unsafe_allow_html=True)

        st.markdown(flat(
            f'<div class="sm-row">'
            f'<div>{" ".join(pill(s, "#eff6ff", "#2563eb") for s in t["subjects"])}</div>'
            f'<div>{pill("&#8599; " + t["stat"], "#f0fdf4", "#16a34a")}</div></div>'),
            unsafe_allow_html=True)

        st.markdown(flat(f'<div class="sm-protip"><b>Pro tip:</b> {t["tip"]}</div>'),
                    unsafe_allow_html=True)

        with st.expander("View Revision Schedule", icon=":material/calendar_month:"):
            st.markdown(_schedule_table(t), unsafe_allow_html=True)

        is_applied = applied_name == t["title"]
        b_l, b_r = st.columns([1, 1])
        with b_l:
            with st.container(key=f"btn_dark_apply_{i}"):
                label = "Applied" if is_applied else "Apply Technique"
                ic = ":material/check_circle:" if is_applied else ":material/auto_awesome:"
                if st.button(label, key=f"ap_{i}", width="stretch", icon=ic):
                    if is_applied:
                        fb.save_study_plan(uid, {})
                        st.toast(f"{t['title']} removed from your study plan.")
                    else:
                        fb.save_study_plan(uid, {
                            "technique": t["title"], "target": t["target"],
                            "applied": today_str(),
                            "schedule": [list(r) for r in t["schedule"]],
                        })
                        st.toast(f"{t['title']} is now your study plan - "
                                 f"check Upcoming Tasks on the Dashboard.")
                    st.rerun()
        with b_r:
            with st.container(key=f"btn_ghost_learn_{i}"):
                if st.button("Learn more", key=f"lm_{i}", width="stretch",
                             icon=":material/arrow_forward:"):
                    _learn_more(t)
