import logging
from db_utils import get_db_connection
import sqlite3
def save_event(name: str, description: str, start_date: str, end_date: str, start_time: str, end_time: str) -> bool:
    try:
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO events (name, description, start_date, end_date, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)',
                (name, description, start_date, end_date, start_time, end_time)
            )
        return True
    except sqlite3.Error:
        return False

def get_current_events():
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM events 
                WHERE 
                    -- Not ended yet (end datetime is in future)
                    datetime(end_date || ' ' || end_time) > datetime('now', 'localtime')
                    AND
                    -- Starts within next 7 days
                    date(start_date) <= date('now', 'localtime', '+7 days')
                    AND
                    date(start_date) >= date('now', 'localtime')
                ORDER BY 
                    date(start_date) ASC,
                    time(start_time) ASC
            ''')
            events = cursor.fetchall()
            if not events:
                logging.info("No events matched the current week criteria.")
                now = conn.execute("SELECT datetime('now', 'localtime')").fetchone()[0]
                week_later = conn.execute("SELECT date('now', 'localtime', '+7 days')").fetchone()[0]
                logging.info(f"Current time: {now}")
                logging.info(f"Week later date: {week_later}")
                
            return events
    except Exception as e:
        logging.error(f"Error getting current events: {e}")
        raise

def get_event(event_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,))
        return cursor.fetchone()

def delete_event(event_id: int):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM events WHERE id = ?', (event_id,))