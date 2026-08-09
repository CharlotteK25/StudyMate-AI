# SETUP.md — Getting StudyMate AI fully working

The app **runs immediately with zero setup** in local demo mode:
accounts are stored in a local JSON file (`data/local_db.json`) and AI
features use an offline NLP fallback (keyword extraction + extractive
summarisation) instead of Gemini. This is enough to demo every screen
and button for your FYP presentation without any API keys.

To connect the *real* tools listed in your project brief (Firebase Auth,
Firestore, Gemini API), follow the steps below. Everything is optional
and independent — you can set up Gemini without Firebase, or vice versa.

## 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run the app

```bash
streamlit run app.py
```

Streamlit opens the app in your browser — this **is** "the website".
On a phone, open the same URL (or the `--server.address` you deploy to)
in a mobile browser; Streamlit's layout is responsive. If you specifically
need an installable app icon, add the site to your phone's home screen
("Add to Home Screen" in the browser share menu) — this gives it a
standalone app-like window without extra code.

## 3. Set up Google Gemini API

1. Go to https://aistudio.google.com/apikey and create a free API key.
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
3. Paste your key into `GEMINI_API_KEY`.
4. Restart the app. The blue "offline mode" info banners on the Notes,
   Quiz, Flashcards, and AI Chat pages will disappear once Gemini is
   active.

## 4. Set up Firebase (Authentication + Firestore)

1. Go to https://console.firebase.google.com and create a new project.
2. **Enable Authentication:**
   - In the left sidebar: Build → Authentication → Get Started.
   - Enable the "Email/Password" sign-in provider.
3. **Enable Firestore:**
   - Build → Firestore Database → Create database → Start in test mode
     (tighten security rules before submitting/deploying for real users).
4. **Get your Web API Key:**
   - Project Settings (gear icon) → General tab → scroll to "Your apps" →
     Web API Key. Paste it into `FIREBASE_WEB_API_KEY` in secrets.toml.
5. **Get a service account key (for Firestore access from Python):**
   - Project Settings → Service Accounts tab → "Generate new private key".
   - This downloads a JSON file. Open it and copy each field into the
     `[firebase_service_account]` section of `secrets.toml` (the field
     names already match).
6. Restart the app. Sign up a test account — you should see the user
   appear under Authentication → Users, and their notes/flashcards/quiz
   results appear under Firestore Database → Data.

## 5. Set up "Sign in with Google"

This uses Streamlit's own built-in Google login (`st.login()`), which is
separate from Firebase Authentication above and needs its own OAuth
credentials from **Google Cloud Console** (not the Firebase console).

1. **Create OAuth credentials:**
   - Go to https://console.cloud.google.com and select/create a project.
   - Left sidebar → APIs & Services → Credentials.
   - Click **+ Create Credentials → OAuth client ID**.
   - If prompted, configure the "OAuth consent screen" first (External is
     fine for testing — add your own email as a test user).
   - Application type: **Web application**.
   - Under "Authorized redirect URIs", add:
     `http://localhost:8501/oauth2callback`
     (add your real deployed URL + `/oauth2callback` too once you deploy).
   - Click Create. Copy the **Client ID** and **Client secret** shown.

2. **Generate a cookie secret** (any long random string works, e.g. run
   `python -c "import secrets; print(secrets.token_hex(32))"`).

3. **Add to `secrets.toml`:**
   ```toml
   [auth]
   redirect_uri = "http://localhost:8501/oauth2callback"
   cookie_secret = "paste-your-random-string-here"
   client_id = "paste-your-client-id-here"
   client_secret = "paste-your-client-secret-here"
   server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
   ```

4. Make sure `Authlib` is installed (`pip install -r requirements.txt`
   already covers this).

5. Restart the app and click the **Google** button on the login page. You
   should be redirected to Google's sign-in screen, then back into the
   app, already logged in.

   Note: signing in with Google creates its own user profile (separate
   from an email/password account with the same email) — that's expected
   for this demo build, since the two auth systems don't share a user
   table automatically.

## 6. Deploying

- **Streamlit Community Cloud** (free, easiest for a FYP submission):
  push this folder to a GitHub repo, then deploy at
  https://share.streamlit.io — paste the same secrets into the app's
  "Secrets" settings in the dashboard (same TOML format as
  `secrets.toml`).
- Any host that can run `streamlit run app.py` (Render, Railway, a VM)
  will also work.

## What maps to what (for your report / viva)

| Tool from your brief         | Where it lives in this project                          |
|-------------------------------|----------------------------------------------------------|
| Figma                         | `README.md` documents the original design; UI rebuilt in `pages_app/*.py` + `utils/theme.py` |
| Python                         | Entire backend logic: `services/*.py`, `pages_app/*.py` |
| Streamlit                      | `app.py` + all of `pages_app/` — the interactive UI      |
| Firebase Authentication        | `services/firebase_service.py` (`sign_up`, `sign_in`, `send_password_reset`) |
| Firebase Firestore             | `services/firebase_service.py` (notes, flashcards, quiz results, chat history, study plans) |
| NLP                            | `services/nlp_utils.py` (keyword extraction, extractive summarisation) |
| Google Gemini API              | `services/gemini_service.py` (summaries, quizzes, flashcards, chatbot, recommendations) |
