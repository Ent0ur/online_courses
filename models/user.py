from core.database import Database

class User:
    def __init__(self, user_id, email, full_name, role):
        self.id = user_id
        self.email = email
        self.full_name = full_name
        self.role = role

    @staticmethod
    def get_by_id(user_id):
        db = Database()
        row = db.fetch_one("SELECT id, email, full_name, role FROM users WHERE id = ?", (user_id,))
        if row:
            return User(row['id'], row['email'], row['full_name'], row['role'])
        return None

    def update_profile(self, full_name=None):
        db = Database()
        if full_name:
            db.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name, self.id))
            self.full_name = full_name
            log_action(self.id, "Profile updated")