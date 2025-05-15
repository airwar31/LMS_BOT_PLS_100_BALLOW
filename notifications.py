from aiogram import Bot
from db_utils import get_db_connection
import asyncio

async def send_announcement(bot: Bot, text: str, media=None):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            users = cursor.fetchall()
            
            for user in users:
                try:
                    if media:
                        if media['type'] == 'photo':
                            await bot.send_photo(user[0], media['file_id'], caption=f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                        elif media['type'] == 'video':
                            await bot.send_video(user[0], media['file_id'], caption=f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                    else:
                        await bot.send_message(user[0], f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Failed to send announcement to user {user[0]}: {e}")
    finally:
        conn.close()

async def send_schedule_notification(bot: Bot, date: str, is_update: bool = False):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users')
            users = cursor.fetchall()
            
            action = "обновлено" if is_update else "добавлено"
            message = f"📅 Расписание на {date} было {action}!"
            
            for user in users:
                try:
                    await bot.send_message(user['user_id'], message)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Error sending notification to user {user['user_id']}: {str(e)}")
    except Exception as e:
        print(f"Error in send_schedule_notification: {str(e)}")