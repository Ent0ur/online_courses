import tkinter as tk
from tkinter import ttk, messagebox
from core.auth import AuthManager
from views.main_view import MainWindow

class AuthWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Курсограф - Вход")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.current_frame = None
        self.show_login()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_login(self):
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding=20)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.current_frame, text="Вход в профиль", font=("Arial", 16)).pack(pady=10)

        ttk.Label(self.current_frame, text="Электронная почта").pack(anchor=tk.W, pady=(10,0))
        self.email_entry = ttk.Entry(self.current_frame, width=30)
        self.email_entry.pack(fill=tk.X, pady=5)

        ttk.Label(self.current_frame, text="Пароль").pack(anchor=tk.W, pady=(10,0))
        self.pass_entry = ttk.Entry(self.current_frame, show="*", width=30)
        self.pass_entry.pack(fill=tk.X, pady=5)

        ttk.Button(self.current_frame, text="Войти", command=self.do_login).pack(pady=10)
        ttk.Button(self.current_frame, text="Не помню пароль", command=self.show_reset).pack()
        ttk.Button(self.current_frame, text="Регистрация", command=self.show_register).pack(pady=5)

    def do_login(self):
        email = self.email_entry.get()
        pwd = self.pass_entry.get()
        user = AuthManager.login(email, pwd)
        if user:
            self.root.destroy()
            MainWindow(user)
        else:
            messagebox.showerror("Ошибка", "Неверный email или пароль")

    def show_register(self):
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding=20)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.current_frame, text="Регистрация", font=("Arial", 16)).pack(pady=10)

        ttk.Label(self.current_frame, text="Электронная почта").pack(anchor=tk.W)
        email_entry = ttk.Entry(self.current_frame)
        email_entry.pack(fill=tk.X, pady=5)

        ttk.Label(self.current_frame, text="ФИО").pack(anchor=tk.W)
        name_entry = ttk.Entry(self.current_frame)
        name_entry.pack(fill=tk.X, pady=5)

        ttk.Label(self.current_frame, text="Придумайте пароль").pack(anchor=tk.W)
        pass_entry = ttk.Entry(self.current_frame, show="*")
        pass_entry.pack(fill=tk.X, pady=5)

        ttk.Label(self.current_frame, text="Повторите пароль").pack(anchor=tk.W)
        pass2_entry = ttk.Entry(self.current_frame, show="*")
        pass2_entry.pack(fill=tk.X, pady=5)

        role_var = tk.StringVar(value="student")
        ttk.Radiobutton(self.current_frame, text="Студент", variable=role_var, value="student").pack(anchor=tk.W)
        ttk.Radiobutton(self.current_frame, text="Преподаватель", variable=role_var, value="teacher").pack(anchor=tk.W)

        # Доп поля для учителя
        spec_frame = ttk.Frame(self.current_frame)
        ttk.Label(spec_frame, text="Специализация").pack(anchor=tk.W)
        spec_entry = ttk.Entry(spec_frame)
        spec_entry.pack(fill=tk.X, pady=5)
        bio_entry = tk.Text(spec_frame, height=3)
        bio_entry.pack(fill=tk.X, pady=5)

        def toggle_teacher_fields(*args):
            if role_var.get() == "teacher":
                spec_frame.pack(fill=tk.X, pady=5)
            else:
                spec_frame.pack_forget()
        role_var.trace('w', toggle_teacher_fields)
        toggle_teacher_fields()

        agree_var = tk.BooleanVar()
        ttk.Checkbutton(self.current_frame, text="Я соглашаюсь на обработку персональных данных", variable=agree_var).pack(anchor=tk.W, pady=5)

        def do_register():
            if not agree_var.get():
                messagebox.showerror("Ошибка", "Необходимо согласие")
                return
            if pass_entry.get() != pass2_entry.get():
                messagebox.showerror("Ошибка", "Пароли не совпадают")
                return
            try:
                if role_var.get() == "teacher":
                    AuthManager.register(email_entry.get(), pass_entry.get(), "teacher", name_entry.get(),
                                         spec_entry.get(), bio_entry.get("1.0", tk.END))
                else:
                    AuthManager.register(email_entry.get(), pass_entry.get(), "student", name_entry.get())
                messagebox.showinfo("Успех", "Регистрация завершена. Теперь войдите.")
                self.show_login()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(self.current_frame, text="Зарегистрироваться", command=do_register).pack(pady=10)
        ttk.Button(self.current_frame, text="Уже есть аккаунт? Войдите", command=self.show_login).pack()

    def show_reset(self):
        self.clear_frame()
        self.current_frame = ttk.Frame(self.root, padding=20)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.current_frame, text="Восстановление пароля", font=("Arial", 16)).pack(pady=10)
        ttk.Label(self.current_frame, text="Электронная почта").pack(anchor=tk.W)
        email_entry = ttk.Entry(self.current_frame)
        email_entry.pack(fill=tk.X, pady=5)

        def send_code():
            email = email_entry.get()
            # Симуляция: генерируем код и "отправляем" на почту
            import random
            code = random.randint(100000, 999999)
            messagebox.showinfo("Код восстановления", f"Код {code} отправлен на {email} (демо)")
            # Окно ввода кода и нового пароля
            code_window = tk.Toplevel(self.root)
            code_window.title("Введите код")
            ttk.Label(code_window, text="Код из письма").pack()
            code_entry = ttk.Entry(code_window)
            code_entry.pack()
            ttk.Label(code_window, text="Новый пароль").pack()
            new_pass = ttk.Entry(code_window, show="*")
            new_pass.pack()
            def reset():
                if code_entry.get() == str(code):
                    if AuthManager.reset_password(email, new_pass.get()):
                        messagebox.showinfo("Успех", "Пароль изменён")
                        code_window.destroy()
                        self.show_login()
                    else:
                        messagebox.showerror("Ошибка", "Email не найден")
                else:
                    messagebox.showerror("Ошибка", "Неверный код")
            ttk.Button(code_window, text="Сбросить пароль", command=reset).pack()
        ttk.Button(self.current_frame, text="Отправить код восстановления", command=send_code).pack(pady=10)
        ttk.Button(self.current_frame, text="Назад к входу", command=self.show_login).pack()

    def run(self):
        self.root.mainloop()