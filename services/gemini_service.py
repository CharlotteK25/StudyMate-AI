"""
Google Gemini API wrapper powering every AI feature of StudyMate AI:
  - Note summarisation
  - Quiz generation
  - Flashcard recommendation / generation
  - Chatbot
  - Personalised study recommendations

If GEMINI_API_KEY is not present in .streamlit/secrets.toml, every function
falls back to a deterministic, offline NLP-based implementation (see
services/nlp_utils.py) so the app is always demoable, e.g. during a viva
with no internet access.
"""

import json
import random
import re
import time

import streamlit as st

from services import nlp_utils as nlp

def _get_secret(key, default=None):
    """Read a value from st.secrets, safely returning `default` if no
    secrets.toml file exists at all (st.secrets raises in that case
    instead of behaving like a normal empty dict)."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


GEMINI_API_KEY = _get_secret("GEMINI_API_KEY", "")
GEMINI_MODEL = _get_secret("GEMINI_MODEL", "gemini-flash-latest")

INIT_ERROR = ""
LAST_ERROR = ""

USE_GEMINI = bool(GEMINI_API_KEY)
_client = None

if USE_GEMINI:
    try:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        INIT_ERROR = f"{type(e).__name__}: {e}"
        USE_GEMINI = False


FALLBACK_MODELS = ("gemini-flash-latest", "gemini-flash-lite-latest")

_active_model = GEMINI_MODEL


def active_model() -> str:
    """The model actually answering right now - may differ from GEMINI_MODEL
    if the configured one turned out to be retired or out of quota."""
    return _active_model


def _model_candidates():
    """Configured model first, then the known-good aliases, no duplicates."""
    ordered = []
    for name in (GEMINI_MODEL,) + FALLBACK_MODELS:
        if name and name not in ordered:
            ordered.append(name)
    return ordered


def _model_unusable(e: Exception) -> bool:
    """True when the failure is about *this model* rather than the key or the
    network - i.e. worth retrying on a different model."""
    text = str(e)
    return any(marker in text for marker in
               ("RESOURCE_EXHAUSTED", "429", "NOT_FOUND", "404"))


def status() -> tuple:
    """(ok: bool, message: str) - what to show the user about Gemini right now."""
    if not GEMINI_API_KEY:
        return False, "No GEMINI_API_KEY in .streamlit/secrets.toml - using offline NLP mode."
    if INIT_ERROR:
        return False, f"Gemini could not start: {INIT_ERROR}"
    if LAST_ERROR:
        return False, LAST_ERROR
    if _active_model != GEMINI_MODEL:
        return True, (f"Gemini connected using '{_active_model}'. The configured model "
                      f"'{GEMINI_MODEL}' is retired or out of free-tier quota, so the app "
                      f"switched automatically.")
    return True, f"Gemini connected ({_active_model})."


def render_notice():
    """Show, once, any Gemini failure recorded since the last render.

    The generate buttons all call st.rerun() immediately, which would wipe a
    warning drawn inline - so failures are stashed in session_state and drawn
    at the top of the next run instead. Without this a quota error is invisible
    and just looks like the AI got worse."""
    try:
        msg = st.session_state.pop("_ai_notice", None)
    except Exception:
        return
    if msg:
        st.warning(msg, icon=":material/cloud_off:")


def _remember(msg: str):
    """Queue a warning, but only the first time this session - a persistent
    quota problem otherwise repeats the same banner after every generation."""
    try:
        seen = st.session_state.setdefault("_ai_notice_seen", set())
        if msg in seen:
            return
        seen.add(msg)
        st.session_state["_ai_notice"] = msg
    except Exception:
        pass


def _friendly_error(e: Exception) -> str:
    """Turn an SDK exception into something a user can act on."""
    text = str(e)
    tried = ", ".join(f"'{m}'" for m in _model_candidates())
    if "RESOURCE_EXHAUSTED" in text or "429" in text:
        return (f"Gemini quota is exhausted on every model tried ({tried}). Free-tier quota "
                f"resets daily - wait it out, or add billing to the key's Google Cloud "
                f"project. Using offline mode meanwhile.")
    if "API_KEY_INVALID" in text or "API key not valid" in text:
        return "Gemini API key is invalid - check GEMINI_API_KEY in .streamlit/secrets.toml."
    if "NOT_FOUND" in text or "404" in text:
        return (f"None of these Gemini models are available to this API key ({tried}). "
                f"Check the key at https://aistudio.google.com/apikey.")
    if "PERMISSION_DENIED" in text or "403" in text:
        return "Gemini refused this key (PERMISSION_DENIED). Check the key's project and restrictions."
    if "UNAVAILABLE" in text or "503" in text:
        return (f"Gemini is temporarily overloaded (503) and didn't answer after "
                f"{_MAX_ATTEMPTS} tries. This clears on its own - press the button again. "
                f"Used offline mode for now.")
    return f"Gemini call failed ({type(e).__name__}): {text[:200]}"


def _extract_json(raw: str):
    """Gemini often wraps JSON in ```json fences - strip them before parsing."""
    cleaned = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
    if fenced:
        cleaned = fenced.group(1)
    return json.loads(cleaned.strip())


_TRANSIENT = ("503", "UNAVAILABLE", "500", "INTERNAL", "DEADLINE_EXCEEDED")
_MAX_ATTEMPTS = 3


def _is_transient(e: Exception) -> bool:
    text = str(e)
    return any(marker in text for marker in _TRANSIENT)


def _call_gemini(prompt: str) -> str:
    """Ask Gemini, moving to a fallback model if the configured one is retired
    or out of quota. Raises only when every candidate fails; callers then
    record LAST_ERROR and fall back to offline NLP."""
    global LAST_ERROR, _active_model

    candidates = _model_candidates()
    if _active_model in candidates:
        candidates.remove(_active_model)
    candidates.insert(0, _active_model)

    last_exc = None
    for model in candidates:
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                response = _client.models.generate_content(model=model, contents=prompt)
                if model != _active_model:
                    _remember(f"Model '{_active_model}' is retired or out of free-tier "
                              f"quota - StudyMate switched to '{model}' for this session.")
                    _active_model = model
                LAST_ERROR = ""
                return response.text or ""
            except Exception as e:
                last_exc = e
                if attempt < _MAX_ATTEMPTS and _is_transient(e):
                    time.sleep(0.8 * attempt)
                    continue
                break
        if not _model_unusable(last_exc):
            break

    LAST_ERROR = _friendly_error(last_exc)
    _remember(LAST_ERROR)
    raise last_exc


def generate_summary(text: str) -> dict:
    """Returns {"summary": str, "keywords": [str]}"""
    if USE_GEMINI:
        prompt = f"""You are an expert study assistant. Summarise the following
study notes into a concise, well-structured summary (150-250 words) a student
can revise from quickly. Also extract the 8 most important keywords/terms.

Respond ONLY with valid JSON in this exact shape:
{{"summary": "...", "keywords": ["...", "..."]}}

NOTES:
{text[:12000]}
"""
        try:
            raw = _call_gemini(prompt)
            return _extract_json(raw)
        except Exception:
            pass

    return {
        "summary": nlp.extractive_summary(text, num_sentences=5),
        "keywords": nlp.extract_keywords(text, top_n=8),
    }


def generate_quiz(text: str, subject: str = "General", num_questions: int = 5,
                   difficulty: str = "Medium") -> list:
    """Returns a list of question dicts:
    {"question": str, "options": [str,str,str,str], "correct_index": int, "explanation": str}
    """
    if USE_GEMINI and text.strip():
        prompt = f"""Create a {difficulty.lower()}-difficulty multiple-choice quiz with
{num_questions} questions based on the study notes below (subject: {subject}).
Each question must have exactly 4 options with exactly one correct answer,
plus a short explanation of the correct answer.

Respond ONLY with valid JSON: a list of objects shaped like:
{{"question": "...", "options": ["...", "...", "...", "..."], "correct_index": 0, "explanation": "..."}}

NOTES:
{text[:12000]}
"""
        try:
            raw = _call_gemini(prompt)
            data = _extract_json(raw)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass

    keywords = nlp.extract_keywords(text, top_n=max(num_questions * 2, 6)) if text.strip() else []
    sentences = nlp.split_sentences(text) if text.strip() else []
    questions = []
    if keywords and sentences:
        for i in range(min(num_questions, len(keywords))):
            kw = keywords[i]
            candidates = [s for s in sentences if kw in s.lower()]
            base_sentence = candidates[0] if candidates else (sentences[i % len(sentences)])
            wrong_pool = [w for w in keywords if w != kw]
            options = [kw] + random.sample(wrong_pool, k=min(3, len(wrong_pool)))
            while len(options) < 4:
                options.append(f"{kw}-related term")
            random.shuffle(options)
            questions.append({
                "question": f"Which term best relates to: \u201c{base_sentence[:140]}\u201d?",
                "options": options,
                "correct_index": options.index(kw),
                "explanation": f"'{kw}' is a key term extracted from your notes for this passage.",
            })
    if not questions:
        questions = DEFAULT_QUESTION_BANK.get(subject, DEFAULT_QUESTION_BANK["General"])[:num_questions]
    return questions


DEFAULT_QUESTION_BANK = {
    "Biology": [
        {"question": "Which organelle produces ATP through cellular respiration?",
         "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi apparatus"],
         "correct_index": 1,
         "explanation": "Mitochondria convert glucose and oxygen into ATP, the cell's energy currency."},
        {"question": "Which molecule carries genetic information from the nucleus to the ribosome?",
         "options": ["tRNA", "rRNA", "DNA", "mRNA"],
         "correct_index": 3,
         "explanation": "mRNA carries the transcribed genetic code to the ribosome for translation."},
        {"question": "What makes the cell membrane selectively permeable?",
         "options": ["Its phospholipid bilayer", "Its cellulose wall", "Its ribosomes", "Its nucleolus"],
         "correct_index": 0,
         "explanation": "The hydrophobic core of the bilayer blocks large or charged molecules."},
        {"question": "Which process moves water across a semi-permeable membrane?",
         "options": ["Active transport", "Osmosis", "Translation", "Mitosis"],
         "correct_index": 1,
         "explanation": "Osmosis is the passive movement of water toward higher solute concentration."},
    ],
    "Chemistry": [
        {"question": "What is the atomic number of Carbon?",
         "options": ["6", "12", "8", "14"],
         "correct_index": 0,
         "explanation": "Carbon has 6 protons, giving it atomic number 6."},
        {"question": "What is the pH of a neutral solution at 25\u00b0C?",
         "options": ["0", "7", "14", "5"],
         "correct_index": 1,
         "explanation": "A neutral solution has equal H+ and OH- concentration, giving pH 7."},
        {"question": "What type of bond forms when electrons are shared between two atoms?",
         "options": ["Ionic", "Covalent", "Metallic", "Hydrogen"],
         "correct_index": 1,
         "explanation": "Covalent bonds involve shared electron pairs; ionic bonds involve transfer."},
        {"question": "Which law states that mass is neither created nor destroyed in a reaction?",
         "options": ["Boyle's law", "Conservation of mass", "Avogadro's law", "Hess's law"],
         "correct_index": 1,
         "explanation": "Total mass of reactants always equals total mass of products."},
    ],
    "Physics": [
        {"question": "What does Newton's second law state?",
         "options": ["F = ma", "E = mc\u00b2", "V = IR", "P = mv"],
         "correct_index": 0,
         "explanation": "Force equals mass times acceleration."},
        {"question": "What is the SI unit of electrical resistance?",
         "options": ["Volt", "Ampere", "Ohm", "Watt"],
         "correct_index": 2,
         "explanation": "Resistance is measured in ohms (\u03a9), from V = IR."},
        {"question": "Which quantity is a vector?",
         "options": ["Speed", "Mass", "Velocity", "Temperature"],
         "correct_index": 2,
         "explanation": "Velocity has both magnitude and direction; speed has magnitude only."},
        {"question": "What happens to the kinetic energy of an object when its speed doubles?",
         "options": ["It doubles", "It halves", "It quadruples", "It stays the same"],
         "correct_index": 2,
         "explanation": "KE = \u00bdmv\u00b2, so doubling v multiplies kinetic energy by four."},
    ],
    "Mathematics": [
        {"question": "What is the derivative of x\u00b3?",
         "options": ["3x\u00b2", "x\u00b2", "3x", "x\u2074/4"],
         "correct_index": 0,
         "explanation": "By the power rule, d/dx(x\u207f) = nx\u207f\u207b\u00b9."},
        {"question": "What is the value of sin(90\u00b0)?",
         "options": ["0", "1", "-1", "\u221a2/2"],
         "correct_index": 1,
         "explanation": "The sine function peaks at 1 when the angle is 90 degrees."},
        {"question": "If f(x) = 2x + 5, what is f(4)?",
         "options": ["9", "11", "13", "14"],
         "correct_index": 2,
         "explanation": "2(4) + 5 = 8 + 5 = 13."},
        {"question": "What does the discriminant b\u00b2 - 4ac tell you about a quadratic?",
         "options": ["Its gradient", "The number of real roots", "Its y-intercept", "Its period"],
         "correct_index": 1,
         "explanation": "Positive gives two real roots, zero gives one, negative gives none."},
    ],
    "History": [
        {"question": "In which year did the Second World War end?",
         "options": ["1943", "1944", "1945", "1946"],
         "correct_index": 2,
         "explanation": "The war ended in 1945, following surrenders in May and August."},
        {"question": "Malaysia gained independence from British rule in which year?",
         "options": ["1948", "1957", "1963", "1965"],
         "correct_index": 1,
         "explanation": "Malaya declared independence on 31 August 1957; Malaysia formed in 1963."},
        {"question": "What is a primary source?",
         "options": ["A textbook summary", "A first-hand account from the period",
                     "A modern documentary", "An encyclopaedia entry"],
         "correct_index": 1,
         "explanation": "Primary sources are created by direct witnesses to the events."},
        {"question": "The Industrial Revolution began in which country?",
         "options": ["France", "Germany", "Britain", "The United States"],
         "correct_index": 2,
         "explanation": "It began in Britain in the late 18th century, driven by textiles and steam."},
    ],
    "General": [
        {"question": "Upload notes above to generate a personalised quiz. Sample question - which of these is a study technique?",
         "options": ["Spaced repetition", "Cramming everything the night before",
                     "Never reviewing notes", "Skipping practice questions"],
         "correct_index": 0,
         "explanation": "Spaced repetition improves long-term retention far more than cramming."},
    ],
}


def generate_flashcards(text: str, num_cards: int = 8) -> list:
    """Returns [{"front": str, "back": str}]"""
    if USE_GEMINI and text.strip():
        prompt = f"""Create {num_cards} concise flashcards (front = question/term,
back = answer/definition) from the study notes below. Keep each side short
enough to fit on a physical flashcard.

Respond ONLY with valid JSON: a list of objects shaped like:
{{"front": "...", "back": "..."}}

NOTES:
{text[:12000]}
"""
        try:
            raw = _call_gemini(prompt)
            data = _extract_json(raw)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass

    keywords = nlp.extract_keywords(text, top_n=num_cards) if text.strip() else []
    sentences = nlp.split_sentences(text) if text.strip() else []
    cards = []
    for kw in keywords:
        match = next((s for s in sentences if kw in s.lower()), None)
        cards.append({
            "front": f"What is / does '{kw}' relate to?",
            "back": match if match else f"Key term found in your notes: {kw}",
        })
    if not cards:
        cards = [{"front": "Upload notes to generate flashcards",
                   "back": "Once you upload notes, StudyMate AI will extract key terms automatically."}]
    return cards


def chat_response(history: list, user_message: str, context: str = "") -> str:
    """history: list of {"role": "user"|"assistant", "content": str}"""
    if USE_GEMINI:
        convo = "\n".join(
            f"{'Student' if m['role'] == 'user' else 'StudyMate AI'}: {m['content']}"
            for m in history[-10:]
        )
        prompt = f"""You are StudyMate AI, a friendly, encouraging study assistant chatbot
embedded in a student's learning app.

How to reply:
- Talk like a helpful tutor in conversation. Two or three sentences is usually
  plenty; only go longer when the student asks for depth.
- If a next study step is genuinely useful, work it into a normal sentence.
  Never append a labelled section like "Suggested next study action:" - and
  never add one to a reply that doesn't need it.
- Light Markdown only: **bold** for key terms, "- " bullets for real lists.
  Don't format a two-sentence answer.
- Don't repeat what you already said earlier in the conversation.
{f"Relevant context from the student's notes: {context[:4000]}" if context else ""}

Conversation so far:
{convo}
Student: {user_message}

StudyMate AI:"""
        try:
            return _call_gemini(prompt).strip()
        except Exception:
            pass

    _, why = status()
    kw = nlp.extract_keywords(user_message, top_n=3)
    if kw:
        return (f"I'd normally use Gemini to answer that in depth, but I'm running in "
                f"offline mode right now. ({why}) Based on your message, you might want "
                f"to review: {', '.join(kw)}.")
    return (f"I'm running in offline mode right now, so my answers are limited. ({why})")


def generate_recommendation(subject_scores: dict, quiz_history: list) -> str:
    if USE_GEMINI:
        prompt = f"""You are a study coach AI. Based on this student's subject
performance scores (0-100) and recent quiz history, write ONE short (max 40 words),
specific, encouraging study recommendation.

Subject scores: {json.dumps(subject_scores)}
Recent quiz results: {json.dumps(quiz_history[-5:])}
"""
        try:
            return _call_gemini(prompt).strip()
        except Exception:
            pass

    if subject_scores:
        weakest = min(subject_scores, key=subject_scores.get)
        return (f"Your {weakest} score is your lowest at {subject_scores[weakest]}%. "
                f"Try a focused 15-minute flashcard review on {weakest} today.")
    return "Upload some notes and take a quiz so StudyMate AI can tailor a recommendation for you."
