import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import sqlite3
import PyPDF2
from docx import Document

# Load environment variables
load_dotenv()

class CaptainLogic:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.setup_langchain()
        self.setup_database()

    def setup_langchain(self):
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=ConversationBufferMemory()
        )

    def setup_database(self):
        self.conn = sqlite3.connect('captain.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications
            (id INTEGER PRIMARY KEY, company TEXT, date TEXT, status TEXT)
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes
            (id INTEGER PRIMARY KEY, content TEXT, is_main INTEGER)
        ''')
        self.conn.commit()

    def process_resume(self, file_path):
        try:
            content = ""
            if file_path.lower().endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        content += page.extract_text()
            elif file_path.lower().endswith('.docx'):
                doc = Document(file_path)
                for para in doc.paragraphs:
                    content += para.text + "\n"
            else:
                raise ValueError("Unsupported file format. Please upload a PDF or Word document.")

            self.cursor.execute('INSERT INTO resumes (content, is_main) VALUES (?, ?)', (content, 1))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error processing resume: {e}")
            return False

    def add_application(self, company, date):
        self.cursor.execute('INSERT INTO applications (company, date, status) VALUES (?, ?, ?)',
                            (company, date, 'New'))
        self.conn.commit()

    def get_applications(self):
        self.cursor.execute('SELECT * FROM applications')
        return self.cursor.fetchall()

    def update_application(self, id, company, date, status):
        self.cursor.execute('UPDATE applications SET company=?, date=?, status=? WHERE id=?',
                            (company, date, status, id))
        self.conn.commit()

    def delete_application(self, id):
        self.cursor.execute('DELETE FROM applications WHERE id=?', (id,))
        self.conn.commit()

    def get_resumes(self):
        self.cursor.execute('SELECT * FROM resumes')
        return self.cursor.fetchall()

    def delete_resume(self, id):
        self.cursor.execute('DELETE FROM resumes WHERE id=?', (id,))
        self.conn.commit()

    def send_message(self, message):
        try:
            response = self.conversation.predict(input=message)
            return response
        except Exception as e:
            return f"Error: {str(e)}"