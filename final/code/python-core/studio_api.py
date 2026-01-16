from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from mood_analyzer import MoodAnalyzer
from music_generator import query_musicgen
from audio_processor import AudioProcessor
import random
import numpy as np
import os
import sqlite3
import time

app = Flask(__name__)

# ---------- INIT ----------
mood_analyzer = MoodAnalyzer()

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

DATA_DIR = "/data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_DB_PATH = os.path.join(DATA_DIR, "users.db")
MUSIC_DB_PATH = os.path.join(DATA_DIR, "music_history.db")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- DB INIT ----------
def init_music_db():
    conn = sqlite3.connect(MUSIC_DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS music_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            mood TEXT,
            tempo INTEGER,
            instruments TEXT,
            duration INTEGER,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def init_users_db():
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullName TEXT,
            username TEXT,
            email TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_music_db()
init_users_db()

# ---------- MUSIC GENERATION ----------
@app.route("/studio-generate", methods=["POST"])
def studio_generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        prompt = data.get("prompt", "Calm music")
        duration = int(data.get("duration", 12))
        use_colab = data.get("use_colab", True)
        colab_url = data.get("colab_url", "").strip()

        # 🔥 THIS WAS MISSING
        analysis = mood_analyzer.analyze(prompt)
        detected_mood = analysis["mood"]
        energy = analysis["energy"]

        seed = (int(time.time() * 1e6) + random.randint(0, 999999)) % (2**32)
        np.random.seed(seed)

        audio_bytes = query_musicgen(
            prompt=prompt,
            duration=duration,
            mood=detected_mood,
            energy=energy,
            use_colab=use_colab,
            colab_url=colab_url
        )

        processor = AudioProcessor()
        result = processor.process_audio_bytes(
            audio_bytes,
            params={"duration": duration},
            output_format="mp3"
        )

        audio_file = result["audio_file"]
        final_path = os.path.join(OUTPUT_DIR, os.path.basename(audio_file))
        os.replace(audio_file, final_path)

        conn = sqlite3.connect(MUSIC_DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO music_history (prompt, mood, tempo, instruments, duration, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (prompt, detected_mood, energy * 20, "synthetic", duration, final_path))
        conn.commit()
        conn.close()

        return send_file(final_path, mimetype="audio/mpeg")

    except Exception as e:
        print("Music generation error:", e)
        return jsonify({"error": str(e)}), 500

# ---------- HEALTH ----------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
