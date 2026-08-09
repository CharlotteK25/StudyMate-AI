"""
First-run demo content.

The Flashcards and AI Chat screens are designed around having material in
them - an empty account renders an empty-state that looks nothing like the
mockups. This seeds one sample deck and a few chat threads the first time a
user lands on those pages, so the app demos the way it was designed.

Nothing here overwrites real data: each seeder bails out if the user
already has content of that kind.
"""

import streamlit as st

from services import firebase_service as fb

SEED_VERSION = 3

SAMPLE_DECK_NAME = "Biology_Lecture_3"

SAMPLE_CARDS = [
    {"front": "What is the powerhouse of the cell?",
     "back": "The mitochondria - it generates ATP through cellular respiration."},
    {"front": "What makes the cell membrane selectively permeable?",
     "back": "Its phospholipid bilayer, which lets small non-polar molecules pass "
             "while blocking large or charged ones."},
    {"front": "Which organelle synthesises proteins?",
     "back": "The ribosome, either free in the cytoplasm or bound to the rough "
             "endoplasmic reticulum."},
    {"front": "What is osmosis?",
     "back": "The movement of water across a semi-permeable membrane, from lower "
             "to higher solute concentration."},
    {"front": "How do prokaryotic and eukaryotic cells differ?",
     "back": "Eukaryotes have a nucleus and membrane-bound organelles; prokaryotes "
             "have neither and keep their DNA in the cytoplasm."},
    {"front": "What does the Golgi apparatus do?",
     "back": "It modifies, sorts and packages proteins from the ER for secretion "
             "or delivery elsewhere in the cell."},
]

SAMPLE_CHATS = {
    "Chapter 3 Summary": [
        {"role": "user", "content": "Can you summarise Chapter 3 of my Biology notes?"},
        {"role": "assistant", "content":
            "Sure! Chapter 3 covers **Cell Structure and Function**. Key topics include:\n\n"
            "- The cell membrane and its selective permeability\n"
            "- Organelles: nucleus, mitochondria, ribosomes, endoplasmic reticulum, "
            "and Golgi apparatus\n"
            "- Differences between prokaryotic and eukaryotic cells\n"
            "- Cell transport mechanisms: diffusion, osmosis, and active transport\n\n"
            "Would you like me to go deeper on any specific section?"},
    ],
    "Explain Concept X": [
        {"role": "user", "content": "What is active transport?"},
        {"role": "assistant", "content":
            "Active transport moves molecules **against** their concentration gradient, "
            "which costs energy in the form of ATP. The sodium-potassium pump is the "
            "classic example — it pushes 3 Na⁺ out for every 2 K⁺ in."},
    ],
    "Explain Concept Y": [
        {"role": "user", "content": "How does diffusion differ from osmosis?"},
        {"role": "assistant", "content":
            "Both are passive, but diffusion describes any solute spreading from high to "
            "low concentration, while osmosis is specifically **water** moving across a "
            "semi-permeable membrane."},
    ],
    "Formula Recap": [
        {"role": "assistant", "content":
            "Hi! I'm StudyMate AI. What are you studying today?"},
    ],
    "Photosynthesis Recap": [
        {"role": "assistant", "content":
            "Photosynthesis in one line: 6CO₂ + 6H₂O + light → "
            "C₆H₁₂O₆ + 6O₂. Ask me to break down the "
            "light-dependent and light-independent stages any time."},
    ],
    "Week 5 Revision Plan": [
        {"role": "assistant", "content":
            "Your Week 5 plan: Mon — cell transport flashcards, Wed — "
            "practice quiz, Fri — summarise lecture notes. Want me to adjust it?"},
    ],
}


def seed_flashcards(uid: str):
    if st.session_state.get("_seeded_decks"):
        return
    st.session_state._seeded_decks = True
    if fb.get_flashcard_decks(uid):
        return
    fb.save_flashcard_deck(uid, SAMPLE_DECK_NAME, SAMPLE_CARDS)
    st.session_state.active_deck = SAMPLE_DECK_NAME
    st.session_state.fc_index = 0


def _stale(uid: str) -> bool:
    """True if this account was seeded by an older build of the demo data."""
    from services import local_store as ls
    meta = ls.get_collection("seed_meta", uid)
    version = meta.get("version") if isinstance(meta, dict) else None
    return version != SEED_VERSION


def _mark_seeded(uid: str):
    from services import local_store as ls
    ls.set_collection_item("seed_meta", uid, {"version": SEED_VERSION})


def seed_chats(uid: str):
    if st.session_state.get("_seeded_chats"):
        return
    st.session_state._seeded_chats = True

    existing = fb.get_chat_sessions(uid) or {}
    has_content = any(msgs for msgs in existing.values())

    if has_content and not _stale(uid):
        return
    if has_content and _stale(uid):
        from services import local_store as ls
        kept = {n: m for n, m in existing.items() if n not in SAMPLE_CHATS}
        ls.set_collection_item("chat_history", uid, kept)

    for name, messages in SAMPLE_CHATS.items():
        for message in messages:
            fb.save_chat_message(uid, name, message)
    _mark_seeded(uid)
    st.session_state.active_chat = "Chapter 3 Summary"
