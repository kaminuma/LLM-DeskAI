# main.py

import torch
print("CUDA Available:", torch.cuda.is_available())
print("GPU Count:", torch.cuda.device_count())
print("GPU Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")


# main.py の冒頭に追加
print("✅ アプリ起動開始...")

import sys
print("✅ sys インポート完了")

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
print("✅ PyQt6 のインポート完了")

from PyQt6.QtGui import QIcon
print("✅ PyQt6.QGui のインポート完了")

from chat import chat_with_ai
print("✅ chat.py のインポート完了")

from learning import save_to_file, load_from_file, reset_learning_data
print("✅ learning.py のインポート完了")

from database import init_db
print("✅ database.py のインポート完了")

# DBの初期化
init_db()
print("✅ DB 初期化完了")


print("✅ PyQt6 のインポート完了")

# DBの初期化
init_db()

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("LLM-DeskAI")
        self.setGeometry(100, 100, 600, 500)

        # モダンなダークテーマのスタイルシート
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit, QTextEdit {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #6a6a6a;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #787878;
            }
        """)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        button_layout = QHBoxLayout()

        self.send_button = QPushButton("送信")
        self.send_button.clicked.connect(self.get_response)
        button_layout.addWidget(self.send_button)

        self.save_button = QPushButton("セーブ")
        self.save_button.clicked.connect(save_to_file)
        button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("ロード")
        self.load_button.clicked.connect(load_from_file)
        button_layout.addWidget(self.load_button)

        self.reset_button = QPushButton("リセット")
        self.reset_button.clicked.connect(reset_learning_data)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_response(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return
        response = chat_with_ai(user_input)
        self.text_edit.append(f"<b>ユーザー:</b> {user_input}")
        self.text_edit.append(f"<b>AI:</b> {response}\n")
        self.input_field.clear()

if __name__ == '__main__':
    print("✅ アプリケーションを起動")
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    print("✅ GUI を表示")
    sys.exit(app.exec())
