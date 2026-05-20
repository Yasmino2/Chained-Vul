import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')

    # Seed an admin account
    c.execute('''
        INSERT OR IGNORE INTO users (username, email, password, role)
        VALUES ('admin', 'admin@site.com', 'admin123', 'admin')
    ''')

    # Seed a regular user account
    c.execute('''
        INSERT OR IGNORE INTO users (username, email, password, role)
        VALUES ('alice', 'alice@site.com', 'alice123', 'user')
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == '__main__':
    init_db()