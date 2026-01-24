# studio_api.py - Lightweight Flask API for Render
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import os
import sqlite3
import time
import base64
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

def extract_audio_from_hf_response(result):
    """
    Safely extract base64 audio from HF Gradio response.
    
    HF Gradio Spaces can return multiple outputs in result["data"].
    Audio is NOT always at index 0 - this function scans ALL items.
    Audio is identified as: a dict containing a "data" field with base64 string.
    
    Returns: (audio_b64_string, error_message or None)
    """
    try:
        if not isinstance(result, dict):
            return None, f"Response is not a dict: {type(result)}"
        
        if "data" not in result:
            return None, f"Response missing 'data' key. Keys: {result.keys()}"
        
        data_list = result.get("data")
        if not isinstance(data_list, list) or len(data_list) == 0:
            return None, f"'data' is not a non-empty list: {type(data_list)}"
        
        # Scan through ALL items to find audio
        # HF Gradio returns multiple outputs: text, sliders, audio, labels, etc.
        # Audio format: {"name": "audio.wav", "data": "base64..."}
        for idx, data_item in enumerate(data_list):
            if isinstance(data_item, dict) and "data" in data_item:
                audio_b64 = data_item["data"]
                # Verify it's a non-empty string (base64)
                if isinstance(audio_b64, str) and len(audio_b64) > 10:
                    print(f"✅ Found audio at index {idx}: {len(audio_b64)} chars")
                    return audio_b64, None
        
        # No audio found in any output - provide diagnostic info
        data_types = [f"[{idx}] {type(item).__name__}" for idx, item in enumerate(data_list)]
        return None, f"No audio found in result['data']. Output items: {', '.join(data_types)}"
    
    except Exception as e:
        return None, f"Exception extracting audio: {e}"

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

        # Validate duration (Render free tier safety)
        if duration < 5 or duration > 30:
            return jsonify({"error": "Duration must be between 5-30 seconds"}), 400

        # merge UI controls into ONE prompt
        prompt = (
            f"{base_prompt}. "
            f"Mood: {mood}. "
            f"Tempo: {tempo} BPM. "
            f"Instrument: {instruments}."
        )

        hf_url = os.environ.get("HF_API_URL")
        if not hf_url:
            print("ERROR: HF_API_URL environment variable not set")
            return jsonify({"error": "Music service not configured"}), 503

        # Retry logic for Render free tier stability
        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"[Attempt {attempt + 1}] Calling HF API: {hf_url}")
                response = requests.post(
                    hf_url,
                    json={"data": [prompt, duration]},
                    timeout=60,  # Reduced from 120 for Render free tier
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"HF Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_msg = response.text[:200] if response.text else "No error details"
                    print(f"HF API Error: {error_msg}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
                    return jsonify({"error": f"Music generation failed (HTTP {response.status_code})"}), 502
                
                # Parse and validate response structure
                try:
                    result = response.json()
                    print(f"HF Response keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
                except Exception as e:
                    print(f"Failed to parse HF response as JSON: {e}")
                    return jsonify({"error": "Invalid response from music service"}), 502
                
                # Extract base64 audio from HF response using helper
                audio_b64, extraction_error = extract_audio_from_hf_response(result)
                
                if extraction_error:
                    print(f"Cannot extract audio: {extraction_error}")
                    print(f"Full response: {str(result)[:500]}")
                    return jsonify({"error": "Invalid audio data from music service"}), 502
                
                # Decode base64 to bytes
                try:
                    # Remove data URI prefix if present (e.g., "data:audio/wav;base64,")
                    if "," in audio_b64:
                        audio_b64 = audio_b64.split(",", 1)[1]
                    
                    audio_bytes = base64.b64decode(audio_b64)
                    print(f"✅ Decoded audio: {len(audio_bytes)} bytes")
                    
                    # Validate audio data (WAV files start with RIFF)
                    if not audio_bytes.startswith(b'RIFF'):
                        print(f"⚠️ Warning: Audio doesn't start with RIFF, may not be valid WAV")
                    
                except Exception as e:
                    print(f"Base64 decode failed: {e}")
                    return jsonify({"error": "Failed to decode audio data"}), 502
                
                # Success - save history (non-blocking)
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
                    print(f"✅ Saved history for user: {username}")
                except Exception as e:
                    print(f"⚠️ History save failed (non-blocking): {e}")
                
                # Return audio file
                audio_io = BytesIO(audio_bytes)
                audio_io.seek(0)
                response_obj = send_file(
                    audio_io,
                    mimetype="audio/wav",
                    as_attachment=False,
                    download_name="generated_music.wav"
                )
                response_obj.headers["Content-Length"] = len(audio_bytes)
                response_obj.headers["Cache-Control"] = "no-cache"
                return response_obj
                
            except requests.Timeout:
                print(f"[Attempt {attempt + 1}] Request timeout after 60s")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return jsonify({"error": "Music generation timed out (service overloaded)"}), 504
            except requests.RequestException as e:
                print(f"[Attempt {attempt + 1}] Request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return jsonify({"error": "Failed to connect to music service"}), 502

    except ValueError as e:
        print(f"Validation error: {e}")
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        print(f"❌ Studio generate error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred"}), 500
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
