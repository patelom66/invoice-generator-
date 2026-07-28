from flask_login import UserMixin
from app import mysql, login_manager

class User(UserMixin):
    def __init__(self, id, name, email, currency='$'):
        self.id = id
        self.name = name
        self.email = email
        self.currency = currency

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user['id'], user['name'], user['email'], user.get('currency', '$'))
    return None