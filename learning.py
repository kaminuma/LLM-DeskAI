# learning.py
import json
import shutil
import os
from database import export_data, import_data
from config import SAVE_PATH, DB_PATH

def save_to_file():
    data = export_data()
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("学習データを保存しました")

def load_from_file():
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        import_data(data)
        print("学習データを復元しました")
    except FileNotFoundError:
        print("セーブデータが見つかりません")

def reset_learning_data():
    # 学習データ（会話履歴とカスタム応答）をリセット
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    cursor.execute("DELETE FROM custom_responses")
    conn.commit()
    conn.close()
    print("学習データをリセットしました")
