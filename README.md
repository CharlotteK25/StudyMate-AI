# StudyMate AI

StudyMate AI is an AI-powered web application developed to assist university students in organising study materials through intelligent note summarisation, flashcard generation, quiz generation, personalised study recommendations, and an AI chatbot.

## Technologies
- Python
- Streamlit
- Firebase Authentication
- Cloud Firestore
- Google Gemini API
- PyPDF2
- python-docx
- Pandas
- Altair

## Installation

pip install -r requirements.txt

streamlit run app.py

## Features (every button is wired up)

- **Auth** — Sign up, sign in, forgot-password, log out (Firebase Auth,
  with a local fallback so it works with zero setup)
- **Dashboard** — stats, subject progress, quiz performance chart, quick
  actions, AI recommendation, streak, today's goal, upcoming tasks
- **Notes** — drag-and-drop upload (PDF/DOCX/TXT/PPTX), AI-generated
  summaries + keywords, delete/view files
- **Flashcards** — AI-generated decks from your notes, manual card
  creation, flip/next/previous study mode, delete deck
- **Quiz** — AI-generated multiple-choice quizzes from your notes (or a
  sample bank), scoring, per-question review with explanations, retake
- **AI Chat** — multi-session chatbot grounded in your uploaded notes
- **Analytics** — study hours, weekly/monthly trends, topic mastery,
  subject breakdown, AI insight
- **Recommendations** — personalised AI study tips linked to real actions
  (jump straight to Quiz / Flashcards / Notes / Chat)
- **Profile** — edit name, manage subjects, log out, delete account

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app works immediately with **no API keys** (local accounts + offline
NLP). See `SETUP.md` to connect real Firebase and Google Gemini for the
full experience described in the project brief.

## Tech stack

| Layer                  | Tool                                                    |
|-------------------------|---------------------------------------------------------|
| UI / frontend design    | Originally prototyped in Figma (React/TSX export in this zip's `src/` folder — kept for reference) |
| App framework            | Streamlit                                              |
| Backend logic             | Python                                                 |
| Authentication             | Firebase Authentication (Identity Toolkit REST API)   |
| Database                    | Firebase Firestore (with local JSON fallback)        |
| NLP                          | Custom keyword extraction + extractive summarisation |
| Generative AI                 | Google Gemini API                                   |

## Project structure

```
app.py                     # Entry point + page routing
pages_app/
  auth.py                  # Sign in / sign up / forgot password
  dashboard.py              # Home dashboard
  notes.py                   # Upload notes + AI summaries
  flashcards.py               # AI flashcards + manual cards
  quiz.py                      # AI quiz generation + scoring
  chat.py                       # AI chatbot
  analytics.py                   # Progress analytics
  recommendations.py              # AI study recommendations
  profile.py                       # Account settings
services/
  firebase_service.py       # Auth + Firestore (with local fallback)
  gemini_service.py          # All Gemini-powered AI features
  nlp_utils.py                 # Offline NLP fallback
  local_store.py                # Local JSON "database"
utils/
  theme.py                    # Shared CSS / styling
  navbar.py                     # Top navigation bar
  state.py                       # Session-state helpers
data/local_db.json              # Local demo-mode data (auto-created)
```

## Note on "website vs app"

Streamlit produces a responsive web app: the same `streamlit run app.py`
command **is** your website, and it renders cleanly in a mobile browser
too (add it to your phone's home screen for an app-like icon/experience).
Streamlit doesn't compile to a native iOS/Android binary — if your FYP
specifically requires a store-installable app, that would need a separate
mobile framework, which is out of scope for what was requested here.
