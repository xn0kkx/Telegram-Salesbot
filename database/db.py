import sqlite3
import os

def init_db():
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            payment_method TEXT,
            payment_status TEXT,
            payment_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id: int):
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def update_payment(user_id: int, payment_id: str, status: str):
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET payment_id = ?, payment_status = ?
        WHERE user_id = ?
    ''', (payment_id, status, user_id))
    conn.commit()
    conn.close()

def get_payment(user_id: int):
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute('SELECT payment_id, payment_status FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result
