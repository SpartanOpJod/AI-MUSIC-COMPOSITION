🎵 AI Music Composition

Generate music from emotions using Generative AI.
Describe how you feel — get a melody that matches your vibe.

AI Music Composition is a full-stack GenAI powered music studio that turns text-based moods and prompts into real, downloadable music.
It combines a modern React frontend with a Streamlit + MusicGen backend to create an interactive AI-driven music experience.

✨ What it does

You type how you feel (happy, sad, energetic, romantic, etc.) →
The AI understands the mood →
It generates music →
You can listen, visualize, and download it 🎶

This is basically Spotify meets AI meets emotions.

🧠 Core Features

🎭 Mood-based music generation (Happy, Sad, Calm, Energetic, Romantic, Mysterious)

✍️ Text prompt control (describe the vibe you want)

🎼 Instrument selection (synth, piano, drums, etc.)

⏱ Tempo & duration control

🎧 Instant audio playback

⬇️ Download generated music as MP3

📊 Waveform visualization

🔀 Seeded randomness → every generation is unique

🖥️ Frontend – MuseAI (React + Vite)

The frontend is a full music studio UI called MuseAI Frontend v3.

Pages

Home

Clean hero section

Featured music grid (20 items)

Studio (/studio)

Instrument-themed background

20 prompt ideas

Manual controls

Music features

History button

Instrument gallery

About

AI music workflow

20 listed features

History

Music library layout

Shows placeholders when empty (20 items)

Profile

User info

Account features list

Dev Setup
cd MuseAI-Frontend
npm install
npm run dev


Vite automatically proxies:

/api → http://localhost:8000

🧪 Backend – Streamlit AI Engine

The backend is a Streamlit-based AI music engine that uses MusicGen (via Colab or API) and custom audio processing.

It:

Takes mood, prompt, tempo, instruments

Calls MusicGen

Processes audio

Converts to MP3

Returns playable + downloadable music

Generates waveform visualizations

🎛 How the AI works

User provides:

Mood

Prompt

Tempo

Instruments

Duration

The system:

Creates a unique random seed

Sends the prompt to MusicGen (via Colab or API)

Receives raw audio

The AudioProcessor:

Applies mood & tempo adjustments

Converts output to MP3

Calculates file size

The app:

Displays audio player

Generates waveform

Enables download

🧩 Tech Stack
Frontend

React

Vite

Tailwind CSS

Backend

Python

Streamlit

NumPy

PyDub

Matplotlib

Seaborn

AI

Meta MusicGen (via Colab / API)

Generative AI for music synthesis

🧑‍💻 How to run locally
1. Backend
pip install -r requirements.txt
streamlit run app.py


Runs on:

http://localhost:8501

2. Frontend
cd MuseAI-Frontend
npm install
npm run dev


Runs on:

http://localhost:5173

📡 Colab Integration

The app can connect to a MusicGen Gradio Colab server.

Just paste the URL into:

Colab Gradio URL


Example:

https://xxxx.gradio.live


Enable:

Use Colab MusicGen ✔

🖼️ Waveform Visualization

Every generated song gets a live waveform preview so you can actually see your music 🔥
This is done using:

PyDub

NumPy

Matplotlib

Seaborn

🚀 Future Ideas

Voice-based mood detection

User accounts

Playlist export

Genre presets

AI mastering

Beat + melody separation

Mobile app

🧠 MusicGen / Colab support

📜 History & Library (Frontend)

🎹 Studio Mode with pro-level controls


📬 Contact

👤 Developed by: Aryan Srivastava 

🔗 LinkedIn Profile:https://www.linkedin.com/in/aryan-srivastava-29a9a031a/

🌐 GitHub: https://github.com/SpartanOpJod