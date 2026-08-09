"""Progress Analytics - metric cards, charts, mastery breakdown, AI insight."""

import streamlit as st
import pandas as pd
import altair as alt

from services import firebase_service as fb
from services import gemini_service as gem
from utils.theme import (
    flat, icon, card, card_heading, section_title, metric_card_html, progress_row_html,
    PRIMARY, PRIMARY_DARK, PRIMARY_PILL, BLUE, BLUE_SOFT, PURPLE_SOFT, ORANGE_SOFT,
)

SUBJECTS = {
    "Biology":   (82, "#22c55e"),
    "Chemistry": (67, "#60a5fa"),
    "Physics":   (74, "#f472b6"),
    "Maths":     (91, "#fb923c"),
    "History":   (58, "#a78bfa"),
}


def _donut(scores):
    df = pd.DataFrame({
        "Subject": list(scores),
        "Score": [v[0] for v in scores.values()],
        "Color": [v[1] for v in scores.values()],
    })
    total = df["Score"].sum()
    df["Share"] = (df["Score"] / total * 100).round(0)
    avg = round(df["Score"].mean())

    arc = (
        alt.Chart(df)
        .mark_arc(innerRadius=54, outerRadius=84, cornerRadius=3, stroke="#fff", strokeWidth=2)
        .encode(
            theta=alt.Theta("Score:Q", stack=True),
            color=alt.Color("Subject:N",
                            scale=alt.Scale(domain=list(scores), range=[v[1] for v in scores.values()]),
                            legend=None),
            tooltip=["Subject", "Score"],
        )
    )
    centre = (
        alt.Chart(pd.DataFrame({"t": [f"{avg}%"]}))
        .mark_text(fontSize=26, fontWeight=700, color="#111827", dy=-6)
        .encode(text="t:N")
    )
    label = (
        alt.Chart(pd.DataFrame({"t": ["avg"]}))
        .mark_text(fontSize=12, color="#9ca3af", dy=16)
        .encode(text="t:N")
    )
    st.altair_chart((arc + centre + label).properties(height=210, background="transparent").configure_view(strokeWidth=0),
                    width="stretch")


def _hours_chart():
    df = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Hours": [2.2, 4.0, 3.0, 5.0, 3.6, 6.0, 2.0],
    })
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=22)
        .encode(
            x=alt.X("Day", sort=list(df["Day"]), title=None,
                    axis=alt.Axis(grid=False, domain=False, tickSize=0,
                                  labelAngle=0, labelColor="#9ca3af", labelFontSize=11.5, labelPadding=8)),
            y=alt.Y("Hours", title=None, scale=alt.Scale(domain=[0, 8]),
                    axis=alt.Axis(values=[0, 2, 4, 6, 8], gridColor="#f1f3f4", gridDash=[3, 3],
                                  domain=False, tickSize=0, labelColor="#9ca3af", labelFontSize=11.5)),
            color=alt.Color("Hours:Q", scale=alt.Scale(range=["#a7f3c8", "#22c55e"]), legend=None),
        )
        .properties(height=215, background="transparent").configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")


def _weekly_chart():
    df = pd.DataFrame({
        "Week": [f"Wk {i}" for i in range(1, 8)],
        "Score": [60, 66, 70, 74, 78, 82, 88],
    })
    base = alt.Chart(df).encode(
        x=alt.X("Week", sort=list(df["Week"]), title=None,
                axis=alt.Axis(grid=False, domain=False, tickSize=0,
                              labelAngle=0, labelColor="#9ca3af", labelFontSize=11.5, labelPadding=8)),
        y=alt.Y("Score", title=None, scale=alt.Scale(domain=[40, 100]),
                axis=alt.Axis(values=[40, 55, 70, 85, 100], gridColor="#f1f3f4", gridDash=[3, 3],
                              domain=False, tickSize=0, labelColor="#9ca3af", labelFontSize=11.5)),
    )
    area = base.mark_area(interpolate="monotone", opacity=0.16, color=BLUE)
    line = base.mark_line(interpolate="monotone", strokeWidth=2.5, color=BLUE)
    dots = base.mark_point(filled=True, size=48, color=BLUE)
    st.altair_chart((area + line + dots).properties(height=215, background="transparent").configure_view(strokeWidth=0),
                    width="stretch")


def render_analytics():
    uid = st.session_state.user["uid"]
    quiz_results = fb.get_quiz_results(uid)

    h_l, h_r1, h_r2 = st.columns([3, 0.8, 0.8], vertical_alignment="center")
    with h_l:
        st.markdown('<p class="sm-title">Progress Analytics</p>', unsafe_allow_html=True)
        st.markdown('<p class="sm-subtitle">Track your study performance over time</p>',
                    unsafe_allow_html=True)
    view = st.session_state.setdefault("analytics_view", "Weekly")
    with h_r1:
        with st.container(key="seg_view_w"):
            if st.button("Weekly View", width="stretch",
                         type="primary" if view == "Weekly" else "secondary"):
                st.session_state.analytics_view = "Weekly"
                st.rerun()
    with h_r2:
        with st.container(key="seg_view_m"):
            if st.button("Monthly View", width="stretch",
                         type="primary" if view == "Monthly" else "secondary"):
                st.session_state.analytics_view = "Monthly"
                st.rerun()
    st.write("")

    avg_score = (round(sum(r.get("percent", 0) for r in quiz_results) / len(quiz_results))
                 if quiz_results else 83)
    metrics = [
        ("flame",  "#f97316", ORANGE_SOFT,  "44",   "Learning Streak",      "days in a row",  "+12%", "up"),
        ("card",   "#2563eb", BLUE_SOFT,    "25",   "Flashcards Completed", "this week",      "+8%",  "up"),
        ("book",   "#7e22ce", PURPLE_SOFT,  "1031", "Study Sessions",       "total sessions", "+5%",  "up"),
        ("target", PRIMARY_DARK, PRIMARY_PILL, f"{avg_score}%", "Avg Quiz Score", "across all quizzes", "+4%", "up"),
        ("clock",  "#2563eb", BLUE_SOFT,    "26.6h", "Hours Studied",       "this week",      "-3%",  "down"),
        ("sparkle", "#db2777", "#fce7f3",   str(len(quiz_results) or 12), "Quizzes Taken", "this week", "0%", "flat"),
    ]
    for col, m in zip(st.columns(6), metrics):
        with col:
            st.markdown(metric_card_html(*m), unsafe_allow_html=True)

    st.write("")

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        with card("hours"):
            card_heading("Study Hours", "Hours per day this week")
            _hours_chart()
    with c2:
        with card("weekly"):
            card_heading("Weekly Progress", "Average quiz score over time")
            _weekly_chart()
    with c3:
        with card("mastery"):
            card_heading("Topic Mastery", "Scores by subject")
            d_l, d_r = st.columns([1.1, 1], vertical_alignment="center")
            with d_l:
                _donut(SUBJECTS)
            with d_r:
                for name, (score, color) in SUBJECTS.items():
                    st.markdown(flat(
                        f'<div class="sm-mastery-row">'
                        f'<span class="sm-mastery-dot" style="background:{color};"></span>'
                        f'<span style="flex:1;">{name}</span>'
                        f'<b style="color:#111827;">{score}%</b></div>'), unsafe_allow_html=True)

    st.write("")

    b_l, b_r = st.columns([2, 1], gap="medium")
    with b_l:
        with card("breakdown"):
            card_heading("Subject Breakdown", "Individual mastery scores")
            for name, (score, color) in SUBJECTS.items():
                st.markdown(progress_row_html(name, score, color), unsafe_allow_html=True)

    with b_r:
        with card("insight"):
            card_heading("AI Insight", "Based on your weekly data")
            best = max(SUBJECTS.items(), key=lambda kv: kv[1][0])
            worst = min(SUBJECTS.items(), key=lambda kv: kv[1][0])
            items = [
                ("&#127942;", "Top subject", f"{best[0]} at {best[1][0]}% &mdash; keep the momentum."),
                ("&#9889;", "Needs attention", f"{worst[0]} at {worst[1][0]}% &mdash; try 2 extra flashcard sessions."),
                ("&#128200;", "Score trend", "Your quiz scores improved by 26% over this 7-week period."),
            ]
            for glyph, title, body in items:
                st.markdown(flat(f'<div class="sm-insight-item"><div style="font-size:19px;">{glyph}</div>'
                                 f'<div><h5>{title}</h5><p>{body}</p></div></div>'),
                            unsafe_allow_html=True)

            if "analytics_insight" not in st.session_state:
                st.session_state.analytics_insight = gem.generate_recommendation(
                    {k: v[0] for k, v in SUBJECTS.items()}, quiz_results)
            with st.container(key="btn_ghost_refreshinsight"):
                if st.button("Refresh insight", width="stretch", icon=":material/refresh:"):
                    st.session_state.analytics_insight = gem.generate_recommendation(
                        {k: v[0] for k, v in SUBJECTS.items()}, quiz_results)
                    st.rerun()
