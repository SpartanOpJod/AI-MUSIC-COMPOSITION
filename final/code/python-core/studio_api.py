from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import sqlite3
from io import BytesIO

from music_generator import query_musicgen
from mood_analyzer import MoodAnalyzer

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

DATA_DIR = "/tmp"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_DB_PATH = os.path.join(DATA_DIR, "users.db")
MUSIC_DB_PATH = os.path.join(DATA_DIR, "music_history.db")


def init_users_db():
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullName TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def init_music_db():
    conn = sqlite3.connect(MUSIC_DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS music_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            prompt TEXT,
            mood TEXT,
            instruments TEXT,
            tempo INTEGER,
            duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


init_users_db()
init_music_db()

mood_analyzer = MoodAnalyzer()


@app.route("/studio-generate", methods=["POST"])
def studio_generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    prompt = data.get("prompt", "Calm music")
    duration = int(data.get("duration", 12))
    tempo = int(data.get("tempo", 120))
    instruments = data.get("instruments", "piano")
    username = data.get("username", "guest")

    if duration < 5 or duration > 30:
        return jsonify({"error": "Duration must be between 5–30 seconds"}), 400

    analysis = mood_analyzer.analyze(prompt)
    mood = analysis["mood"]
    energy = analysis["energy"]

    audio_bytes = query_musicgen(
        prompt=prompt,
        duration=duration,
        mood=mood,
        energy=energy,
        use_colab=False,
    )

    try:
        conn = sqlite3.connect(MUSIC_DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO music_history
            (username, prompt, mood, instruments, tempo, duration)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, prompt, mood, instruments, tempo, duration),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    audio_io = BytesIO(audio_bytes)
    audio_io.seek(0)

    return send_file(
        audio_io,
        mimetype="audio/wav",
        as_attachment=False,
        download_name="generated_music.wav",
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "AI Music Backend"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
