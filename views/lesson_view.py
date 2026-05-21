import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class LessonView:
    def __init__(self, user, lesson, parent_window, on_complete):
        self.user = user
        self.lesson = lesson
        self.parent = parent_window
        self.on_complete = on_complete   # сохраняем callback
        self.window = tk.Toplevel(parent_window)
        self.window.title(lesson['title'])
        self.window.geometry("700x500")
        self.create_content()

    def create_content(self):
        ttk.Label(self.window, text=self.lesson['title'], font=("Arial", 16)).pack(pady=10)
        if self.lesson['lesson_type'] == 'video':
            ttk.Label(self.window, text="Видео (откроется в браузере):").pack()
            url = self.lesson['content']
            ttk.Button(self.window, text="Смотреть видео", command=lambda: webbrowser.open(url)).pack(pady=10)
        elif self.lesson['lesson_type'] == 'text':
            text_frame = tk.Text(self.window, wrap=tk.WORD, height=15)
            text_frame.insert(tk.END, self.lesson['content'])
            text_frame.config(state=tk.DISABLED)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Для тестов отдельное окно QuizView

        def complete():
            if self.on_complete:
                self.on_complete()   # было on_conplete – исправлено
            self.window.destroy()

        ttk.Button(self.window, text="Отметить как пройденный", command=complete).pack(pady=10)