# database.py
import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 会話履歴テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # カスタム応答テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT UNIQUE,
            answer TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_chat(user_input, ai_response):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_input, ai_response) VALUES (?, ?)", (user_input, ai_response))
    conn.commit()
    conn.close()

def get_custom_response(question):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM custom_responses WHERE question = ?", (question,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def export_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM custom_responses")
    custom_responses = cursor.fetchall()
    cursor.execute("SELECT * FROM chat_history")
    chat_history = cursor.fetchall()
    conn.close()
    return {"custom_responses": custom_responses, "chat_history": chat_history}

def import_data(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_responses")
    cursor.execute("DELETE FROM chat_history")
    for row in data.get("custom_responses", []):
        # row: (id, question, answer)
        cursor.execute("INSERT INTO custom_responses (question, answer) VALUES (?, ?)", (row[1], row[2]))
    for row in data.get("chat_history", []):
        # row: (id, user_input, ai_response, timestamp)
        cursor.execute("INSERT INTO chat_history (user_input, ai_response, timestamp) VALUES (?, ?, ?)", (row[1], row[2], row[3]))
    conn.commit()
    conn.close()
