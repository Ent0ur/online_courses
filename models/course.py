from core.database import Database
from core.logger import log_action

class Course:
    @staticmethod
    def create(title, description, price, level, teacher_id):
        db = Database()
        cursor = db.execute(
            "INSERT INTO courses (title, description, price, level, teacher_id) VALUES (?, ?, ?, ?, ?)",
            (title, description, price, level, teacher_id)
        )
        course_id = cursor.lastrowid
        log_action(teacher_id, f"Created course {course_id}")
        return course_id

    @staticmethod
    def get_all(filter_level=None, search=None):
        db = Database()
        query = "SELECT c.*, u.full_name as teacher_name FROM courses c LEFT JOIN teachers t ON c.teacher_id = t.user_id LEFT JOIN users u ON t.user_id = u.id"
        params = []
        conditions = []
        if filter_level:
            conditions.append("c.level = ?")
            params.append(filter_level)
        if search:
            conditions.append("c.title LIKE ?")
            params.append(f"%{search}%")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        return db.fetch_all(query, params)

    @staticmethod
    def get_by_id(course_id):
        db = Database()
        return db.fetch_one("SELECT c.*, u.full_name as teacher_name FROM courses c LEFT JOIN teachers t ON c.teacher_id = t.user_id LEFT JOIN users u ON t.user_id = u.id WHERE c.id = ?", (course_id,))

    @staticmethod
    def update_rating(course_id):
        db = Database()
        # Простая средняя оценка из тестов студентов (имитация)
        # В реальности можно считать из lesson_progress.score
        db.execute("UPDATE courses SET rating = (SELECT AVG(score) FROM lesson_progress WHERE lesson_id IN (SELECT id FROM lessons WHERE course_id=?)) WHERE id=?", (course_id, course_id))

class Lesson:
    @staticmethod
    def add(course_id, title, lesson_type, content, order_num, duration=0):
        db = Database()
        db.execute(
            "INSERT INTO lessons (course_id, title, lesson_type, content, order_num, duration) VALUES (?, ?, ?, ?, ?, ?)",
            (course_id, title, lesson_type, content, order_num, duration)
        )
        log_action(None, f"Lesson added to course {course_id}")

    @staticmethod
    def get_by_course(course_id):
        db = Database()
        return db.fetch_all("SELECT * FROM lessons WHERE course_id = ? ORDER BY order_num", (course_id,))

    @staticmethod
    def delete(lesson_id):
        db = Database()
        db.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))