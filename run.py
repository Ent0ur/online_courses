#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.auth import AuthManager
from views.auth_view import AuthWindow

def main():
    # Инициализация БД
    db = Database()
    db.create_tables()
    # Создание тестового админа, если нет пользователей
    if not db.fetch_one("SELECT id FROM users LIMIT 1"):
        from core.auth import AuthManager
        AuthManager.register("admin@example.com", "admin123", "admin", "Admin User")
        print("Создан администратор: admin@example.com / admin123")
    # НЕ закрываем БД здесь, оставляем открытым на всё время работы приложения
    # db.close()  - убрать!

    # Запуск окна авторизации
    app = AuthWindow()
    app.run()

if __name__ == "__main__":
    main()