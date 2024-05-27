import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QTextEdit, QPushButton, QLineEdit, QMessageBox
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QKeySequence
from api_port import API_Loader

APP_NAME = "Logic Launchpad"
TITLE_FONT_SIZE = 20
SMALL_TITLE_FONT_SIZE = 16
DESCRIPTION_FONT_SIZE = 14
ANSWER_FONT_SIZE = 14
RESULT_FONT_SIZE = 14

class NoPasteTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            return
        else:
            super().keyPressEvent(event)
    
class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(f"{APP_NAME} Login")
        self.setFixedSize(QSize(400, 200))
        
        layout = QVBoxLayout(self)
        self.server_label = QLabel("Server URL:")
        self.server_input = QLineEdit()
        self.server_input.setText("127.0.0.1:8000")

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(150)
        self.login_button.clicked.connect(self.check_login)
        
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        
    def check_login(self):
        url = self.server_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        api_loder = API_Loader(url)
        status, message = api_loder.login(username, password)
        if status:
            QMessageBox.information(self, "Success", message)
            self.parent().show_main_window(api_loder)
        else:
            QMessageBox.warning(self, "Error", message)

class MainWindow(QMainWindow):
    def __init__(self, api_loader):
        super().__init__()
        self.api_loader = api_loader
        
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(QSize(1600, 900))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layouts
        main_layout = QHBoxLayout(central_widget)
        question_list_layout = QVBoxLayout()
        question_detail_layout = QVBoxLayout()
        answer_layout = QVBoxLayout()

        # Question List
        self.question_list_ui = QListWidget()
        self.question_list_ui.setFixedWidth(250)
        self.question_list_ui.currentItemChanged.connect(self.load_question_info)
        
        # Question Detail
        self.question_title = QLabel("Select a question")
        self.question_title.setStyleSheet(f"font-size: {TITLE_FONT_SIZE}px; font-weight: bold;")
        self.question_description_label = QLabel("Description:")
        self.question_description_label.setStyleSheet(f"font-size: {SMALL_TITLE_FONT_SIZE}px; font-weight: bold")
        self.question_description = QTextEdit("Select a question to view the description.")
        self.question_description.setStyleSheet(f"font-size: {DESCRIPTION_FONT_SIZE}px;")
        self.question_description.setReadOnly(True)
        self.question_description.setFixedHeight(350)
        self.answer_label = QLabel("Answer:")
        self.answer_label.setStyleSheet(f"font-size: {SMALL_TITLE_FONT_SIZE}px; font-weight: bold")
        self.answer_text = NoPasteTextEdit()
        self.answer_text.setStyleSheet(f"font-size: {ANSWER_FONT_SIZE}px;")
        self.answer_text.setFixedHeight(410)
        self.answer_text.setFixedWidth(800)
        self.submit_part = QHBoxLayout()
        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedWidth(100)
        self.submit_button.clicked.connect(self.submit_answer)
        self.quota_label = QLabel("Quota: 0")
        self.quota_label.setStyleSheet("font-size: 12px;")
        self.submit_part.addWidget(self.submit_button)
        self.submit_part.addWidget(self.quota_label)
        self.result_label = QLabel("Result:")
        self.result_label.setStyleSheet(f"font-size: {SMALL_TITLE_FONT_SIZE}px; font-weight: bold")
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet(f"font-size: {RESULT_FONT_SIZE}px;")

        # Add widgets to layouts
        question_list_layout.addWidget(QLabel("Questions List"))
        question_list_layout.addWidget(self.question_list_ui)
        
        question_detail_layout.addWidget(self.question_title, alignment=Qt.AlignTop)
        question_detail_layout.addWidget(self.question_description_label, alignment=Qt.AlignTop)
        question_detail_layout.addWidget(self.question_description, alignment=Qt.AlignTop)
        question_detail_layout.addWidget(self.answer_label, alignment=Qt.AlignBottom)
        question_detail_layout.addWidget(self.answer_text, alignment=Qt.AlignBottom)
        question_detail_layout.addLayout(self.submit_part)

        answer_layout.addWidget(self.result_label)
        answer_layout.addWidget(self.result_text)

        main_layout.addLayout(question_list_layout)
        main_layout.addLayout(question_detail_layout)
        main_layout.addLayout(answer_layout)

        self.update_question_list()

    def update_question_list(self):
        status, questions = self.api_loader.get_questions()
        if not status:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            sys.exit(0)
        self.question_info_list = []
        if questions is not None:
            qid = 1
            for question in questions:
                title = str(qid) + ". " + question["title"]
                self.question_list_ui.addItem(title)
                self.question_info_list.append(question)
                qid += 1
        else:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            sys.exit(0)

    def load_question_info(self, current_item):
        q_index = int(current_item.text().split(".")[0]) - 1
        question_info = self.question_info_list[q_index]
        status, question_info = self.api_loader.get_question_info(question_info["id"])
        if not status:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            return
        self.question_info_list[q_index]["quota"] = question_info["quota"]
        question_title = question_info["title"]
        question_description = question_info["description"]
        self.quota_label.setText(f"Quota: {question_info['quota']}")
        self.answer_text.clear()
        script = ""
        for line in question_info["start_code_template_file"]:
            script += line
        self.answer_text.setText(script)
        self.question_title.setText(question_title)
        self.question_description.setText(question_description)
        self.question_list_ui.setCurrentRow(q_index)
        if self.question_info_list[q_index]["quota"] == 0 or self.question_info_list[q_index]["finished"]:
            self.submit_button.setDisabled(True)
            self.quota_label.setText("You have already finished this question.")
        else:
            self.submit_button.setDisabled(False)
    
    def submit_answer(self):
        self.submit_button.setDisabled(True)
        answer = self.answer_text.toPlainText()
        ui_qid = self.question_list_ui.currentRow()
        qid = self.question_info_list[ui_qid]["id"]
        status, result = self.api_loader.submit_answer(qid, answer)
        if not status:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            return
        self.question_info_list[ui_qid]['quota'] -= 1
        self.quota_label.setText(f"Quota: {self.question_info_list[ui_qid]['quota']}")
        if not result["status"]:
            self.result_text.setText(result["message"])
            self.submit_button.setDisabled(False)
        else:
            QMessageBox.information(self, "Congratulations!", "You have successfully finished the question.")
            self.question_info_list[ui_qid]["finished"] = True
            self.quota_label.setText("You have already finished this question.")
        

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(QSize(400, 200))
        
        self.login_page = LoginPage(self)
        self.setCentralWidget(self.login_page)
        
    def show_main_window(self, api_loader):
        self.main_window = MainWindow(api_loader)
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())