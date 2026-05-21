from core.database import Database
from models.course import Course

class AnalyticsController:
    def get_top_courses(self, limit=5):
        """Топ-5 самых популярных курсов по количеству студентов"""
        db = Database()
        return db.fetch_all("""
            SELECT c.title, COUNT(e.student_id) as cnt
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY c.id
            ORDER BY cnt DESC
            LIMIT ?
        """, (limit,))

    def get_level_distribution(self):
        """Распределение курсов по уровням сложности"""
        db = Database()
        return db.fetch_all("""
            SELECT level, COUNT(*) as cnt 
            FROM courses 
            GROUP BY level
        """)

    def get_avg_performance(self):
        """Средняя успеваемость по курсам (средний балл за тесты)"""
        db = Database()
        # Получаем средний балл для каждого курса на основе пройденных тестов
        results = db.fetch_all("""
            SELECT 
                c.id,
                c.title, 
                COALESCE(AVG(lp.score), 0) as avg_score
            FROM courses c
            LEFT JOIN lessons l ON c.id = l.course_id AND l.lesson_type = 'quiz'
            LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.completed = 1
            GROUP BY c.id
            ORDER BY c.id
        """)
        
        # Если нет данных, возвращаем курсы с нулевыми значениями
        if not results or len(results) == 0:
            all_courses = Course.get_all()
            return [(c['title'], 0) for c in all_courses]
        
        return [(r['title'], round(r['avg_score'] or 0, 1)) for r in results]

    def get_student_ranking(self):
        """Рейтинг студентов по баллам"""
        db = Database()
        return db.fetch_all("""
            SELECT 
                u.id,
                u.full_name, 
                COALESCE(s.total_points, 0) as total_points
            FROM students s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.total_points DESC
        """)

    def get_teacher_ranking(self):
        """Рейтинг преподавателей по количеству студентов"""
        db = Database()
        return db.fetch_all("""
            SELECT 
                u.full_name, 
                COUNT(DISTINCT e.student_id) as student_count
            FROM teachers t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN courses c ON c.teacher_id = t.user_id
            LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY t.user_id
            ORDER BY student_count DESC
        """)

    def get_course_difficulty(self):
        """Рейтинг курсов по сложности (средний балл студентов за тесты)"""
        db = Database()
        return db.fetch_all("""
            SELECT 
                c.title, 
                COALESCE(AVG(lp.score), 0) as avg_score
            FROM courses c
            JOIN lessons l ON c.id = l.course_id AND l.lesson_type = 'quiz'
            LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id
            GROUP BY c.id
            ORDER BY avg_score ASC
        """)

    def get_full_report(self):
        """Полный отчёт для экспорта"""
        return {
            "courses": Course.get_all(),
            "students": self.get_student_ranking(),
            "teachers": self.get_teacher_ranking(),
            "popular_courses": self.get_top_courses(10)
        }