import sqlite3

def create_table():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (telegram_id INTEGER PRIMARY KEY, username TEXT, balance REAL)''')
    conn.commit()
    conn.close()
