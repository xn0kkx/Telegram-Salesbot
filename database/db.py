import sqlite3
import logging

logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            payment_id TEXT,
            payment_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Banco de dados inicializado")

def add_user(user_id: int):
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()
    logger.debug(f"Usuário {user_id} adicionado")

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
    logger.debug(f"Pagamento atualizado: {payment_id} -> {status}")

def get_payment(user_id: int):
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute('SELECT payment_id, payment_status FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    logger.debug(f"Consulta pagamento: {user_id} -> {result}")
    return result

def delete_user(user_id: int):
    conn = sqlite3.connect('payments.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    logger.debug(f"Usuário {user_id} removido")
