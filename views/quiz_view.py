import tkinter as tk
from tkinter import ttk, messagebox
import json
from models.quiz import Quiz

class QuizView:
    def __init__(self, user, lesson, parent_window, on_complete):
        self.user = user
        self.lesson = lesson
        self.parent = parent_window
        self.on_complete = on_complete
        self.window = tk.Toplevel(parent_window)
        self.window.title(f"Тест: {lesson['title']}")
        self.window.geometry("600x500")
        self.answers = {}
        self.load_quiz()

    def load_quiz(self):
        try:
            questions = json.loads(self.lesson['content'])
        except:
            messagebox.showerror("Ошибка", "Некорректный формат теста")
            self.window.destroy()
            return
        self.questions = questions
        self.create_widgets()

    def create_widgets(self):
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, q in enumerate(self.questions):
            frame = ttk.LabelFrame(scrollable_frame, text=f"Вопрос {i+1}", padding=5)
            frame.pack(fill=tk.X, padx=10, pady=5)
            ttk.Label(frame, text=q['question'], wraplength=500).pack(anchor=tk.W)
            if q['type'] == 'single':
                var = tk.StringVar()
                for opt in q['options']:
                    ttk.Radiobutton(frame, text=opt, variable=var, value=opt).pack(anchor=tk.W)
                self.answers[str(i)] = var
            elif q['type'] == 'text':
                entry = ttk.Entry(frame, width=50)
                entry.pack(anchor=tk.W, pady=2)
                self.answers[str(i)] = entry

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def submit():
            user_answers = {}
            for k, v in self.answers.items():
                if isinstance(v, tk.StringVar):
                    user_answers[k] = v.get()
                else:
                    user_answers[k] = v.get()
            score = Quiz.process_quiz(self.lesson['id'], self.user['id'], user_answers)
            total = len(self.questions)
            messagebox.showinfo("Результат", f"Вы набрали {score} из {total} баллов")
            self.on_complete()
            self.window.destroy()
        ttk.Button(self.window, text="Завершить тест", command=submit).pack(pady=10)