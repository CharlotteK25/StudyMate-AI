"""
Dashboard - the home screen. Layout mirrors the Figma mock:
greeting + date pill, four stat cards, then a 2/3 + 1/3 grid.
"""

from datetime import datetime

import streamlit as st
import pandas as pd
import altair as alt

from services import firebase_service as fb
from services import gemini_service as gem
from utils.state import go_to, today_str
from utils.theme import (
    card, card_heading, icon, flat, stat_card_html, progress_row_html,
    streak_chip_html,
    PRIMARY, PRIMARY_DARK, PRIMARY_SOFT, PRIMARY_PILL,
    BLUE, BLUE_SOFT, PURPLE, PURPLE_SOFT, ORANGE, ORANGE_SOFT,
)

SUBJECT_PROGRESS = {
    "Mathematics": 82, "Physics": 67, "Chemistry": 74, "History": 91, "Literature": 58,
}

QUICK_ACTIONS = [
    (":material/upload:",        "Upload Notes",       "Notes"),
    (":material/auto_awesome:",  "Generate Summary",   "Notes"),
    (":material/functions:",     "Generate Formulas",  "Notes"),
    (":material/credit_card:",   "Create Flashcards",  "Flashcards"),
    (":material/menu_book:",     "Start Quiz",         "Quiz"),
    (":material/forum:",         "Ask AI",             "AI Chat"),
]

UPCOMING_TASKS = [
    "Review biology summary",
    "Complete physics quiz",
    "Revise flashcard deck",
    "Upload chemistry notes",
]

DAY_LETTERS = ["M", "T", "W", "T", "F", "S", "S"]
CHART_COLORS = {"Math": "#22c55e", "Physics": "#3b82f6", "Chemistry": "#ec4899"}


def _greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    return "Good afternoon" if hour < 18 else "Good evening"


def _long_date() -> str:
    """e.g. 'Friday, June 5, 2026' - built without %-d so it works on Windows."""
    now = datetime.now()
    return f"{now.strftime('%A, %B')} {now.day}, {now.year}"


def _quiz_performance_chart():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    df = pd.DataFrame({
        "Day": days * 3,
        "Score": [70, 75, 68, 82, 79, 88, 91,
                  55, 60, 72, 67, 80, 75, 83,
                  62, 68, 65, 74, 71, 80, 85],
        "Subject": ["Math"] * 7 + ["Physics"] * 7 + ["Chemistry"] * 7,
    })
    chart = (
        alt.Chart(df)
        .mark_line(strokeWidth=2.5, interpolate="monotone")
        .encode(
            x=alt.X("Day", sort=days, title=None,
                    axis=alt.Axis(grid=False, domain=False, tickSize=0, labelAngle=0,
                                  labelColor="#9ca3af", labelFontSize=12, labelPadding=10)),
            y=alt.Y("Score", title=None, scale=alt.Scale(domain=[40, 100]),
                    axis=alt.Axis(values=[40, 55, 70, 85, 100], gridColor="#f1f3f4",
                                  domain=False, tickSize=0, labelColor="#9ca3af",
                                  labelFontSize=12, labelPadding=8)),
            color=alt.Color(
                "Subject",
                scale=alt.Scale(domain=list(CHART_COLORS), range=list(CHART_COLORS.values())),
                legend=alt.Legend(orient="bottom", title=None, symbolType="stroke",
                                  labelColor="#6b7280", labelFontSize=12),
            ),
        )
        .properties(height=230, background="transparent")
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")


def render_dashboard():
    uid = st.session_state.user["uid"]
    first_name = st.session_state.user["name"].split(" ")[0]

    head_l, head_r = st.columns([3, 1.15], vertical_alignment="center")
    with head_l:
        st.markdown(f'<p class="sm-title">{_greeting()}, {first_name} &#128075;</p>',
                    unsafe_allow_html=True)
        st.markdown('<p class="sm-subtitle">Here\'s your study summary for today</p>',
                    unsafe_allow_html=True)
    with head_r:
        st.markdown(f'<div class="sm-date-pill"><span class="sm-dot"></span>{_long_date()}</div>',
                    unsafe_allow_html=True)
    st.write("")

    notes = fb.get_notes(uid)
    decks = fb.get_flashcard_decks(uid)
    quiz_results = fb.get_quiz_results(uid)

    num_summaries = len([n for n in notes if n.get("status") == "done"])
    num_flashcards = sum(len(cards) for cards in decks.values())
    notes_today = len([n for n in notes if n.get("date") == today_str()])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card_html("file", PRIMARY_DARK, PRIMARY_PILL, "+12%", len(notes),
                                   "Recent Notes", f"{notes_today} added today"),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card_html("card", "#2563eb", BLUE_SOFT, "+8%", num_flashcards,
                                   "Flashcards Generated", f"{num_flashcards} reviewed today"),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card_html("upload", "#7e22ce", PURPLE_SOFT, "+5%", len(notes),
                                   "Files Uploaded", f"{notes_today} uploaded today"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(stat_card_html("brain", "#c2410c", ORANGE_SOFT, "+18%", num_summaries,
                                   "AI Summaries", f"{num_summaries} generated today"),
                    unsafe_allow_html=True)

    st.write("")

    main_col, side_col = st.columns([2, 1], gap="medium")

    with main_col:
        with card("study_progress"):
            card_heading("Study Progress", "% completed this week", "layers", PRIMARY_DARK)
            for subject, percent in SUBJECT_PROGRESS.items():
                st.markdown(progress_row_html(subject, percent, PRIMARY), unsafe_allow_html=True)

        with card("quiz_perf"):
            h_l, h_r = st.columns([3, 1], vertical_alignment="center")
            with h_l:
                st.markdown('<p class="sm-card-title">Quiz Performance</p>'
                            '<p class="sm-card-sub">Score trends this week</p>',
                            unsafe_allow_html=True)
            with h_r:
                st.markdown('<div style="text-align:right;"><span class="sm-badge">Weekly</span></div>',
                            unsafe_allow_html=True)
            _quiz_performance_chart()

        with card("quick_actions"):
            card_heading("Quick Actions", "Jump into your study tasks", "sparkle", PRIMARY_DARK)
            for row_start in (0, 3):
                cols = st.columns(3)
                for offset, col in enumerate(cols):
                    idx = row_start + offset
                    micon, label, target = QUICK_ACTIONS[idx]
                    with col:
                        with st.container(key=f"qa_{idx}"):
                            if st.button(f"{micon}\n{label}", key=f"qa_btn_{idx}",
                                         width="stretch"):
                                go_to(target)
                                st.rerun()

    with side_col:
        with card("streak"):
            card_heading("Learning Streak", "", "flame", "#f97316")
            streak_days = len(quiz_results) if quiz_results else 3
            st.markdown(f'<span class="sm-big-number">{streak_days}</span>'
                        f'<span class="sm-big-unit">days</span>', unsafe_allow_html=True)
            st.markdown('<p class="sm-card-sub" style="margin:6px 0 0 0;">Learning days this week</p>',
                        unsafe_allow_html=True)
            today_index = datetime.now().weekday()
            chips = "".join(
                streak_chip_html(letter, active=i < today_index, is_today=i == today_index)
                for i, letter in enumerate(DAY_LETTERS)
            )
            st.markdown(f'<div class="sm-streak-row">{chips}</div>', unsafe_allow_html=True)

        with card("goal"):
            card_heading("Today's Study Goal", "", "target", PRIMARY_DARK)
            goal = st.session_state.study_goal_hours
            done = st.session_state.study_hours_today
            percent = round(min(done / goal, 1.0) * 100) if goal else 0
            st.markdown(progress_row_html(f"{done} / {goal} hours", percent, PRIMARY),
                        unsafe_allow_html=True)

        with card("tasks"):
            plan = fb.get_study_plan(uid)
            if isinstance(plan, dict) and plan.get("schedule"):
                card_heading("Upcoming Tasks", plan.get("technique", ""), "clock", "#2563eb")
                tasks = [f"{day}: {subj} - {note} ({dur})"
                         for day, subj, dur, note in plan["schedule"]][:5]
            else:
                card_heading("Upcoming Tasks", "", "clock", "#2563eb")
                tasks = UPCOMING_TASKS
            with st.container(key="tasklist"):
                for i, label in enumerate(tasks):
                    st.checkbox(label, key=f"task_{i}", value=(i == 0))

        with card("ai_rec"):
            r_l, r_r = st.columns([4, 1], vertical_alignment="center")
            with r_l:
                st.markdown(flat(
                    f'<div class="sm-row-tight">'
                    f'  <div class="sm-rec-icon">{icon("sparkle", "#7e22ce", 17)}</div>'
                    f'  <p class="sm-card-title">AI Recommendation</p></div>'),
                    unsafe_allow_html=True)
            with r_r:
                with st.container(key="recrefresh"):
                    refresh = st.button("", key="ai_rec_refresh", icon=":material/refresh:")

            if "dash_recommendation" not in st.session_state or refresh:
                st.session_state.dash_recommendation = gem.generate_recommendation(
                    SUBJECT_PROGRESS, quiz_results
                )
                if refresh:
                    st.rerun()

            st.markdown(f'<p style="font-size:13.5px;color:#4b5563;line-height:1.6;margin:8px 0 14px 0;">'
                        f'{st.session_state.dash_recommendation}</p>', unsafe_allow_html=True)

            b_l, b_r = st.columns([1, 1.1], vertical_alignment="center")
            with b_l:
                with st.container(key="apply_tip"):
                    if st.button("Apply Tip", key="apply_tip_btn", width="stretch"):
                        go_to("Recommendations")
                        st.rerun()
            with b_r:
                with st.container(key="dismiss_tip"):
                    if st.button("Dismiss", key="dismiss_tip_btn", width="stretch"):
                        st.session_state.dash_recommendation = gem.generate_recommendation(
                            SUBJECT_PROGRESS, quiz_results
                        )
                        st.rerun()

        with card("uploaded"):
            u_l, u_r = st.columns([2, 1], vertical_alignment="center")
            with u_l:
                st.markdown('<p class="sm-card-title">Progress Uploaded</p>', unsafe_allow_html=True)
            with u_r:
                st.markdown('<div style="text-align:right;"><span class="sm-badge-blue">This Month</span></div>',
                            unsafe_allow_html=True)
            total_files = max(len(notes), 1)
            upload_percent = round(num_summaries / total_files * 100)
            st.markdown(f'<div style="margin-top:12px;"><span class="sm-big-number">{upload_percent}</span>'
                        f'<span class="sm-big-unit">%</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sm-progress-track" style="margin-top:12px;">'
                        f'<div class="sm-progress-fill" style="width:{upload_percent}%;background:{BLUE};">'
                        f'</div></div>', unsafe_allow_html=True)
            st.markdown(f'<p class="sm-card-sub" style="margin:0;">{num_summaries} of {total_files} '
                        f'files reviewed</p>', unsafe_allow_html=True)
