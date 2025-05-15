import logging
from db_utils import get_db_connection

def create_events_table(conn):
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        logging.info("Events table created successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to create events table: {e}")
        raise

if __name__ == '__main__':
    try:
        with get_db_connection() as conn:
            create_events_table(conn)
    except Exception as e:
        logging.error(f"Failed to create events table: {e}")
        raise