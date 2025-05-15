import logging
from db_utils import get_db_connection

def add_event_indexes():
    try:
        with get_db_connection() as conn:
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_start 
                ON events (start_date, start_time)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_end 
                ON events (end_date, end_time)
            """)
            conn.commit()
            logging.info("Event indexes created successfully")
            cursor = conn.execute('''
                SELECT id, start_date, end_date, start_time, end_time 
                FROM events 
                WHERE strftime('%Y-%m-%d %H:%M', start_date || ' ' || start_time) IS NULL
                OR strftime('%Y-%m-%d %H:%M', end_date || ' ' || end_time) IS NULL
            ''')
            invalid = cursor.fetchall()
            if invalid:
                logging.error(f"Found {len(invalid)} events with invalid date/time format: {invalid}")
            cursor = conn.execute('SELECT id, start_date, end_date, start_time, end_time FROM events')
            events = cursor.fetchall()
            for event in events:
                logging.info(f"Event {event[0]}: Start={event[1]} {event[3]}, End={event[2]} {event[4]}")
    except Exception as e:
        logging.error(f"Error creating indexes: {e}")

if __name__ == '__main__':
    add_event_indexes()