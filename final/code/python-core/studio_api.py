# studio_api.py
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import random, numpy as np
from music_generator import query_musicgen
from audio_processor import AudioProcessor
import os
import sqlite3

app = Flask(__name__)
CORS(app)

# --- Database setup ---
DB_PATH = "music_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
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

# create the table when app starts
init_db()


# Always output to this path
OUTPUT_FILE = "./outputs/music.mp3"
os.makedirs("./outputs", exist_ok=True)

@app.route("/studio-generate", methods=["POST"])
def studio_generate():
    data = request.json
    prompt = data.get("prompt", "Calm music")
    duration = int(data.get("duration", 12))
    mood = data.get("mood", "Happy")
    tempo = int(data.get("tempo", 120))
    instruments = data.get("instruments", "piano")
    use_colab = data.get("use_colab", True)
    colab_url = data.get("colab_url", "")

    try:
        # ----- Add randomness for uniqueness -----
        seed = (hash(prompt) + random.randint(0, 100000)) % (2**32)
        np.random.seed(seed)

        # ----- Generate audio bytes -----
        audio_bytes = query_musicgen(
            prompt=prompt,
            duration=duration,
            use_colab=use_colab,
            colab_url=colab_url.strip()
        )

        if not audio_bytes:
            return jsonify({"error": "Music generator returned empty audio"}), 500

        # ----- Process audio into MP3 -----
        processor = AudioProcessor()
        params = {
            "mood": mood,
            "tempo": tempo,
            "instruments": instruments,
            "duration": duration
        }
        result = processor.process_audio_bytes(
            audio_bytes,
            params=params,
            output_format="mp3"
        )

        audio_file = result.get("audio_file")
        if not audio_file or not os.path.exists(audio_file):
            return jsonify({"error": "Failed to save MP3 file"}), 500

        # ----- Debug logs -----
        print("Generated MP3:", audio_file, "Size (MB):", result.get("file_size_mb"))


        # --- Save details to SQLite ---
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO music_history (prompt, mood, tempo, instruments, duration, file_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (prompt, mood, tempo, instruments, duration, audio_file))
        conn.commit()
        conn.close()

          


        # ----- Return MP3 directly -----
        return send_file(audio_file, mimetype="audio/mpeg", as_attachment=False)

    except Exception as e:
        print("Error generating music:", e)
        return jsonify({"error": str(e)}), 500



@app.route("/save-history", methods=["POST"])
def save_history():
    data = request.json
    username = data.get("username")
    prompt = data.get("prompt")
    mood = data.get("mood")
    instruments = data.get("instruments")
    tempo = data.get("tempo")
    duration = data.get("duration")
    audioUrl = data.get("audioUrl")
    timestamp = data.get("timestamp")

    # Connect to database
    conn = sqlite3.connect("music_history.db")
    c = conn.cursor()

    # Create table if not exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            prompt TEXT,
            mood TEXT,
            instruments TEXT,
            tempo INTEGER,
            duration INTEGER,
            audioUrl TEXT,
            timestamp TEXT
        )
    """)

    # Insert record
    c.execute("""
        INSERT INTO history (username, prompt, mood, instruments, tempo, duration, audioUrl, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, prompt, mood, instruments, tempo, duration, audioUrl, timestamp))

    conn.commit()
    conn.close()

    return jsonify({"message": "Saved to history successfully!"})



@app.route("/get-history/<username>", methods=["GET"])
def get_user_history(username):
    conn = sqlite3.connect("music_history.db")
    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE username=?", (username,))
    rows = c.fetchall()
    conn.close()

    # Convert rows to a list of dicts
    history = [
        {
            "prompt": row[2],
            "mood": row[3],
            "instruments": row[4],
            "tempo": row[5],
            "duration": row[6],
            "audioUrl": row[7],
            "timestamp": row[8],
        }
        for row in rows
    ]

    return jsonify(history)




@app.route("/history", methods=["GET"])
def get_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM music_history ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    history = [
        {
            "id": r[0],
            "prompt": r[1],
            "mood": r[2],
            "tempo": r[3],
            "instruments": r[4],
            "duration": r[5],
            "file_path": r[6],
            "created_at": r[7]
        }
        for r in rows
    ]
    return jsonify(history)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

