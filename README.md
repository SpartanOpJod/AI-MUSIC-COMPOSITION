# AI Music Composition

A full-stack music generation project that converts natural-language prompts and mood inputs into AI-generated audio.

## Overview

AI Music Composition combines:

- A React + Vite frontend (`final/code`) for authentication, studio controls, history, and playback.
- A Python backend (`final/code/python-core`) with Flask APIs and MusicGen/Gradio integration.
- Optional Streamlit interface for direct local experimentation (`python-core/app.py`).

## Key Features

- Mood-aware prompt-driven music generation
- Adjustable generation controls (duration, tempo, instruments)
- User sign-up/sign-in flow
- Audio playback and download in the studio
- Local history tracking in the frontend
- Health endpoint for API monitoring

## Repository Structure

```text
AI-MUSIC-COMPOSITION/
  README.md
  LICENSE
  final/
    code/
      src/                  # React frontend
      python-core/          # Flask API + Music generation logic
      package.json
```

## Tech Stack

- Frontend: React, Vite, Tailwind CSS
- Backend: Python, Flask, Flask-CORS, SQLite
- AI/Audio: Gradio Client, Hugging Face Space integration, NumPy, PyDub

## Local Setup

### 1. Frontend

```bash
cd final/code
npm install
npm run dev
```

Default frontend URL: `http://localhost:5173`

Create `.env` in `final/code`:

```bash
VITE_API_URL=http://localhost:8000
```

### 2. Backend (Flask API)

```bash
cd final/code/python-core
pip install -r requirements.txt
python studio_api.py
```

Default backend URL: `http://localhost:8000`

Health check:

```bash
curl http://localhost:8000/health
```

### 3. Optional: Streamlit Interface

```bash
cd final/code/python-core
pip install -r requirements.txt
streamlit run app.py
```

Default Streamlit URL: `http://localhost:8501`

## API Endpoints (Flask)

- `POST /signup`
- `POST /signin`
- `POST /studio-generate`
- `GET /health`

## Notes

- Music generation is powered through the configured Gradio endpoint in `python-core/music_generator.py`.
- SQLite databases are initialized automatically by the backend.
- The frontend expects `VITE_API_URL` to be set before starting.

## Author

- Aryan Srivastava
- LinkedIn: https://www.linkedin.com/in/aryan-srivastava-29a9a031a/
- GitHub: https://github.com/SpartanOpJod
