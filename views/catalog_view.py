import tkinter as tk
from tkinter import ttk, messagebox
from models.course import Course
from models.enrollment import Enrollment
from controllers.course_controller import CourseController

class CatalogView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.controller = CourseController()
        self.create_widgets()
        self.load_courses()

    def create_widgets(self):
        top_frame = ttk.Frame(self.parent)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top_frame, text="Каталог курсов", font=("Arial", 18)).pack(side=tk.LEFT)

        # Фильтры
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Уровень:").pack(side=tk.LEFT)
        self.level_var = tk.StringVar(value="all")
        levels = [("Все", "all"), ("Начальный", "beginner"), ("Средний", "intermediate"), ("Продвинутый", "advanced")]
        for text, val in levels:
            ttk.Radiobutton(filter_frame, text=text, variable=self.level_var, value=val, command=self.load_courses).pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Поиск:").pack(side=tk.LEFT, padx=(20,5))
        self.search_entry = ttk.Entry(filter_frame, width=20)
        self.search_entry.pack(side=tk.LEFT)
        ttk.Button(filter_frame, text="Найти", command=self.load_courses).pack(side=tk.LEFT, padx=5)

        # Таблица курсов
        columns = ("id", "Название", "Преподаватель", "Цена", "Уровень", "Рейтинг")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.on_course_select)

    def load_courses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        level = self.level_var.get() if self.level_var.get() != "all" else None
        search = self.search_entry.get().strip()
        courses = Course.get_all(filter_level=level, search=search)
        for c in courses:
            level_text = {"beginner":"Начальный","intermediate":"Средний","advanced":"Продвинутый"}.get(c['level'], c['level'])
            self.tree.insert("", tk.END, values=(c['id'], c['title'], c['teacher_name'], f"{c['price']} ₽", level_text, c['rating']))

    def on_course_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        course_id = self.tree.item(selected[0])['values'][0]
        # Детальная страница
        self.show_course_detail(course_id)

    def show_course_detail(self, course_id):
        course = Course.get_by_id(course_id)
        if not course:
            return
        detail = tk.Toplevel(self.parent)
        detail.title(course['title'])
        detail.geometry("500x400")
        ttk.Label(detail, text=course['title'], font=("Arial", 16)).pack(pady=10)
        ttk.Label(detail, text=f"Преподаватель: {course['teacher_name']}").pack(anchor=tk.W, padx=10)
        ttk.Label(detail, text=f"Уровень: {course['level']}").pack(anchor=tk.W, padx=10)
        ttk.Label(detail, text=f"Цена: {course['price']} ₽").pack(anchor=tk.W, padx=10)
        ttk.Label(detail, text="Описание:").pack(anchor=tk.W, padx=10)
        desc = tk.Text(detail, height=5, wrap=tk.WORD)
        desc.insert(tk.END, course['description'] or "")
        desc.config(state=tk.DISABLED)
        desc.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        if self.user['role'] == 'student':
            # Проверить, записан ли уже
            from models.enrollment import Enrollment
            enrollments = Enrollment.get_student_courses(self.user['id'])
            enrolled = any(e['id'] == course_id for e in enrollments)
            if not enrolled:
                def do_enroll():
                    if Enrollment.enroll(self.user['id'], course_id):
                        messagebox.showinfo("Успех", "Вы записаны на курс")
                        detail.destroy()
                    else:
                        messagebox.showerror("Ошибка", "Не удалось записаться")
                ttk.Button(detail, text="Записаться на курс", command=do_enroll).pack(pady=10)
            else:
                ttk.Label(detail, text="Вы уже записаны на этот курс", foreground="green").pack(pady=5)