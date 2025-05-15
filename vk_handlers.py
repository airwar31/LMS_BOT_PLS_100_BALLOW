from aiogram import Bot, types
import vk_api
from config import VK_TOKEN, VK_GROUP_ID
import logging

async def get_vk_news():
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    posts = vk.wall.get(owner_id=f"-{VK_GROUP_ID}", count=5)
    return posts['items']

async def forward_vk_post_to_telegram(bot: Bot, post, user_id: int):
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    try:
        MAX_CAPTION_LENGTH = 1024
        text = post.get('text', '')
        attachments = post.get('attachments', [])
        photos = []
        media = []

        if attachments:
            for attachment in attachments:
                if attachment['type'] == 'photo':
                    sizes = attachment['photo']['sizes']
                    largest_photo = max(sizes, key=lambda x: x['width'] * x['height'])
                    photos.append(largest_photo['url'])
                elif attachment['type'] == 'video':
                    video_data = attachment['video']
                    if 'player' in video_data:
                        if len(attachments) > 1:
                            media.append(types.InputMediaVideo(media=video_data['player'], caption=text if not photos and not media else None))
                            text = ''
                        else:
                            await bot.send_video(user_id, video_data['player'], caption=text)
                            text = ''
                    else:
                        video_link = f"[View video on VK](https://vk.com/video{video_data['owner_id']}_{video_data['id']})"
                        if len(attachments) > 1:
                            text = (text + "\n" + video_link) if text else video_link
                        else:
                            await bot.send_message(user_id, (text + "\n" + video_link) if text else video_link, parse_mode="Markdown")
                            text = ''

        if len(text) > MAX_CAPTION_LENGTH:
            await bot.send_message(user_id, text)
            text = ''

        if photos:
            for i, photo_url in enumerate(photos):
                if i == 0 and text:
                    media.append(types.InputMediaPhoto(media=photo_url, caption=text))
                else:
                    media.append(types.InputMediaPhoto(media=photo_url))
            
            if len(media) == 1:
                await bot.send_photo(user_id, media[0].media, caption=media[0].caption)
            elif len(media) > 1:
                await bot.send_media_group(user_id, media)
        elif media:
            await bot.send_media_group(user_id, media)
        elif text:
            await bot.send_message(user_id, text)

    except Exception as e:
        logging.error(f"Error forwarding VK post to user {user_id}: {e}")