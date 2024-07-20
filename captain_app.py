import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QListWidget,
                             QLabel, QFileDialog, QMessageBox, QInputDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QDate
from captain_logic import CaptainLogic

class CaptainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = CaptainLogic()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('CAPTAIN 🚢')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QLineEdit, QTextEdit {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #7F8C8D;
                border-radius: 3px;
            }
            QListWidget {
                background-color: #34495E;
                color: #ECF0F1;
                border: 1px solid #7F8C8D;
                border-radius: 3px;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Resume Tab
        resume_tab = QWidget()
        resume_layout = QVBoxLayout()
        resume_tab.setLayout(resume_layout)

        upload_btn = QPushButton('Upload Resume')
        upload_btn.clicked.connect(self.upload_resume)
        resume_layout.addWidget(upload_btn)

        self.resume_list = QListWidget()
        resume_layout.addWidget(self.resume_list)

        delete_resume_btn = QPushButton('Delete Resume')
        delete_resume_btn.clicked.connect(self.delete_resume)
        resume_layout.addWidget(delete_resume_btn)

        tabs.addTab(resume_tab, "Resumes")

        # Applications Tab
        app_tab = QWidget()
        app_layout = QVBoxLayout()
        app_tab.setLayout(app_layout)

        add_app_btn = QPushButton('Add Application')
        add_app_btn.clicked.connect(self.add_application)
        app_layout.addWidget(add_app_btn)

        self.app_list = QListWidget()
        app_layout.addWidget(self.app_list)

        delete_app_btn = QPushButton('Delete Application')
        delete_app_btn.clicked.connect(self.delete_application)
        app_layout.addWidget(delete_app_btn)

        tabs.addTab(app_tab, "Applications")

        # Chat Tab
        chat_tab = QWidget()
        chat_layout = QVBoxLayout()
        chat_tab.setLayout(chat_layout)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)

        chat_input = QLineEdit()
        chat_input.returnPressed.connect(lambda: self.send_message(chat_input.text()))
        chat_layout.addWidget(chat_input)

        send_btn = QPushButton('Send')
        send_btn.clicked.connect(lambda: self.send_message(chat_input.text()))
        chat_layout.addWidget(send_btn)

        tabs.addTab(chat_tab, "Chat")

        self.load_applications()
        self.load_resumes()

    def upload_resume(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Resume", "", "PDF Files (*.pdf);;Word Files (*.docx)")
        if file_path:
            try:
                if self.logic.process_resume(file_path):
                    QMessageBox.information(self, "Success", "Resume uploaded successfully!")
                    self.load_resumes()
                else:
                    QMessageBox.warning(self, "Error", "Failed to process the resume. Please check the file format and content.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while processing the resume: {str(e)}")

    def load_resumes(self):
        self.resume_list.clear()
        resumes = self.logic.get_resumes()
        for resume in resumes:
            self.resume_list.addItem(f"Resume {resume[0]}")

    def delete_resume(self):
        current_item = self.resume_list.currentItem()
        if current_item:
            resume_id = int(current_item.text().split()[1])
            self.logic.delete_resume(resume_id)
            self.load_resumes()

    def add_application(self):
        company, ok = QInputDialog.getText(self, 'Add Application', 'Enter company name:')
        if ok and company:
            date = QDate.currentDate().toString(Qt.ISODate)
            self.logic.add_application(company, date)
            self.load_applications()

    def load_applications(self):
        self.app_list.clear()
        applications = self.logic.get_applications()
        for app in applications:
            self.app_list.addItem(f"{app[1]} - {app[2]} - {app[3]}")

    def delete_application(self):
        current_item = self.app_list.currentItem()
        if current_item:
            app_id = self.app_list.row(current_item) + 1
            self.logic.delete_application(app_id)
            self.load_applications()

    def send_message(self, message):
        if message:
            self.chat_history.append(f"You: {message}")
            response = self.logic.send_message(message)
            self.chat_history.append(f"AI: {response}")
            self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

def main():
    app = QApplication(sys.argv)
    ex = CaptainApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
