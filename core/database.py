import sqlite3
import os
from contextlib import closing

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.conn = None
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'courses.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()

    def execute(self, query, params=()):
        """Выполняет запрос без возврата данных (INSERT, UPDATE, DELETE, CREATE)"""
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(query, params)
            self.conn.commit()
            return cursor

    def fetch_all(self, query, params=()):
        """Возвращает все строки результата запроса"""
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query, params=()):
        """Возвращает одну строку результата запроса"""
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def create_tables(self):
        queries = [
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin','teacher','student','guest')),
                full_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS teachers (
                user_id INTEGER PRIMARY KEY,
                specialization TEXT,
                bio TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS students (
                user_id INTEGER PRIMARY KEY,
                total_points INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )""",
            """CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                price REAL DEFAULT 0,
                level TEXT CHECK(level IN ('beginner','intermediate','advanced')),
                teacher_id INTEGER,
                rating REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(user_id)
            )""",
            """CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                title TEXT NOT NULL,
                lesson_type TEXT CHECK(lesson_type IN ('video','text','quiz')),
                content TEXT,
                order_num INTEGER,
                duration INTEGER,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )""",
            """CREATE TABLE IF NOT EXISTS enrollments (
                student_id INTEGER,
                course_id INTEGER,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                progress_percent INTEGER DEFAULT 0,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students(user_id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )""",
            """CREATE TABLE IF NOT EXISTS lesson_progress (
                student_id INTEGER,
                lesson_id INTEGER,
                completed BOOLEAN DEFAULT 0,
                score INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                PRIMARY KEY (student_id, lesson_id),
                FOREIGN KEY (student_id) REFERENCES students(user_id),
                FOREIGN KEY (lesson_id) REFERENCES lessons(id)
            )""",
            """CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        ]
        for q in queries:
            self.execute(q)