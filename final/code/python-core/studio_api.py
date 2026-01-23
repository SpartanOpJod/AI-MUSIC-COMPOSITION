# studio_api.py - Lightweight Flask API for Render
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import os
import sqlite3
import time
from io import BytesIO

app = Flask(__name__)

# --- CORS Configuration ---
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# --- Database Setup ---
DATA_DIR = "/tmp"  # Use /tmp for Render free tier
os.makedirs(DATA_DIR, exist_ok=True)

USERS_DB_PATH = os.path.join(DATA_DIR, "users.db")
MUSIC_DB_PATH = os.path.join(DATA_DIR, "music_history.db")

def init_users_db():
    """Initialize users database"""
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullName TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def init_music_db():
    """Initialize music history database"""
    conn = sqlite3.connect(MUSIC_DB_PATH)
    c = conn.cursor()
    c.execute("""
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
    """)
    conn.commit()
    conn.close()

# Initialize databases
try:
    init_users_db()
    init_music_db()
    print("✅ Databases initialized")
except Exception as e:
    print(f"⚠️ Database init error: {e}")

# --- Authentication Routes ---

@app.route("/signup", methods=["POST"])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
        
        fullName = data.get("fullName", "").strip()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        # Validate all fields
        if not all([fullName, username, email, password]):
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
                (fullName, username, email, password)
            )
            conn.commit()
            conn.close()
            print(f"User registered: {username}")
            return jsonify({"message": "Signup successful"}), 201

        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return jsonify({"error": "Username already exists"}), 400
            elif "email" in str(e):
                return jsonify({"error": "Email already exists"}), 400
            return jsonify({"error": "Registration failed"}), 400

    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/signin", methods=["POST"])
def signin():
    """Authenticate a user"""
    try:
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
            (username, password)
        )
        user = c.fetchone()
        conn.close()

        if user:
            print(f"User signed in: {username}")
            return jsonify({
                "message": "Signin successful",
                "user": {
                    "id": user[0],
                    "fullName": user[1],
                    "username": user[2],
                    "email": user[3]
                }
            }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        print(f"Signin error: {e}")
        return jsonify({"error": str(e)}), 500

# --- Music Generation Route (Forwards to External Service) ---

@app.route("/studio-generate", methods=["POST"])
def studio_generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        base_prompt = data.get("prompt", "Calm music")
        duration = int(data.get("duration", 12))
        mood = data.get("mood", "Happy")
        tempo = int(data.get("tempo", 120))
        instruments = data.get("instruments", "piano")
        username = data.get("username", "guest")

        # merge UI controls into ONE prompt
        prompt = (
            f"{base_prompt}. "
            f"Mood: {mood}. "
            f"Tempo: {tempo} BPM. "
            f"Instrument: {instruments}."
        )

        hf_url = os.environ.get("HF_API_URL")
        if not hf_url:
            return jsonify({"error": "HF_API_URL not set"}), 500

        response = requests.post(
            hf_url,
            json={"data": [prompt, duration]},
            timeout=120
        )

        if response.status_code != 200:
            return jsonify({"error": "Hugging Face inference failed"}), 500

        result = response.json()
        audio_bytes = bytes(result["data"][0])

        # save history (non-blocking)
        try:
            conn = sqlite3.connect(MUSIC_DB_PATH)
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO music_history
                (username, prompt, mood, instruments, tempo, duration)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, base_prompt, mood, instruments, tempo, duration)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print("History save failed:", e)

        return send_file(
            BytesIO(audio_bytes),
            mimetype="audio/wav",
            as_attachment=False
        )

    except Exception as e:
        print("Studio generate error:", e)
        return jsonify({"error": str(e)}), 500
# --- Music History Routes ---

@app.route("/save-history", methods=["POST"])
def save_history():
    """Save music generation to user history"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
        
        username = data.get("username", "guest")
        prompt = data.get("prompt")
        mood = data.get("mood")
        instruments = data.get("instruments")
        tempo = data.get("tempo")
        duration = data.get("duration")

        conn = sqlite3.connect(MUSIC_DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO music_history (username, prompt, mood, instruments, tempo, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, prompt, mood, instruments, tempo, duration))
        conn.commit()
        conn.close()

        return jsonify({"message": "Saved to history"}), 201

    except Exception as e:
        print(f"Save history error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-history/<username>", methods=["GET"])
def get_history(username):
    """Get user's music history"""
    try:
        conn = sqlite3.connect(MUSIC_DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT prompt, mood, instruments, tempo, duration, created_at FROM music_history WHERE username = ? ORDER BY created_at DESC",
            (username,)
        )
        rows = c.fetchall()
        conn.close()

        history = [
            {
                "prompt": row[0],
                "mood": row[1],
                "instruments": row[2],
                "tempo": row[3],
                "duration": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]

        return jsonify(history), 200

    except Exception as e:
        print(f"Get history error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=["GET"])
def get_users():
    """Get all registered users (debug endpoint)"""
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, fullName, username, email FROM users")
        users = [
            {
                "id": row[0],
                "fullName": row[1],
                "username": row[2],
                "email": row[3]
            }
            for row in c.fetchall()
        ]
        conn.close()
        return jsonify(users), 200

    except Exception as e:
        print(f"Get users error: {e}")
        return jsonify({"error": str(e)}), 500

# --- Health Check ---

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "AI Music Backend"}), 200

# --- Error Handlers ---

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# --- Entry Point ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    # In production, use gunicorn instead:
    # gunicorn studio_api:app --workers=1 --threads=2 --bind 0.0.0.0:PORT
    app.run(host="0.0.0.0", port=port, debug=False)
