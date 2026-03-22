import hashlib
import sqlite3
from database import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?", (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "username": user[1], "role": user[2]}
    return None

def register_user(username, password, role, name=""):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash, name, role) VALUES (?, ?, ?, ?)", (username, hashed_pw, name, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Update initial users to have hashed passwords if they were added as plain text
def upgrade_passwords():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users")
    users = cursor.fetchall()
    
    for uid, pwd in users:
        if len(pwd) < 64: # If not already a SHA256 hash (64 chars)
            hashed = hash_password(pwd)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, uid))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    upgrade_passwords()
    print("Passwords upgraded successfully.")
