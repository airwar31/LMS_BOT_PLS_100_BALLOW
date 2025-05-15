import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db_utils import init_db
from schedule_db import init_db as init_schedule_db
from vk_notifications import check_and_forward_vk_posts
from router import register_handlers
from config import BOT_TOKEN


logging.basicConfig(level=logging.INFO)
logging.info("Initializing database and creating tables...")
for attempt in range(3):
    try:
        logging.info("Initializing database...")
        init_db()
        init_schedule_db()
        logging.info("Database initialization successful")
        break
    except Exception as e:
        logging.error(f"Database initialization attempt {attempt + 1} failed: {e}")
        if attempt == 2:
            raise SystemExit(1)
        continue

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def main():
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    from db_utils import init_db, DB_PATH
    from db_lock import DatabaseLock
    
    logging.info(f"Using database at path: {DB_PATH}")
    
    DatabaseLock.clear_lock()
    
    try:
        logging.info("Initializing database...")
        
        logging.info("Initializing database tables...")
        logging.info("Starting database initialization...")
        init_db()
        DatabaseLock.mark_initialized()
        logging.info("Database initialization completed")
        
        register_handlers(dp)
        logging.info("Handlers registered")
        
        async def check_vk_posts_periodically():
            while True:
                try:
                    await check_and_forward_vk_posts(bot)
                except Exception as e:
                    logging.error(f"Error checking VK posts: {e}")
                await asyncio.sleep(60)
        
        loop = asyncio.get_event_loop()
        loop.create_task(check_vk_posts_periodically())
        
        logging.info("Starting bot polling...")
        await dp.start_polling()
    except Exception as e:
        logging.critical(f"Failed to start bot: {e}")
        raise


if __name__ == '__main__':
    from migrations.convert_date_format import convert_dates
    from migrations.add_event_indexes import add_event_indexes
    convert_dates()
    add_event_indexes()
    asyncio.run(main())