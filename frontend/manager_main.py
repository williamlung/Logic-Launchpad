import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QTextEdit, QPushButton, QLineEdit, QMessageBox
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QKeySequence
from api_port import ManageTools

class NoPasteTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        # Check if the key combination is Ctrl+V (or Command+V on macOS)
        if event.matches(QKeySequence.Paste):
            # Ignore the event, effectively disabling the paste function
            return
        else:
            # Pass the event to the base class for normal processing
            super().keyPressEvent(event)
    
class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Questions Manager Login")
        self.setFixedSize(QSize(400, 250))
        
        layout = QVBoxLayout(self)
        self.server_label = QLabel("Server URL:")
        self.server_input = QLineEdit()
        self.server_input.setText("127.0.0.1:8000")

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.week_label = QLabel("Week:")
        self.week_input = QLineEdit()
        self.week_input.setText("1")
        
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(150)
        self.login_button.clicked.connect(self.check_login)
        
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.week_label)
        layout.addWidget(self.week_input)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        
    def check_login(self):
        url = self.server_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        week = self.week_input.text()
        api_loder = ManageTools(url, week)
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
        
        self.setWindowTitle("Questionnaire")
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
        self.question_list = QListWidget()
        self.question_list.setFixedWidth(250)
        questions = self.api_loader.get_questions()
        self.question_info_list = []
        if questions is not None:
            qid = 1
            for question in questions:
                title = str(qid) + ". " + question["title"]
                self.question_list.addItem(title)
                qid += 1
                self.question_info_list.append(question)
        else:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            sys.exit(0)

        #self.question_list.currentItemChanged.connect(self.load_question)
        
        # Question Detail
        self.question_title = QLabel("Select a question")
        self.question_title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px")
        self.question_title.setFixedHeight(100)
        self.question_description = QLabel("Description will appear here.")
        self.question_description.setStyleSheet("font-size: 14px; margin: 10px")
        self.question_description.setFixedHeight(700)
        self.question_description.setWordWrap(True)
        self.answer_text = NoPasteTextEdit()
        self.answer_text.setFixedWidth(800)
        self.submit_part = QHBoxLayout()
        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedWidth(100)
        self.submit_button.clicked.connect(self.submit_answer)
        self.quota_label = QLabel("Quota: 0")
        self.quota_label.setStyleSheet("font-size: 12px;")
        self.submit_part.addWidget(self.submit_button)
        self.submit_part.addWidget(self.quota_label)
        
        # Add widgets to layouts
        question_list_layout.addWidget(QLabel("Questions List"))
        question_list_layout.addWidget(self.question_list)
        
        question_detail_layout.addWidget(self.question_title, alignment=Qt.AlignTop)
        question_detail_layout.addWidget(self.question_description, alignment=Qt.AlignTop)

        answer_layout.addWidget(QLabel("Your Answer:"))
        answer_layout.addWidget(self.answer_text)
        answer_layout.addLayout(self.submit_part)
        
        main_layout.addLayout(question_list_layout)
        main_layout.addLayout(question_detail_layout)
        main_layout.addLayout(answer_layout)
                
    
    def load_question(self, current_item):
        if current_item is not None:
            q_index = int(current_item.text().split(".")[0]) - 1
            current_item = self.question_info_list[q_index]
            question_info = self.api_loader.get_question_info(current_item["id"])
            question_title = question_info["title"]
            # Here you would load the actual question details from a data source
            question_description = question_info["description"]
            self.quota_label.setText(f"Quota: {question_info['quota']}")
            self.answer_text.clear()
            for line in question_info["start_code_template_file"]:
                self.answer_text.append(line.replace("\r\n", ""))
            self.question_title.setText(question_title)
            self.question_description.setText(question_description)
    
    def submit_answer(self):
        answer = self.answer_text.toPlainText()
        question = self.question_title.text()
        print(f"Submitted answer for {question}: {answer}")
        self.answer_text.clear()

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(QSize(400, 250))
        
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