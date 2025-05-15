import logging
from datetime import datetime
from db_utils import get_db_connection

def convert_dates():
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT id, start_date, end_date FROM events')
            events = cursor.fetchall()
            
            for event in events:
                event_id, start_date, end_date = event
                try:
                    if '.' in start_date:
                        start_dt = datetime.strptime(start_date, '%d.%m.%Y')
                        end_dt = datetime.strptime(end_date, '%d.%m.%Y')
                        
                        new_start = start_dt.strftime('%Y-%m-%d')
                        new_end = end_dt.strftime('%Y-%m-%d')
                        
                        conn.execute(
                            'UPDATE events SET start_date = ?, end_date = ? WHERE id = ?',
                            (new_start, new_end, event_id)
                        )
                        logging.info(f"Converted dates for event {event_id}: {start_date}->{new_start}, {end_date}->{new_end}")
                except ValueError as e:
                    logging.error(f"Failed to convert dates for event {event_id}: {e}")
                    continue
            
            conn.commit()
            logging.info("Date format conversion completed")
    except Exception as e:
        logging.error(f"Failed to convert date formats: {e}")

if __name__ == '__main__':
    convert_dates()