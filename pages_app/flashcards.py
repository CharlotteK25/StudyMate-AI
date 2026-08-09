"""Flashcards - study one card at a time with a card-picker sidebar."""

import streamlit as st

from services import firebase_service as fb
from services import gemini_service as gem
from services import demo_seed
from utils.theme import flat, icon, pill, card, progress_row_html, PRIMARY, PRIMARY_DARK


def _deck_state(deck: str) -> dict:
    """Per-deck learned/flagged sets, kept in session state."""
    store = st.session_state.setdefault("fc_progress", {})
    return store.setdefault(deck, {"learned": set(), "flagged": set()})


def _generator_panel(uid, notes, decks):
    with st.expander("Generate a new deck from your notes", expanded=not decks):
        if not notes:
            st.caption("Upload notes with readable text first (Notes page).")
        else:
            src = st.selectbox("Source note", [n["name"] for n in notes], key="fc_src")
            count = st.slider("Number of cards", 4, 20, 8, key="fc_count")
            if st.button("Generate Flashcards", type="primary", key="fc_gen"):
                note = next(n for n in notes if n["name"] == src)
                with st.spinner("Generating flashcards..."):
                    cards = gem.generate_flashcards(note["text"], num_cards=count)
                fb.save_flashcard_deck(uid, src, cards)
                st.session_state.active_deck = src
                st.session_state.fc_index = 0
                st.rerun()

        st.divider()
        st.caption("Or add a card by hand")
        name = st.text_input("Deck name", value="My Deck", key="fc_manual_deck")
        front = st.text_input("Front (question)", key="fc_front")
        back = st.text_area("Back (answer)", key="fc_back", height=68)
        if st.button("Add Card", key="fc_add"):
            if front and back:
                existing = decks.get(name, [])
                existing.append({"front": front, "back": back})
                fb.save_flashcard_deck(uid, name, existing)
                st.rerun()
            else:
                st.error("Fill in both sides of the card.")


def render_flashcards():
    uid = st.session_state.user["uid"]
    demo_seed.seed_flashcards(uid)
    decks = fb.get_flashcard_decks(uid)
    notes = [n for n in fb.get_notes(uid) if n.get("text")]

    if not decks:
        st.markdown('<p class="sm-title">Flashcards</p>', unsafe_allow_html=True)
        st.markdown('<p class="sm-subtitle">Generate a deck from your notes to start studying</p>',
                    unsafe_allow_html=True)
        st.write("")
        _generator_panel(uid, notes, decks)
        return

    deck_names = list(decks)
    active = st.session_state.get("active_deck")
    if active not in deck_names:
        active = deck_names[0]
        st.session_state.active_deck = active
    cards = decks[active]
    prog = _deck_state(active)

    idx = st.session_state.setdefault("fc_index", 0) % len(cards)
    flipped = st.session_state.setdefault("fc_flipped", False)
    learned = len(prog["learned"])
    percent = round(learned / len(cards) * 100)

    h_l, h_r1, h_r2 = st.columns([3, 1.1, 1], vertical_alignment="center")
    with h_l:
        st.markdown('<p class="sm-title">Flashcards</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="sm-subtitle">{learned} of {len(cards)} cards learned</p>',
                    unsafe_allow_html=True)
    with h_r1:
        st.markdown(flat(f'<div style="text-align:right;">'
                         f'{pill(f"{percent}% complete", "#ffffff", "#374151", "book")}</div>'),
                    unsafe_allow_html=True)
    with h_r2:
        with st.container(key="btn_dark_genmore"):
            if st.button("Generate More", width="stretch", icon=":material/auto_awesome:"):
                st.session_state.fc_show_gen = not st.session_state.get("fc_show_gen", False)
                st.rerun()

    p_l, p_r = st.columns([9, 1], vertical_alignment="center")
    with p_l:
        st.markdown(flat(f'<div class="sm-progress-track" style="margin:6px 0 18px 0;">'
                         f'<div class="sm-progress-fill" style="width:{percent}%;'
                         f'background:{PRIMARY};"></div></div>'), unsafe_allow_html=True)
    with p_r:
        st.markdown(f'<p class="sm-flash-meta" style="text-align:right;">{idx+1} / {len(cards)}</p>',
                    unsafe_allow_html=True)

    if st.session_state.get("fc_show_gen"):
        _generator_panel(uid, notes, decks)

    main, side = st.columns([2.9, 1], gap="medium")

    with main:
        with card("flash"):
            t_l, t_r = st.columns([2, 1], vertical_alignment="center")
            with t_l:
                st.markdown(pill(active[:22], "#f0fdf4", "#16a34a"), unsafe_allow_html=True)
            with t_r:
                st.markdown('<p class="sm-flash-meta" style="text-align:right;">Click to flip</p>',
                            unsafe_allow_html=True)

            label = "Answer" if flipped else "Question"
            body = cards[idx]["back"] if flipped else cards[idx]["front"]
            st.markdown(f'<p class="sm-label" style="text-align:center;margin-top:26px;">{label}</p>',
                        unsafe_allow_html=True)
            st.markdown(f'<p class="sm-flash-q">{body}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="sm-flash-meta">Card {idx+1}</p>', unsafe_allow_html=True)

        a_l, a_r, _ = st.columns([1, 1, 1.4])
        with a_l:
            with st.container(key="btn_green_learn"):
                if st.button("Mark as Learned", width="stretch", icon=":material/check_circle:"):
                    prog["learned"].add(idx)
                    st.rerun()
        with a_r:
            with st.container(key="btn_orange_flag"):
                if st.button("Flag for Review", width="stretch", icon=":material/flag:"):
                    prog["flagged"].add(idx)
                    st.rerun()

        n1, n2, n3, _ = st.columns([1, 1, 1, 0.8])
        with n1:
            with st.container(key="btn_ghost_prev"):
                if st.button("Previous Card", width="stretch", icon=":material/chevron_left:"):
                    st.session_state.fc_index = (idx - 1) % len(cards)
                    st.session_state.fc_flipped = False
                    st.rerun()
        with n2:
            with st.container(key="btn_ghost_flip"):
                if st.button("Flip Card", width="stretch", icon=":material/refresh:"):
                    st.session_state.fc_flipped = not flipped
                    st.rerun()
        with n3:
            with st.container(key="btn_dark_next"):
                if st.button("Next Card", width="stretch", icon=":material/chevron_right:"):
                    st.session_state.fc_index = (idx + 1) % len(cards)
                    st.session_state.fc_flipped = False
                    st.rerun()

    with side:
        with card("cardlist"):
            st.markdown('<p class="sm-label">All cards</p>', unsafe_allow_html=True)
            for row in range(0, len(cards), 2):
                cols = st.columns(2)
                for offset, col in enumerate(cols):
                    i = row + offset
                    if i >= len(cards):
                        continue
                    mark = ""
                    if i in prog["learned"]:
                        mark = '<span style="color:#22c55e;">&#9679;</span>'
                    elif i in prog["flagged"]:
                        mark = '<span style="color:#fb923c;">&#9679;</span>'
                    with col:
                        with st.container(key=f"cardsel_{i}"):
                            if st.button(f"Card {i+1}", key=f"cs_{i}", width="stretch",
                                         type="primary" if i == idx else "secondary"):
                                st.session_state.fc_index = i
                                st.session_state.fc_flipped = False
                                st.rerun()
                        if mark:
                            st.markdown(flat(f'<div style="text-align:right;margin-top:-52px;'
                                             f'margin-right:8px;font-size:11px;">{mark}</div>'),
                                        unsafe_allow_html=True)

            st.markdown(flat(f'<div class="sm-row" style="margin-top:14px;font-size:11.5px;'
                             f'color:#9ca3af;"><span>{learned} learned</span>'
                             f'<span><span style="color:#22c55e;">&#9679;</span> done &nbsp;'
                             f'<span style="color:#fb923c;">&#9679;</span> flagged</span></div>'),
                        unsafe_allow_html=True)

        if len(deck_names) > 1:
            choice = st.selectbox("Deck", deck_names, index=deck_names.index(active), key="deck_sel")
            if choice != active:
                st.session_state.active_deck = choice
                st.session_state.fc_index = 0
                st.rerun()
