from core.database import Database
from core.logger import log_action

class Enrollment:
    @staticmethod
    def enroll(student_id, course_id):
        db = Database()
        exists = db.fetch_one("SELECT 1 FROM enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id))
        if exists:
            return False
        db.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
        log_action(student_id, f"Enrolled in course {course_id}")
        return True

    @staticmethod
    def get_student_courses(student_id):
        db = Database()
        return db.fetch_all(
            "SELECT c.*, e.progress_percent, e.completed_at FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE e.student_id = ?",
            (student_id,)
        )

    @staticmethod
    def update_progress(student_id, course_id):
        db = Database()
        lessons = db.fetch_all("SELECT id FROM lessons WHERE course_id = ?", (course_id,))
        total = len(lessons)
        if total == 0:
            progress = 100
        else:
            completed = db.fetch_one(
                "SELECT COUNT(*) as cnt FROM lesson_progress WHERE student_id = ? AND lesson_id IN (SELECT id FROM lessons WHERE course_id = ?) AND completed = 1",
                (student_id, course_id)
            )['cnt']
            progress = int(completed / total * 100)
        
        # Проверяем, был ли курс уже завершён ранее
        old_enrollment = db.fetch_one(
            "SELECT completed_at, progress_percent FROM enrollments WHERE student_id = ? AND course_id = ?",
            (student_id, course_id)
        )
        
        db.execute("UPDATE enrollments SET progress_percent = ? WHERE student_id = ? AND course_id = ?",
                   (progress, student_id, course_id))
        
        # Если курс только что завершён (прогресс стал 100% и ранее не был завершён)
        if progress == 100 and old_enrollment and old_enrollment['completed_at'] is None:
            db.execute("UPDATE enrollments SET completed_at = CURRENT_TIMESTAMP WHERE student_id = ? AND course_id = ?",
                       (student_id, course_id))
            # Добавляем бонусные баллы за завершение курса
            db.execute("UPDATE students SET total_points = total_points + 10 WHERE user_id = ?", (student_id,))
            log_action(student_id, f"Completed course {course_id} and earned 10 bonus points")