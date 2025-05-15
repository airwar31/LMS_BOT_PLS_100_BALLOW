import logging
from db_utils import get_db_connection

def init_db(conn=None):
    if conn is None:
        conn = get_db_connection()
        
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                date TEXT PRIMARY KEY,
                first_shift_photo TEXT,
                second_shift_photo TEXT
            )
        ''')
        logging.info("Schedule table created successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to create schedule table: {e}")
        raise

def save_schedule(date: str, first_shift: str, second_shift: str = None) -> bool:
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM schedule WHERE date = ?', (date,))
        exists = cursor.fetchone() is not None
        cursor.execute(
            'INSERT OR REPLACE INTO schedule (date, first_shift_photo, second_shift_photo) VALUES (?, ?, ?)',
            (date, first_shift, second_shift)
        )
        return exists

def get_schedule(date: str):
    conn = get_db_connection()
    with conn:
        cursor = conn.execute(
            'SELECT first_shift_photo, second_shift_photo FROM schedule WHERE date = ?',
            (date,)
        )
        result = cursor.fetchone()
        return result if result else (None, None)

def delete_schedule(date: str):
    conn = get_db_connection()
    with conn:
        conn.execute('DELETE FROM schedule WHERE date = ?', (date,))