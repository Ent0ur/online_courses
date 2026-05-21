import tkinter as tk
from tkinter import ttk, messagebox
from core.auth import AuthManager
from models.user import User

class ProfileView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Профиль пользователя", font=("Arial", 18)).pack(pady=10)

        ttk.Label(frame, text=f"Email: {self.user['email']}").pack(anchor=tk.W, pady=5)
        ttk.Label(frame, text=f"Роль: {self.user['role']}").pack(anchor=tk.W, pady=5)

        ttk.Label(frame, text="ФИО:").pack(anchor=tk.W, pady=(10,0))
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.insert(0, self.user['full_name'] or "")
        self.name_entry.pack(anchor=tk.W, pady=5)

        def update_name():
            new_name = self.name_entry.get()
            u = User.get_by_id(self.user['id'])
            u.update_profile(new_name)
            messagebox.showinfo("Успех", "Имя обновлено")
            self.user['full_name'] = new_name
        ttk.Button(frame, text="Обновить ФИО", command=update_name).pack(anchor=tk.W, pady=5)

        # Смена пароля
        ttk.Label(frame, text="Смена пароля", font=("Arial", 12)).pack(anchor=tk.W, pady=(20,0))
        ttk.Label(frame, text="Старый пароль:").pack(anchor=tk.W)
        old_pass = ttk.Entry(frame, show="*")
        old_pass.pack(anchor=tk.W, pady=2)
        ttk.Label(frame, text="Новый пароль:").pack(anchor=tk.W)
        new_pass = ttk.Entry(frame, show="*")
        new_pass.pack(anchor=tk.W, pady=2)
        ttk.Label(frame, text="Повторите:").pack(anchor=tk.W)
        new_pass2 = ttk.Entry(frame, show="*")
        new_pass2.pack(anchor=tk.W, pady=2)

        def change_pwd():
            if new_pass.get() != new_pass2.get():
                messagebox.showerror("Ошибка", "Новые пароли не совпадают")
                return
            if AuthManager.change_password(self.user['id'], old_pass.get(), new_pass.get()):
                messagebox.showinfo("Успех", "Пароль изменён")
                old_pass.delete(0, tk.END)
                new_pass.delete(0, tk.END)
                new_pass2.delete(0, tk.END)
            else:
                messagebox.showerror("Ошибка", "Неверный старый пароль")
        ttk.Button(frame, text="Сменить пароль", command=change_pwd).pack(anchor=tk.W, pady=5)