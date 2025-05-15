import os
import sqlite3
import logging
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, 'bot.db'))

def get_db_connection():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=20)
        conn.execute("PRAGMA journal_mode = DELETE")
        conn.execute("PRAGMA synchronous = FULL") 
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA locking_mode = NORMAL")
        conn.execute("PRAGMA read_uncommitted = 0")
        conn.row_factory = sqlite3.Row
        results = conn.execute("PRAGMA journal_mode").fetchone()
        logging.debug(f"journal_mode set to: {results[0]}")
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise

def ensure_table_exists():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = get_db_connection()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Failed to create database: {e}")
        raise

def init_db():
    try:
        logging.info("Starting database initialization...")
        with get_db_connection() as conn:
            logging.info("Creating users table if it doesn't exist...")
            conn.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                patronymic TEXT NOT NULL,
                class TEXT NOT NULL,
                shift TEXT NOT NULL,
                phone TEXT NOT NULL,
                telegram_username TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('users',))
            if not cursor.fetchone():
                raise Exception("Failed to create users table - table not found after creation")
            logging.info("Users table created and verified")
            logging.info("Creating sent_vk_posts table if it doesn't exist...")
            with open('migrations/20230000_add_sent_vk_posts.sql', 'r') as f:
                conn.executescript(f.read())
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('sent_vk_posts',))
            if not cursor.fetchone():
                raise Exception("Failed to create sent_vk_posts table - table not found after creation")
            logging.info("sent_vk_posts table created and verified")
        with get_db_connection() as conn:
            logging.info("Creating events table...")
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
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('events',))
            if not cursor.fetchone():
                raise Exception("Failed to create events table - table not found after creation")
            logging.info("Events table created and verified")

        logging.info("Database initialization completed successfully")
        return True
            
    except Exception as e:
        import traceback
        logging.error(f"Failed to initialize database: {e}")
        logging.error(f"Full traceback:\n{traceback.format_exc()}")
        raise

def register_user(user_id: int, name: str, surname: str, patronymic: str, class_name: str, 
              shift: str, phone: str, telegram_username: str) -> None:
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO users (
                user_id, name, surname, patronymic, class, shift, 
                phone, telegram_username, registration_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (user_id, name, surname, patronymic, class_name, shift, 
              phone, telegram_username))
        conn.commit()

def get_user_profile(user_id: int) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    conn = None
    try:
        ensure_table_exists()
        logging.info("Database file and directory verified")
        from migrations.create_events_table import create_events_table
        from schedule_db import init_db as init_schedule_db
        conn = get_db_connection()
        conn.execute("BEGIN EXCLUSIVE")
        
        try:
            logging.info("Creating tables...")
            create_users_table(conn)
            create_events_table(conn)
            init_schedule_db(conn)
            
            logging.info("Verifying tables...")
            cursor = conn.cursor()
            for table in ['users', 'events']:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if not cursor.fetchone():
                    raise Exception(f"Failed to create table: {table}")
            
            conn.commit()
            logging.info("Database initialized successfully")
            return True
            
        except Exception:
            if conn:
                conn.rollback()
            raise
            
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        return False
        
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logging.error(f"Error closing connection: {e}")