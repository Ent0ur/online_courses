import tkinter as tk
from tkinter import ttk, messagebox
from models.course import Course, Lesson
from core.database import Database

class CourseEditorView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.current_course_id = None
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка создания курса
        self.course_frame = ttk.Frame(notebook)
        notebook.add(self.course_frame, text="➕ Создать курс")
        self.create_course_tab()

        # Вкладка управления уроками
        self.lessons_frame = ttk.Frame(notebook)
        notebook.add(self.lessons_frame, text="📖 Управление уроками")
        self.create_lessons_tab()

    def create_course_tab(self):
        """Вкладка создания нового курса"""
        frame = ttk.Frame(self.course_frame, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Название курса:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(frame, width=50)
        self.title_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Описание:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.desc_text = tk.Text(frame, height=5, width=50)
        self.desc_text.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Цена (₽):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(frame, width=20)
        self.price_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)

        ttk.Label(frame, text="Уровень:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.level_var = tk.StringVar(value="beginner")
        level_combo = ttk.Combobox(frame, textvariable=self.level_var, 
                                   values=["beginner", "intermediate", "advanced"], 
                                   state="readonly", width=20)
        level_combo.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Пояснение по уровням
        level_info = ttk.Label(frame, text="beginner - Начальный | intermediate - Средний | advanced - Продвинутый",
                               foreground="gray", font=("Arial", 8))
        level_info.grid(row=4, column=1, sticky=tk.W, padx=5)

        def save_course():
            title = self.title_entry.get().strip()
            if not title:
                messagebox.showerror("Ошибка", "Введите название курса")
                return
            desc = self.desc_text.get("1.0", tk.END).strip()
            try:
                price = float(self.price_entry.get()) if self.price_entry.get() else 0
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом")
                return
            level = self.level_var.get()
            
            teacher_id = self.user['id']
            
            # Проверяем, есть ли пользователь в таблице teachers
            db = Database()
            if not db.fetch_one("SELECT user_id FROM teachers WHERE user_id = ?", (teacher_id,)):
                # Если админ создаёт курс, добавляем его в teachers
                db.execute("INSERT INTO teachers (user_id, specialization) VALUES (?, ?)", 
                          (teacher_id, "Преподаватель" if self.user['role'] == 'admin' else "Преподаватель"))
                messagebox.showinfo("Информация", "Вы добавлены в список преподавателей")
            
            course_id = Course.create(title, desc, price, level, teacher_id)
            messagebox.showinfo("Успех", f"Курс «{title}» создан!\nID курса: {course_id}")
            
            # Очищаем поля
            self.title_entry.delete(0, tk.END)
            self.desc_text.delete("1.0", tk.END)
            self.price_entry.delete(0, tk.END)
            
            # Обновляем список курсов во вкладке уроков
            self.load_my_courses()

        ttk.Button(frame, text="💾 Сохранить курс", command=save_course, width=20).grid(row=5, column=0, columnspan=2, pady=20)

    def create_lessons_tab(self):
        """Вкладка управления уроками (только свои курсы)"""
        frame = ttk.Frame(self.lessons_frame, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # ===== Блок выбора курса =====
        select_frame = ttk.LabelFrame(frame, text="Выберите свой курс", padding=10)
        select_frame.pack(fill=tk.X, pady=5)
        
        # Список курсов преподавателя
        ttk.Label(select_frame, text="Мои курсы:").pack(side=tk.LEFT, padx=5)
        self.course_combo = ttk.Combobox(select_frame, width=50, state="readonly")
        self.course_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.course_combo.bind("<<ComboboxSelected>>", self.on_course_selected)
        
        ttk.Button(select_frame, text="🔄 Обновить", command=self.load_my_courses).pack(side=tk.LEFT, padx=5)
        
        # Информация о выбранном курсе
        self.course_info_label = ttk.Label(select_frame, text="", foreground="blue")
        self.course_info_label.pack(side=tk.LEFT, padx=10)
        
        # ===== Список уроков =====
        lessons_frame = ttk.LabelFrame(frame, text="Уроки курса", padding=10)
        lessons_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Список уроков
        self.lessons_listbox = tk.Listbox(lessons_frame, height=10, font=("Arial", 10))
        self.lessons_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопка удаления урока
        delete_frame = ttk.Frame(lessons_frame)
        delete_frame.pack(fill=tk.X, pady=5)
        ttk.Button(delete_frame, text="🗑 Удалить выбранный урок", command=self.delete_selected_lesson).pack()
        
        # ===== Добавление урока =====
        add_frame = ttk.LabelFrame(frame, text="Добавить новый урок", padding=10)
        add_frame.pack(fill=tk.X, pady=10)
        
        # Название урока
        ttk.Label(add_frame, text="Название урока:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.lesson_title = ttk.Entry(add_frame, width=40)
        self.lesson_title.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Тип урока
        ttk.Label(add_frame, text="Тип урока:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.lesson_type = ttk.Combobox(add_frame, values=["video", "text", "quiz"], 
                                        state="readonly", width=20)
        self.lesson_type.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        self.lesson_type.current(0)
        
        # Пояснение по типам
        type_info = ttk.Label(add_frame, text="video - YouTube ссылка | text - обычный текст | quiz - JSON с вопросами",
                              foreground="gray", font=("Arial", 8))
        type_info.grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Содержимое
        ttk.Label(add_frame, text="Содержимое:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.lesson_content = tk.Text(add_frame, height=4, width=50)
        self.lesson_content.grid(row=3, column=1, padx=10, pady=5)
        
        # Пример содержимого
        def show_example():
            example_text = """Для video: https://youtu.be/example

Для text: Текст урока...

Для quiz: 
[
    {"question": "Вопрос 1?", "type": "single", "options": ["A","B","C"], "correct": "A"},
    {"question": "Вопрос 2?", "type": "text", "correct": "ответ"}
]"""
            messagebox.showinfo("Пример содержимого", example_text)
        
        ttk.Button(add_frame, text="❓ Пример", command=show_example).grid(row=3, column=2, padx=5, sticky=tk.N)
        
        # Порядковый номер
        ttk.Label(add_frame, text="Порядок:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.order_entry = ttk.Entry(add_frame, width=10)
        self.order_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(add_frame, text="(число, чем меньше - тем выше в списке)", 
                  foreground="gray", font=("Arial", 8)).grid(row=4, column=1, padx=120, sticky=tk.W)
        
        # Кнопка добавления
        ttk.Button(add_frame, text="➕ Добавить урок", command=self.add_lesson, width=20).grid(row=5, column=0, columnspan=2, pady=15)
        
        # Загружаем курсы преподавателя
        self.load_my_courses()

    def load_my_courses(self):
        """Загружает ТОЛЬКО курсы, созданные текущим преподавателем"""
        db = Database()
        
        if self.user['role'] == 'admin':
            # Администратор видит все курсы (но это отдельный случай)
            courses = db.fetch_all("SELECT id, title FROM courses ORDER BY id")
        else:
            # Преподаватель видит ТОЛЬКО свои курсы
            courses = db.fetch_all(
                "SELECT c.id, c.title FROM courses c WHERE c.teacher_id = ? ORDER BY c.id", 
                (self.user['id'],)
            )
        
        if not courses:
            self.course_combo['values'] = []
            self.course_combo.set("")
            self.course_info_label.config(text="У вас пока нет курсов. Создайте курс на вкладке «Создать курс»", foreground="red")
            self.current_course_id = None
            self.lessons_listbox.delete(0, tk.END)
            self.lessons_listbox.insert(tk.END, "Нет доступных курсов")
            return
        
        course_list = [f"{c['id']} - {c['title']}" for c in courses]
        self.course_combo['values'] = course_list
        self.course_combo.current(0)
        self.course_info_label.config(text=f"Всего курсов: {len(courses)}", foreground="green")
        self.on_course_selected()

    def on_course_selected(self, event=None):
        """При выборе курса загружаем его уроки"""
        selection = self.course_combo.get()
        if not selection:
            return
        
        try:
            course_id = int(selection.split(" - ")[0])
        except (ValueError, IndexError):
            return
        
        # Дополнительная проверка: принадлежит ли курс этому преподавателю
        db = Database()
        if self.user['role'] != 'admin':
            course_check = db.fetch_one(
                "SELECT id FROM courses WHERE id = ? AND teacher_id = ?", 
                (course_id, self.user['id'])
            )
            if not course_check:
                messagebox.showerror("Ошибка доступа", "Этот курс принадлежит другому преподавателю!")
                self.load_my_courses()  # Перезагружаем список
                return
        
        self.current_course_id = course_id
        self.load_lessons()

    def load_lessons(self):
        """Загружает уроки выбранного курса"""
        if not self.current_course_id:
            self.lessons_listbox.delete(0, tk.END)
            self.lessons_listbox.insert(tk.END, "Выберите курс из списка")
            return
        
        lessons = Lesson.get_by_course(self.current_course_id)
        self.lessons_listbox.delete(0, tk.END)
        
        if not lessons:
            self.lessons_listbox.insert(tk.END, "В этом курсе пока нет уроков")
            return
        
        for lesson in lessons:
            type_icon = "🎬" if lesson['lesson_type'] == 'video' else "📝" if lesson['lesson_type'] == 'text' else "📊"
            self.lessons_listbox.insert(
                tk.END, 
                f"{type_icon} [{lesson['order_num']}] {lesson['title']} ({lesson['lesson_type']})"
            )

    def delete_selected_lesson(self):
        """Удаляет выбранный урок"""
        selection = self.lessons_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите урок для удаления")
            return
        
        if not self.current_course_id:
            messagebox.showerror("Ошибка", "Сначала выберите курс")
            return
        
        # Получаем ID урока из выбранной строки
        lessons = Lesson.get_by_course(self.current_course_id)
        if selection[0] >= len(lessons):
            return
        
        lesson = lessons[selection[0]]
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Удалить урок «{lesson['title']}»?\nЭто действие нельзя отменить."):
            Lesson.delete(lesson['id'])
            messagebox.showinfo("Успех", "Урок удалён")
            self.load_lessons()

    def add_lesson(self):
        """Добавляет новый урок в выбранный курс"""
        if not self.current_course_id:
            messagebox.showerror("Ошибка", "Сначала выберите курс из списка")
            return
        
        title = self.lesson_title.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Введите название урока")
            return
        
        lesson_type = self.lesson_type.get()
        content = self.lesson_content.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showerror("Ошибка", "Введите содержимое урока")
            return
        
        # Валидация содержимого в зависимости от типа
        if lesson_type == 'video':
            if not (content.startswith('http://') or content.startswith('https://')):
                if not messagebox.askyesno("Предупреждение", "Ссылка на видео должна начинаться с http:// или https://\nПродолжить?"):
                    return
        
        elif lesson_type == 'quiz':
            # Проверяем, что JSON валидный
            import json
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                messagebox.showerror("Ошибка", f"Неверный формат JSON для теста\nОшибка: {e}")
                return
        
        try:
            order = int(self.order_entry.get()) if self.order_entry.get().strip() else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Порядок должен быть числом")
            return
        
        Lesson.add(self.current_course_id, title, lesson_type, content, order)
        messagebox.showinfo("Успех", f"Урок «{title}» добавлен в курс!")
        
        # Очищаем поля
        self.lesson_title.delete(0, tk.END)
        self.lesson_content.delete("1.0", tk.END)
        self.order_entry.delete(0, tk.END)
        
        # Обновляем список уроков
        self.load_lessons()