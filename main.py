import torch
import time
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, pyqtSignal
import markdown
from chat import chat_with_ai
from learning import save_to_file, load_from_file, reset_learning_data
from database import init_db

print("CUDA Available:", torch.cuda.is_available())
print("GPU Count:", torch.cuda.device_count())
print("GPU Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")
print("アプリ起動開始...")

init_db()
print("DB 初期化完了")


class ChatThread(QThread):
    response_ready = pyqtSignal(str, float)  # 応答時間も返す

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input

    def run(self):
        start_time = time.time()  # 開始時刻を記録
        response = chat_with_ai(self.user_input)
        end_time = time.time()  # 終了時刻を記録

        response_html = markdown.markdown(response)
        elapsed_time = round(end_time - start_time, 2)  # 応答時間を計測（小数点2桁）
        self.response_ready.emit(response_html, elapsed_time)


class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("LLM-DeskAI")
        self.setGeometry(100, 100, 700, 550)
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
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #6a6a6a;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #787878;
            }
        """)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("font-size: 14px; line-height: 1.5;")
        layout.addWidget(self.text_edit)

        self.loading_label = QLabel("")
        self.loading_label.setStyleSheet("color: #FFA500; font-size: 14px;")
        layout.addWidget(self.loading_label)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("メッセージを入力...")
        self.input_field.setStyleSheet("font-size: 14px; padding: 5px;")
        self.input_field.returnPressed.connect(self.get_response)
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
        
        # 入力をクリアし、ローディングメッセージを表示
        self.input_field.clear()
        self.loading_label.setText("⏳ ローディング中...")

        # UI に即座にユーザーの入力を表示
        self.text_edit.append(f"<p><b>🙍 ユーザー:</b><br>{user_input}</p>")

        # 非同期スレッドで AI の応答を取得
        self.chat_thread = ChatThread(user_input)
        self.chat_thread.response_ready.connect(self.display_response)
        self.chat_thread.start()

    def display_response(self, response_html, elapsed_time):
        # AI の応答を表示し、ローディングメッセージを消去
        formatted_response = f"<p><b>🤖 AI:</b><br>{response_html} <br><i>（応答時間: {elapsed_time} 秒）</i></p>"
        self.text_edit.append(formatted_response)
        self.loading_label.setText("")


if __name__ == '__main__':
    print("アプリケーションを起動")
    app = QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    print("GUI を表示")
    sys.exit(app.exec())
