import tkinter as tk
from tkinter import ttk, messagebox
from core.database import Database  # ← добавьте этот импорт
from models.enrollment import Enrollment
from models.course import Course, Lesson
from controllers.enrollment_controller import EnrollmentController
from views.lesson_view import LessonView
from views.quiz_view import QuizView

class MyCoursesView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.controller = EnrollmentController()
        self.create_widgets()
        self.load_courses()

    def create_widgets(self):
        ttk.Label(self.parent, text="Мои курсы", font=("Arial", 18)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Таблица курсов
        columns = ("id", "Название", "Прогресс", "Дата завершения")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Прогресс", text="Прогресс")
        self.tree.heading("Дата завершения", text="Дата завершения")
        self.tree.column("id", width=50)
        self.tree.column("Название", width=300)
        self.tree.column("Прогресс", width=100)
        self.tree.column("Дата завершения", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.open_course)

    def load_courses(self):
        """Загружает курсы студента"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        courses = Enrollment.get_student_courses(self.user['id'])
        for c in courses:
            completed = c['completed_at'] if c['completed_at'] else "—"
            self.tree.insert("", tk.END, values=(c['id'], c['title'], f"{c['progress_percent']}%", completed))

    def open_course(self, event):
        """Открывает окно прохождения курса"""
        selected = self.tree.selection()
        if not selected:
            return
        course_id = self.tree.item(selected[0])['values'][0]
        
        # Получаем уроки курса
        lessons = Lesson.get_by_course(course_id)
        course = Course.get_by_id(course_id)
        if not lessons:
            messagebox.showinfo("Инфо", "В курсе пока нет уроков")
            return
        
        # Создаём окно прохождения
        win = tk.Toplevel(self.parent)
        win.title(course['title'])
        win.geometry("800x600")

        # Заголовок и прогресс
        ttk.Label(win, text=course['title'], font=("Arial", 16)).pack(pady=10)
        progress_label = ttk.Label(win, text="")
        progress_label.pack(pady=5)

        # Список уроков
        listbox = tk.Listbox(win, height=15, font=("Arial", 11))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Загружаем прогресс по урокам
        db = Database()
        lesson_status = {}
        for lesson in lessons:
            prog = db.fetch_one(
                "SELECT completed FROM lesson_progress WHERE student_id = ? AND lesson_id = ?",
                (self.user['id'], lesson['id'])
            )
            status = "✓" if prog and prog['completed'] else "○"
            listbox.insert(tk.END, f"{status} {lesson['order_num']}. {lesson['title']} ({lesson['lesson_type']})")
            lesson_status[lesson['id']] = prog['completed'] if prog else False
        
        def update_progress_bar():
            total = len(lessons)
            completed_count = sum(1 for s in lesson_status.values() if s)
            percent = int(completed_count/total*100) if total > 0 else 0
            progress_label.config(text=f"Прогресс курса: {percent}%")
            # Обновляем прогресс в БД
            Enrollment.update_progress(self.user['id'], course_id)
            self.load_courses()  # обновляем таблицу моих курсов
        
        update_progress_bar()

        def open_lesson():
            idx = listbox.curselection()
            if not idx:
                messagebox.showwarning("Внимание", "Выберите урок из списка")
                return
            lesson = lessons[idx[0]]
            if lesson['lesson_type'] == 'quiz':
                if lesson_status.get(lesson['id']):
                    messagebox.showinfo("Инфо", "Вы уже прошли этот тест")
                    return
                QuizView(
                    self.user, lesson, win,
                    on_complete=lambda: refresh_lesson_status(lesson)
                )
            else:
                LessonView(
                    self.user, lesson, win,
                    on_complete=lambda: mark_lesson_complete(lesson)
                )
        
        def refresh_lesson_status(lesson):
            """Обновляет статус урока после прохождения"""
            # Обновляем статус в словаре
            lesson_status[lesson['id']] = True
            # Обновляем список уроков
            for i in range(listbox.size()):
                listbox.delete(0)
            for l in lessons:
                status = "✓" if lesson_status.get(l['id']) else "○"
                listbox.insert(tk.END, f"{status} {l['order_num']}. {l['title']} ({l['lesson_type']})")
            update_progress_bar()
        
        def mark_lesson_complete(lesson):
            """Отмечает урок как пройденный (для видео и текста)"""
            db = Database()
            db.execute(
                "INSERT OR REPLACE INTO lesson_progress (student_id, lesson_id, completed, completed_at) VALUES (?, ?, 1, CURRENT_TIMESTAMP)",
                (self.user['id'], lesson['id'])
            )
            refresh_lesson_status(lesson)
            messagebox.showinfo("Успех", f"Урок «{lesson['title']}» отмечен как пройденный")
        
        # Кнопки
        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Открыть выбранный урок", command=open_lesson).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть", command=win.destroy).pack(side=tk.LEFT, padx=5)