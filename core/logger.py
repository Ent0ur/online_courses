from core.database import Database

def log_action(user_id, action):
    db = Database()
    db.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user_id, action))