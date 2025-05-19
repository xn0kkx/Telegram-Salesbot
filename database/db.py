import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    payment_id TEXT,
                    payment_status TEXT,
                    plano_valor REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    logger.info("Banco de dados PostgreSQL inicializado")

def add_user(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING', (user_id,))
            conn.commit()
    logger.debug(f"Usuário {user_id} adicionado")

def update_payment(user_id: int, payment_id: str, status: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET payment_id = %s, payment_status = %s
                WHERE user_id = %s
            ''', (payment_id, status, user_id))
            conn.commit()
    logger.debug(f"Pagamento atualizado: {payment_id} -> {status}")

def get_payment(user_id: int):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT payment_id, payment_status FROM users WHERE user_id = %s', (user_id,))
            result = cursor.fetchone()
    logger.debug(f"Consulta pagamento: {user_id} -> {result}")
    return result

def delete_user(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
            conn.commit()
    logger.debug(f"Usuário {user_id} removido")

def set_plano(user_id: int, valor: float):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET plano_valor = %s WHERE user_id = %s', (valor, user_id))
            conn.commit()
    logger.debug(f"Plano definido para usuário {user_id}: R$ {valor}")

def get_plano(user_id: int) -> float | None:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT plano_valor FROM users WHERE user_id = %s', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None