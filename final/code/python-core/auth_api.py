from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # ✅ allows React frontend to talk to backend

DB_FILE = "users.db"

# --- Initialize DB ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
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

init_db()

# --- Signup API ---
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    print("Received signup data:", data)
    fullName = data.get("fullName")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([fullName, username, email, password]):
        return jsonify({"error": "All fields are mandatory"}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (fullName, username, email, password) VALUES (?, ?, ?, ?)",
                  (fullName, username, email, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "Signup successful"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 400


# --- Signin API ---
@app.route("/signin", methods=["POST"])
def signin():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "All fields are mandatory"}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, fullName, username, email FROM users WHERE username = ? AND password = ?",
              (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Signin successful", "user": {
            "id": user[0],
            "fullName": user[1],
            "username": user[2],
            "email": user[3]
        }}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 400


# --- View all users API (optional) ---
@app.route("/users", methods=["GET"])
def get_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, fullName, username, email FROM users")
    users = [{"id": row[0], "fullName": row[1], "username": row[2], "email": row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(users)


if __name__ == "__main__":
    app.run(debug=True)
