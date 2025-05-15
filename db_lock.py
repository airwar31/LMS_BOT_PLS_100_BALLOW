import os
import logging
import time

class DatabaseLock:
    LOCK_FILE = "db.lock"
    MAX_WAIT = 30

    @classmethod
    def wait_for_initialization(cls):
        start_time = time.time()
        while not os.path.exists(cls.LOCK_FILE):
            if time.time() - start_time > cls.MAX_WAIT:
                raise TimeoutError("Database initialization timed out")
            time.sleep(0.1)
        return True

    @classmethod
    def mark_initialized(cls):
        try:
            with open(cls.LOCK_FILE, 'w') as f:
                f.write('initialized')
            logging.info("Database marked as initialized")
        except Exception as e:
            logging.error(f"Failed to create database lock file: {e}")
            raise

    @classmethod
    def clear_lock(cls):
        try:
            if os.path.exists(cls.LOCK_FILE):
                os.remove(cls.LOCK_FILE)
        except Exception:
            pass