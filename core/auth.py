import hashlib
import secrets
from core.database import Database
from core.logger import log_action

class AuthManager:
    @staticmethod
    def _hash_password(password):
        salt = secrets.token_hex(8)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"

    @staticmethod
    def _verify_password(password, stored):
        salt, pwd_hash = stored.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return new_hash == pwd_hash

    @staticmethod
    def register(email, password, role, full_name, specialization=None, bio=None):
        db = Database()
        # Проверка уникальности email
        if db.fetch_one("SELECT id FROM users WHERE email = ?", (email,)):
            raise ValueError("Email уже существует")
        hashed = AuthManager._hash_password(password)
        try:
            db.execute(
                "INSERT INTO users (email, password, role, full_name) VALUES (?, ?, ?, ?)",
                (email, hashed, role, full_name)
            )
            user_id = db.fetch_one("SELECT last_insert_rowid()")[0]
            if role == 'teacher':
                db.execute(
                    "INSERT INTO teachers (user_id, specialization, bio) VALUES (?, ?, ?)",
                    (user_id, specialization, bio)
                )
            elif role == 'student':
                db.execute("INSERT INTO students (user_id) VALUES (?)", (user_id,))
            log_action(user_id, f"Registered as {role}")
            return user_id
        except Exception as e:
            raise e

    @staticmethod
    def login(email, password):
        db = Database()
        user = db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
        if user and AuthManager._verify_password(password, user['password']):
            log_action(user['id'], "Logged in")
            return dict(user)
        return None

    @staticmethod
    def change_password(user_id, old_password, new_password):
        db = Database()
        user = db.fetch_one("SELECT password FROM users WHERE id = ?", (user_id,))
        if user and AuthManager._verify_password(old_password, user['password']):
            new_hashed = AuthManager._hash_password(new_password)
            db.execute("UPDATE users SET password = ? WHERE id = ?", (new_hashed, user_id))
            log_action(user_id, "Password changed")
            return True
        return False

    @staticmethod
    def reset_password(email, new_password):
        db = Database()
        user = db.fetch_one("SELECT id FROM users WHERE email = ?", (email,))
        if user:
            new_hashed = AuthManager._hash_password(new_password)
            db.execute("UPDATE users SET password = ? WHERE id = ?", (new_hashed, user['id']))
            log_action(user['id'], "Password reset")
            return True
        return False