import sqlite3

class User:
    def __init__(self, telegram_id, username):
        self.telegram_id = telegram_id
        self.username = username

    @staticmethod
    def get_user_by_username(username):
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute('SELECT telegram_id, balance FROM employees WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(row[0], username)
        else:
            return None

    @staticmethod
    def get_user_by_telegram_id(telegram_id):
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute('SELECT username, balance FROM employees WHERE telegram_id = ?', (telegram_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(telegram_id, row[0])
        else:
            return None

    def update_balance(self, amount):
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute('UPDATE employees SET balance = ? WHERE telegram_id = ?', (amount, self.telegram_id))
        conn.commit()
        conn.close()

    def get_balance(self):
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute('SELECT balance FROM employees WHERE telegram_id = ?', (self.telegram_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
        else:
            return 0.0
