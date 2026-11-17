from datetime import datetime, timezone
import sqlite3
from flask import Flask, jsonify, render_template, request, session
from bot import answer_question

app = Flask(__name__)
app.secret_key = "replace-this-development-secret-before-deployment"
DB_PATH = "chatbot.db"

def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Please type a message."}), 400
    if len(message) > 1000:
        return jsonify({"error": "Please keep your message under 1,000 characters."}), 400

    answer, topic = answer_question(message, session.get("topic"))
    session["topic"] = topic

    with get_db() as db:
        db.execute(
            "INSERT INTO chat_logs (session_id, user_message, bot_response, created_at) VALUES (?, ?, ?, ?)",
            (session.get("conversation_id", "browser-session"), message, answer,
             datetime.now(timezone.utc).isoformat()),
        )
    return jsonify({"answer": answer})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True, port=5000)
