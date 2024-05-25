import datetime
import sys
import threading
import time

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QTextEdit, QPushButton, QLineEdit, QMessageBox,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QFileDialog
)
from PySide6.QtCore import QSize, Qt
from api_port import ManageTools

    
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
    def __init__(self, api_loader: ManageTools):
        super().__init__()
        self.api_loader = api_loader
        self.setWindowTitle("Fuck")
        self.setGeometry(100, 100, 1600, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel
        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel, 1)
        
        top_left_layout = QHBoxLayout()
        self.week_label = QLabel("Week: "+self.api_loader.week)
        self.week_label.setStyleSheet("font-size: 16px")
        top_left_layout.addWidget(self.week_label, alignment=Qt.AlignLeft)
        
        self.add_question_button = QPushButton("Add")
        self.add_question_button.clicked.connect(self.add_question)
        self.add_question_button.setFixedWidth(120)
        top_left_layout.addWidget(self.add_question_button, alignment=Qt.AlignRight)
        left_panel.addLayout(top_left_layout)
        
        self.question_list = QListWidget()
        self.reload_question_list()
        self.question_list.itemClicked.connect(self.select_question)
        left_panel.addWidget(self.question_list)

        # Middle panel
        question_info_panel = QVBoxLayout()
        main_layout.addLayout(question_info_panel, 1)
        
        self.title_label = QLabel("Title:")
        self.title_label.setStyleSheet("font-size: 16px")
        question_info_panel.addWidget(self.title_label)
        
        self.title_input = QLineEdit("")
        question_info_panel.addWidget(self.title_input)

        self.description_label = QLabel("Description:")
        self.description_label.setStyleSheet("font-size: 16px")
        question_info_panel.addWidget(self.description_label)
        
        self.description_input = QTextEdit("")
        question_info_panel.addWidget(self.description_input)
        
        self.script_label = QLabel("Start Script:")
        self.script_label.setStyleSheet("font-size: 16px")
        question_info_panel.addWidget(self.script_label)
        
        self.code_script_input = QTextEdit("")
        question_info_panel.addWidget(self.code_script_input)

        action_buttons_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_question)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_question)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_question)
        action_buttons_layout.addWidget(self.reset_button)
        action_buttons_layout.addWidget(self.delete_button)
        action_buttons_layout.addWidget(self.save_button)
        question_info_panel.addLayout(action_buttons_layout)
        # Test cases panel
        test_case_panel = QVBoxLayout()
        main_layout.addLayout(test_case_panel, 1)
        
        self.test_cases_label = QLabel("Test Cases:")
        self.test_cases_label.setStyleSheet("font-size: 16px")
        test_case_button_layout = QHBoxLayout()
        self.test_cases_details_label = QLabel(f"Total test cases: 0, Hidden test cases: 0")
        self.add_test_case_button = QPushButton("Add")
        self.add_test_case_button.clicked.connect(self.add_test_case)
        self.add_test_case_button.setFixedWidth(90)
        self.valid_test_cases_button = QPushButton("Validate")
        self.valid_test_cases_button.clicked.connect(self.valid_test_cases)
        self.valid_test_cases_button.setFixedWidth(90)
        test_case_panel.addWidget(self.test_cases_label)
        test_case_button_layout.addWidget(self.test_cases_details_label)
        test_case_button_layout.addWidget(self.valid_test_cases_button)
        test_case_button_layout.addWidget(self.add_test_case_button)
        test_case_panel.addLayout(test_case_button_layout)

        self.test_cases_table = QTableWidget(0, 4)
        self.test_cases_table.setHorizontalHeaderLabels(["Input", "Output", "Hidden", "Action"])
        self.test_cases_table.setColumnWidth(0, 120)
        self.test_cases_table.setColumnWidth(1, 120)
        self.test_cases_table.setColumnWidth(2, 50)
        self.test_cases_table.setColumnWidth(3, 70)
        header = self.test_cases_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        self.test_cases_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.test_cases_table.setSelectionMode(QTableWidget.NoSelection)
        self.test_cases_table.setFocusPolicy(Qt.NoFocus)
        test_case_panel.addWidget(self.test_cases_table)

        model_answer_label = QLabel("Model Answer:")
        model_answer_label.setStyleSheet("font-size: 16px")
        test_case_panel.addWidget(model_answer_label)
        self.model_answer_input = QTextEdit()
        test_case_panel.addWidget(self.model_answer_input)

        # Right panel
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel, 1)
        
        self.create_user_button = QPushButton("Create User")
        self.create_user_button.setFixedWidth(120)
        self.create_user_button.clicked.connect(lambda: CreateUserDialog(self).show())
        right_panel.addWidget(self.create_user_button, alignment=Qt.AlignRight)
        

        self.user_record_table = QTableWidget(0, 4)
        self.user_record_table.setHorizontalHeaderLabels(["Name", "Quota", "Completed", "Last Submit"])
        self.user_record_table.setColumnWidth(0, 120)
        self.user_record_table.setColumnWidth(1, 50)
        self.user_record_table.setColumnWidth(2, 80)
        self.user_record_table.setColumnWidth(3, 120)
        self.user_record_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_record_table.setSelectionMode(QTableWidget.NoSelection)
        self.user_record_table.setFocusPolicy(Qt.NoFocus)
        header = self.user_record_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        
        right_panel.addWidget(self.user_record_table)
        
        self.update_time_label = QLabel("Update time: 04/05/2024 19:32:28")
        right_panel.addWidget(self.update_time_label, alignment=Qt.AlignLeft)

        # select the first question
        if len(self.questions) > 0:
            self.select_question(0)
        else:
            self.title_input.setText("No question found")
            self.title_input.setReadOnly(True)
            self.description_input.setText("No question found")
            self.description_input.setReadOnly(True)
            self.code_script_input.setText("No question found")
            self.code_script_input.setReadOnly(True)
            self.add_test_case_button.setDisabled(True)
        
    def select_question(self, index):
        if type(index) != int:
            index = self.question_list.currentRow()
        qid = self.questions[index]["id"]
        question_info = self.api_loader.get_question_info(qid)
        self.title_input.setText(question_info["title"])
        self.description_input.setText(question_info["description"])
        script = ""
        for n in question_info["start_code_template_file"]:
            script += n
        self.code_script_input.setText(script)
        self.question_list.setCurrentRow(index)
        if not "update_userlist_thread" in dir(self):
            self.auto_update_userlist_thread()
        self.update_userlist()
        self.update_test_cases_list()
        self.add_test_case_button.setDisabled(False)
        self.title_input.setReadOnly(False)
        self.description_input.setReadOnly(False)
        self.code_script_input.setReadOnly(False)

    def add_test_case(self):
        self.add_test_case_dialog = AddTestCaseDialog(self, self.questions[self.question_list.currentRow()]["id"])
        self.add_test_case_dialog.show()

    def update_test_cases_list(self):
        qid = self.questions[self.question_list.currentRow()]["id"]
        self.test_cases = self.api_loader.get_test_cases(qid)
        if self.test_cases is None:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            sys.exit(0)
        test_case_for_ui = []
        for test_case in self.test_cases:
            input, output = "", ""
            for n in test_case["input"]:
                input += n
            for n in test_case["output"]:
                output += n
            test_case_for_ui.append([input, output, str(test_case["hidden"])])
        self.test_cases_table.setRowCount(len(test_case_for_ui))
        self.test_cases_table.clearContents()
        for row, data in enumerate(test_case_for_ui):
            for col, item in enumerate(data):
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, row=row: self.delete_test_case(self.test_cases[row]["id"]))
                delete_button.setFixedWidth(70)
                self.test_cases_table.setItem(row, col, QTableWidgetItem(item))
                self.test_cases_table.setCellWidget(row, 3, delete_button)
        self.test_cases_details_label.setText(f"Total test cases: {len(self.test_cases)}, Hidden test cases: {sum([1 for data in self.test_cases if data['hidden'] == 'False'])}")
        if len(self.test_cases) == 0:
            self.valid_test_cases_button.setDisabled(True)
        else:
            self.valid_test_cases_button.setDisabled(False)

    def delete_test_case(self, tid):
        # ask user confirmation
        index = self.test_cases_table.currentRow()
        confirm_delete = QMessageBox.question(self, "Delete", "Are you sure you want to delete the test case?", 
                                              QMessageBox.Yes | QMessageBox.No)
        if confirm_delete == QMessageBox.No:
            return
        tid = self.test_cases[index]["id"]
        response = self.api_loader.delete_test_case(tid)
        if response == None:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            sys.exit(0)
        if not response["status"]:
            QMessageBox.warning(self, "Error", response["message"])
        self.update_test_cases_list()

    def valid_test_cases(self):
        qid = self.questions[self.question_list.currentRow()]["id"]
        code = self.model_answer_input.toPlainText()
        response = self.api_loader.validate_test_cases(qid, code)
        if response == None:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            sys.exit(0)
        if "status" not in response:
            QMessageBox.warning(self, "Error", "Unable to validate test cases.")
            return
        if not response["status"]:
            QMessageBox.warning(self, "Error", response["message"])
        else:
            QMessageBox.information(self, "Success", response["message"])

    def add_question_to_list(self, question, index):
        item = QListWidgetItem()
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel(f"{index}. {question['title']}")
        layout.addWidget(label)
        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.question_list.addItem(item)
        self.question_list.setItemWidget(item, widget)

    def add_question(self):
        title = "New Question"
        description = "Description will appear here."
        start_code_template = "Start code template will appear here."
        response = self.api_loader.create_question(title, description, start_code_template)
        if response["status"]:
            question = {"title": title,
                        "description": description,
                        "start_code_template_file": start_code_template,
                        "week": self.api_loader.week,
                        "id": response["id"]}
            self.questions.append(question)
            self.add_question_to_list(question, len(self.questions))
        else:
            QMessageBox.warning(self, "Error", response["message"])
            sys.exit(0)

    def delete_question(self):
        # ask user confirmation
        index = self.question_list.currentRow()
        confirm_delete = QMessageBox.question(self, "Delete", "Are you sure you want to delete question - " + self.questions[index]["title"] + "?", 
                                              QMessageBox.Yes | QMessageBox.No)
        if confirm_delete == QMessageBox.No:
            return
        
        qid = self.questions[index]["id"]
        response = self.api_loader.delete_question(qid)
        if not response["status"]:
            QMessageBox.warning(self, "Error", response["message"])
            return
        self.questions.pop(index)
        self.question_list.takeItem(index)
        self.select_question(0)
        self.question_list.setCurrentRow(0)
        # update question list index
        for i in range(index, len(self.questions)):
            item = self.question_list.item(i)
            widget = self.question_list.itemWidget(item)
            label = widget.layout().itemAt(0).widget()
            label.setText(f"{i+1}. {self.questions[i]['title']}")
    
    def reset_question(self):
        confirm_reset = QMessageBox.question(self, "Reset", "Are you sure you want to reset the question?", 
                                            QMessageBox.Yes | QMessageBox.No)
        if confirm_reset == QMessageBox.No:
            return
        index = self.question_list.currentRow()
        question_info = self.api_loader.get_question_info(self.questions[index]["id"])
        self.title_input.setText(question_info["title"])
        self.description_input.setText(question_info["description"])
        script = ""
        for n in question_info["start_code_template_file"]:
            script += n
        self.code_script_input.setText(script)

    def save_question(self):
        confirm_save = QMessageBox.question(self, "Save", "Are you sure you want to save the question?",
                                             QMessageBox.Yes | QMessageBox.No)
        if confirm_save == QMessageBox.No:
            return
        index = self.question_list.currentRow()
        qid = self.questions[index]["id"]
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        script = self.code_script_input.toPlainText()
        response = self.api_loader.update_question(qid, title, description, script)
        if not response["status"]:
            QMessageBox.warning(self, "Error", response["message"])
        self.reload_question_list()
        self.select_question(index)

    def reload_question_list(self):
        self.questions = self.api_loader.get_questions()
        self.question_list.clear()
        question_id = 1
        for question in self.questions:
            self.add_question_to_list(question, question_id)
            question_id += 1

    def auto_update_userlist_thread(self):
        def auto_update_userlist(window):
            while True:
                window.update_userlist()
                time.sleep(10)

        self.update_userlist_thread = threading.Thread(target=auto_update_userlist, args=(self,))
        self.update_userlist_thread.start()

    def update_userlist(self):
        qid = self.questions[self.question_list.currentRow()]["id"]
        userlist = self.api_loader.get_user_list(qid)
        if userlist is None:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            sys.exit(0)
        self.user_record_table.setRowCount(len(userlist))
        self.user_record_table.clearContents()
        for user_info in userlist:
            name = user_info["username"]
            quota = user_info["quota"]
            completed = user_info["finished"]
            last_submit = user_info["last_submit_time"]
            self.user_record_table.setItem(userlist.index(user_info), 0, QTableWidgetItem(name))
            self.user_record_table.setItem(userlist.index(user_info), 1, QTableWidgetItem(str(quota)))
            self.user_record_table.setItem(userlist.index(user_info), 2, QTableWidgetItem(str(completed)))
            self.user_record_table.setItem(userlist.index(user_info), 3, QTableWidgetItem(last_submit))
        
        now_time_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.update_time_label.setText(f"Update time: {now_time_str}")

class AddTestCaseDialog(QMainWindow):
    def __init__(self, parent: MainWindow, qid):
        super().__init__(parent)
        self.qid = qid
        self.setWindowTitle("Add Test Case")
        self.setFixedSize(QSize(400, 500))
        
        layout = QVBoxLayout()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(layout)
        
        input_layout = QHBoxLayout()
        self.input_label = QLabel("Input:")
        self.input_load_btn = QPushButton("Load from file")
        self.input_load_btn.clicked.connect(self.input_load_file)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_load_btn)
        self.input_input = QTextEdit()

        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output:")
        self.output_load_btn = QPushButton("Load from file")
        self.output_load_btn.clicked.connect(self.output_load_file)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_load_btn)
        self.output_input = QTextEdit()
        
        hidden_layout = QHBoxLayout()
        self.hidden_label = QLabel("Hidden:")
        self.hidden_input = QCheckBox()
        self.hidden_input.setChecked(False)
        hidden_layout.addWidget(self.hidden_label)
        hidden_layout.addWidget(self.hidden_input)

        self.add_button = QPushButton("Add")
        self.add_button.setFixedWidth(150)
        self.add_button.clicked.connect(self.add_test_case)
        
        layout.addLayout(input_layout)
        layout.addWidget(self.input_input)
        layout.addLayout(output_layout)
        layout.addWidget(self.output_input)
        layout.addLayout(hidden_layout)
        layout.addWidget(self.add_button, alignment=Qt.AlignCenter)
    
    def input_load_file(self):
        filepath = QFileDialog.getOpenFileName(self, "Open file", "", "Text files (*.txt)")[0]
        try:
            if filepath == "":
                return
            with open(filepath, "r") as f:
                self.input_input.setText(f.read())
        except:
            QMessageBox.warning(self, "Error", "Unable to open file.")

    def output_load_file(self):
        filepath = QFileDialog.getOpenFileName(self, "Open file", "", "Text files (*.txt)")[0]
        try:
            if filepath == "":
                return
            with open(filepath, "r") as f:
                self.output_input.setText(f.read())
        except:
            QMessageBox.warning(self, "Error", "Unable to open file.")

    def add_test_case(self):
        input = self.input_input.toPlainText()
        output = self.output_input.toPlainText()
        hidden = self.hidden_input.isChecked()
        self.parent().api_loader.create_test_case(self.qid, input, output, hidden)
        self.parent().update_test_cases_list()
        self.close()

class CreateUserDialog(QMainWindow):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.setWindowTitle("Create User")
        self.setFixedSize(QSize(400, 250))
        
        layout = QVBoxLayout()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(layout)
        
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()

        self.create_button = QPushButton("Create")
        self.create_button.setFixedWidth(150)
        self.create_button.clicked.connect(self.create_user)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.create_button, alignment=Qt.AlignCenter)
    
    def create_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        response = self.parent().api_loader.create_user(username, password)
        if response is None:
            QMessageBox.warning(self, "Error", "Unable to connect to server.")
            sys.exit(0)
        if not response["status"]:
            QMessageBox.warning(self, "Error", response["message"])
        else:
            QMessageBox.information(self, "Success", response["message"])
        self.close()

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