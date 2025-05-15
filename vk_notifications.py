from aiogram import Bot
import asyncio
from vk_handlers import get_vk_news, forward_vk_post_to_telegram
from db_utils import get_db_connection
import logging
async def get_sent_post_ids(cursor):
    cursor.execute("SELECT post_id FROM sent_vk_posts")
    return {row[0] for row in cursor.fetchall()}

async def add_sent_post_id(cursor, post_id):
    cursor.execute("INSERT INTO sent_vk_posts (post_id) VALUES (?)", (post_id,))
    cursor.execute("DELETE FROM sent_vk_posts WHERE post_id NOT IN (SELECT post_id FROM sent_vk_posts ORDER BY sent_at DESC LIMIT 1000)")

async def check_and_forward_vk_posts(bot: Bot):
    try:
        posts = await get_vk_news()
        
        if not posts:
            return
            
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                sent_post_ids = await get_sent_post_ids(cursor)
                new_posts = [post for post in posts if post['id'] not in sent_post_ids]
                if not new_posts:
                    return
                    
                cursor.execute("SELECT user_id FROM users")
                users = cursor.fetchall()
                for post in new_posts:
                    post_id = post['id']
                    for user in users:
                        try:
                            await forward_vk_post_to_telegram(bot, post, user[0])
                            await asyncio.sleep(0.1)
                        except Exception as e:
                            logging.error(f"Failed to send VK post {post_id} to user {user[0]}: {e}")

                    await add_sent_post_id(cursor, post_id)
        finally:
            conn.close()
    except Exception as e:
        logging.error(f"Error in check_and_forward_vk_posts: {e}")