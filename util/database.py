import hashlib
import sqlite3
import secrets

def selfHash(passwd: bytes,salt:bytes=None) -> bytes:
    if not salt:
        salt = secrets.token_bytes(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', passwd, salt, 100000)
    return salt +b":"+ hashed_password

def create_database():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, email, hash):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, hash))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Error: E-Mail already exists.")
        conn.close()
        return False
    conn.close()
    return True
def get_user(email):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, email, password_hash FROM users WHERE email=?
    ''', (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        username, email, password_hash = row
        return (username, email, password_hash)
    else:
        return None


def delete_user(email):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM users WHERE email=?
    ''', (email,))
    if cursor.rowcount == 0:
        print("Error: Username not found.")
    else:
        conn.commit()
        print(f"User '{email}' deleted successfully.")
    conn.close()
