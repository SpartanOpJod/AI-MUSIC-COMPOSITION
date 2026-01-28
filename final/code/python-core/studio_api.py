from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import os
import sqlite3
import time
import base64
from io import BytesIO

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


try:
    init_users_db()
    init_music_db()
except Exception as e:
    print(e)


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    full_name = data.get("fullName", "").strip()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not all([full_name, username, email, password]):
        return jsonify({"error": "All fields are mandatory"}), 400

    if "@" not in email:
        return jsonify({"error": "Invalid email format"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (fullName, username, email, password) VALUES (?, ?, ?, ?)",
            (full_name, username, email, password),
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Signup successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, fullName, username, email FROM users WHERE username = ? AND password = ?",
        (username, password),
    )
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    return (
        jsonify(
            {
                "message": "Signin successful",
                "user": {
                    "id": user[0],
                    "fullName": user[1],
                    "username": user[2],
                    "email": user[3],
                },
            }
        ),
        200,
    )


def extract_audio_from_hf_response(result):
    if not isinstance(result, dict) or "data" not in result:
        return None, "Invalid response format"

    data_list = result.get("data")
    if not isinstance(data_list, list):
        return None, "Invalid data field"

    for item in data_list:
        if isinstance(item, dict) and isinstance(item.get("data"), str):
            return item["data"], None

    return None, "No audio found"


@app.route("/studio-generate", methods=["POST"])
def studio_generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    base_prompt = data.get("prompt", "Calm music")
    duration = int(data.get("duration", 12))
    mood = data.get("mood", "Happy")
    tempo = int(data.get("tempo", 120))
    instruments = data.get("instruments", "piano")
    username = data.get("username", "guest")

    if duration < 5 or duration > 30:
        return jsonify({"error": "Duration must be between 5-30 seconds"}), 400

    prompt = (
        f"{base_prompt}. Mood: {mood}. Tempo: {tempo} BPM. "
        f"Instrument: {instruments}."
    )

    hf_url = os.environ.get("HF_API_URL")
    if not hf_url:
        return jsonify({"error": "Music service not configured"}), 503

    trigger = requests.post(
        f"{hf_url}/gradio_api/call/generate_music",
        json={"data": [prompt, duration]},
        timeout=30,
    )

    if trigger.status_code != 200:
        return jsonify({"error": "Failed to start generation"}), 502

    event_id = trigger.json().get("event_id")
    if not event_id:
        return jsonify({"error": "No event id returned"}), 502

    stream = requests.get(
        f"{hf_url}/gradio_api/call/generate_music/{event_id}",
        stream=True,
        timeout=120,
    )

    audio_b64 = None
    for line in stream.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if '"data"' in decoded:
                audio_b64 = decoded.split('"')[-2]
                break

    if not audio_b64:
        return jsonify({"error": "No audio received"}), 502

    if "," in audio_b64:
        audio_b64 = audio_b64.split(",", 1)[1]

    audio_bytes = base64.b64decode(audio_b64)

    try:
        conn = sqlite3.connect(MUSIC_DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO music_history
            (username, prompt, mood, instruments, tempo, duration)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, base_prompt, mood, instruments, tempo, duration),
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


@app.route("/save-history", methods=["POST"])
def save_history():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    conn = sqlite3.connect(MUSIC_DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO music_history (username, prompt, mood, instruments, tempo, duration)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("username", "guest"),
            data.get("prompt"),
            data.get("mood"),
            data.get("instruments"),
            data.get("tempo"),
            data.get("duration"),
        ),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Saved to history"}), 201


@app.route("/get-history/<username>", methods=["GET"])
def get_history(username):
    conn = sqlite3.connect(MUSIC_DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT prompt, mood, instruments, tempo, duration, created_at
        FROM music_history
        WHERE username = ?
        ORDER BY created_at DESC
        """,
        (username,),
    )
    rows = c.fetchall()
    conn.close()

    return (
        jsonify(
            [
                {
                    "prompt": r[0],
                    "mood": r[1],
                    "instruments": r[2],
                    "tempo": r[3],
                    "duration": r[4],
                    "created_at": r[5],
                }
                for r in rows
            ]
        ),
        200,
    )


@app.route("/users", methods=["GET"])
def get_users():
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, fullName, username, email FROM users")
    rows = c.fetchall()
    conn.close()

    return (
        jsonify(
            [
                {
                    "id": r[0],
                    "fullName": r[1],
                    "username": r[2],
                    "email": r[3],
                }
                for r in rows
            ]
        ),
        200,
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "AI Music Backend"}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
