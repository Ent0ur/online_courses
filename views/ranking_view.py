import tkinter as tk
from tkinter import ttk, messagebox
from core.database import Database

class RankingView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка 1: Рейтинг студентов
        student_frame = ttk.Frame(notebook)
        notebook.add(student_frame, text="🏆 Рейтинг студентов")
        self.create_student_ranking(student_frame)

        # Вкладка 2: Рейтинг преподавателей
        teacher_frame = ttk.Frame(notebook)
        notebook.add(teacher_frame, text="👨‍🏫 Рейтинг преподавателей")
        self.create_teacher_ranking(teacher_frame)

        # Вкладка 3: Рейтинг курсов
        course_frame = ttk.Frame(notebook)
        notebook.add(course_frame, text="📚 Рейтинг курсов")
        self.create_course_ranking(course_frame)

        # Вкладка 4: Мои достижения (для студента)
        if self.user['role'] == 'student':
            my_frame = ttk.Frame(notebook)
            notebook.add(my_frame, text="⭐ Мои достижения")
            self.create_my_achievements(my_frame)

    def create_student_ranking(self, parent):
        """Рейтинг студентов по баллам"""
        # Заголовок с пояснением
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text="Студенты получают баллы за прохождение тестов (+бонус 10 баллов за полное завершение курса)",
                  foreground="gray", font=("Arial", 9)).pack()

        # Таблица
        columns = ("place", "full_name", "total_points", "courses_completed", "tests_passed")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        tree.heading("place", text="Место")
        tree.heading("full_name", text="Студент")
        tree.heading("total_points", text="Всего баллов")
        tree.heading("courses_completed", text="Завершено курсов")
        tree.heading("tests_passed", text="Пройдено тестов")
        
        tree.column("place", width=60, anchor=tk.CENTER)
        tree.column("full_name", width=200)
        tree.column("total_points", width=100, anchor=tk.CENTER)
        tree.column("courses_completed", width=120, anchor=tk.CENTER)
        tree.column("tests_passed", width=120, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Загрузка данных
        db = Database()
        students = db.fetch_all("""
            SELECT 
                u.id,
                u.full_name, 
                s.total_points,
                (SELECT COUNT(*) FROM enrollments e WHERE e.student_id = u.id AND e.completed_at IS NOT NULL) as courses_completed,
                (SELECT COUNT(*) FROM lesson_progress lp WHERE lp.student_id = u.id AND lp.completed = 1 AND lp.score > 0) as tests_passed
            FROM students s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.total_points DESC
        """)
        
        for i, student in enumerate(students, 1):
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "
            tree.insert("", tk.END, values=(
                f"{medal}{i}",
                student['full_name'] or "—",
                student['total_points'],
                student['courses_completed'],
                student['tests_passed']
            ))

    def create_teacher_ranking(self, parent):
        """Рейтинг преподавателей по количеству студентов и рейтингу курсов"""
        # Таблица
        columns = ("place", "full_name", "students_count", "courses_count", "avg_course_rating")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        tree.heading("place", text="Место")
        tree.heading("full_name", text="Преподаватель")
        tree.heading("students_count", text="Всего студентов")
        tree.heading("courses_count", text="Курсов создано")
        tree.heading("avg_course_rating", text="Ср. рейтинг курсов")
        
        tree.column("place", width=60, anchor=tk.CENTER)
        tree.column("full_name", width=200)
        tree.column("students_count", width=120, anchor=tk.CENTER)
        tree.column("courses_count", width=120, anchor=tk.CENTER)
        tree.column("avg_course_rating", width=130, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        db = Database()
        teachers = db.fetch_all("""
            SELECT 
                u.full_name,
                COUNT(DISTINCT e.student_id) as students_count,
                COUNT(DISTINCT c.id) as courses_count,
                AVG(c.rating) as avg_course_rating
            FROM teachers t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN courses c ON c.teacher_id = t.user_id
            LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY t.user_id
            ORDER BY students_count DESC, avg_course_rating DESC
        """)
        
        for i, teacher in enumerate(teachers, 1):
            tree.insert("", tk.END, values=(
                i,
                teacher['full_name'] or "—",
                teacher['students_count'] or 0,
                teacher['courses_count'] or 0,
                f"{teacher['avg_course_rating'] or 0:.1f}"
            ))

    def create_course_ranking(self, parent):
        """Рейтинг курсов по сложности и популярности"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка: По популярности
        popular_frame = ttk.Frame(notebook)
        notebook.add(popular_frame, text="🔥 По популярности")
        self.create_popular_courses(popular_frame)

        # Вкладка: По сложности
        difficulty_frame = ttk.Frame(notebook)
        notebook.add(difficulty_frame, text="⭐ По сложности")
        self.create_difficulty_ranking(difficulty_frame)

    def create_popular_courses(self, parent):
        """Самые популярные курсы"""
        columns = ("place", "title", "teacher", "students_count", "rating")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        tree.heading("place", text="Место")
        tree.heading("title", text="Название курса")
        tree.heading("teacher", text="Преподаватель")
        tree.heading("students_count", text="Студентов")
        tree.heading("rating", text="Рейтинг")
        
        tree.column("place", width=60, anchor=tk.CENTER)
        tree.column("title", width=250)
        tree.column("teacher", width=180)
        tree.column("students_count", width=100, anchor=tk.CENTER)
        tree.column("rating", width=100, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        db = Database()
        courses = db.fetch_all("""
            SELECT 
                c.title,
                u.full_name as teacher_name,
                COUNT(e.student_id) as students_count,
                c.rating
            FROM courses c
            JOIN teachers t ON c.teacher_id = t.user_id
            JOIN users u ON t.user_id = u.id
            LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY c.id
            ORDER BY students_count DESC, c.rating DESC
            LIMIT 10
        """)
        
        for i, course in enumerate(courses, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}"
            tree.insert("", tk.END, values=(
                medal,
                course['title'],
                course['teacher_name'] or "—",
                course['students_count'] or 0,
                f"{course['rating'] or 0:.1f}"
            ))

    def create_difficulty_ranking(self, parent):
        """Рейтинг курсов по сложности (средний балл студентов за тесты)"""
        columns = ("place", "title", "teacher", "avg_test_score", "difficulty")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        tree.heading("place", text="Место")
        tree.heading("title", text="Название курса")
        tree.heading("teacher", text="Преподаватель")
        tree.heading("avg_test_score", text="Ср. балл за тесты")
        tree.heading("difficulty", text="Сложность")
        
        tree.column("place", width=60, anchor=tk.CENTER)
        tree.column("title", width=250)
        tree.column("teacher", width=180)
        tree.column("avg_test_score", width=120, anchor=tk.CENTER)
        tree.column("difficulty", width=100, anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        db = Database()
        courses = db.fetch_all("""
            SELECT 
                c.title,
                u.full_name as teacher_name,
                AVG(lp.score) as avg_score,
                c.level
            FROM courses c
            JOIN teachers t ON c.teacher_id = t.user_id
            JOIN users u ON t.user_id = u.id
            JOIN lessons l ON c.id = l.course_id
            JOIN lesson_progress lp ON l.id = lp.lesson_id
            WHERE l.lesson_type = 'quiz'
            GROUP BY c.id
            ORDER BY avg_score ASC
        """)
        
        difficulty_map = {
            'beginner': '🌱 Начальный',
            'intermediate': '📘 Средний',
            'advanced': '🔥 Продвинутый'
        }
        
        for i, course in enumerate(courses, 1):
            avg_score = course['avg_score'] or 0
            # Определяем уровень сложности на основе среднего балла
            if avg_score <= 3:
                difficulty_level = "🔴 Сложный"
            elif avg_score <= 7:
                difficulty_level = "🟡 Средний"
            else:
                difficulty_level = "🟢 Лёгкий"
            
            tree.insert("", tk.END, values=(
                i,
                course['title'],
                course['teacher_name'] or "—",
                f"{avg_score:.1f} / 10",
                difficulty_level
            ))

    def create_my_achievements(self, parent):
        """Мои достижения (для студента)"""
        db = Database()
        
        # Получаем данные студента
        student = db.fetch_one(
            "SELECT total_points FROM students WHERE user_id = ?",
            (self.user['id'],)
        )
        
        completed_courses = db.fetch_all("""
            SELECT c.title, c.level, e.completed_at, e.progress_percent
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = ? AND e.completed_at IS NOT NULL
        """, (self.user['id'],))
        
        total_points = student['total_points'] if student else 0
        
        # Статистика
        stats_frame = ttk.LabelFrame(parent, text="📊 Моя статистика", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(stats_frame, text=f"Всего баллов: {total_points}", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"Завершено курсов: {len(completed_courses)}", font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        
        # Определение уровня
        if total_points >= 100:
            level = "🏆 Гранд-мастер"
            color = "gold"
        elif total_points >= 50:
            level = "⭐ Эксперт"
            color = "silver"
        elif total_points >= 25:
            level = "📚 Ученик"
            color = "#cd7f32"
        else:
            level = "🌱 Новичок"
            color = "green"
        
        ttk.Label(stats_frame, text=f"Ваш уровень: {level}", foreground=color, font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        # Завершённые курсы
        if completed_courses:
            courses_frame = ttk.LabelFrame(parent, text="✅ Завершённые курсы", padding=10)
            courses_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for course in completed_courses:
                frame = ttk.Frame(courses_frame)
                frame.pack(fill=tk.X, pady=5)
                ttk.Label(frame, text=f"📘 {course['title']}", font=("Arial", 10)).pack(side=tk.LEFT)
                ttk.Label(frame, text=f"Завершён", foreground="green").pack(side=tk.RIGHT)
        else:
            ttk.Label(parent, text="Пока нет завершённых курсов. Запишитесь на курс и пройдите все уроки!",
                      foreground="gray", font=("Arial", 11)).pack(pady=50)