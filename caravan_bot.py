import asyncio
import json
import os  # Для переменных окружения на Render

from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto

# Лучше брать токен из переменных окружения (безопасно для Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")  # На Render добавь в Environment Variables
if not BOT_TOKEN:
    raise ValueError("Укажите BOT_TOKEN в переменных окружения!")

# Список каналов для публикации (добавь сколько нужно)
CHANNELS = [
    "@caravan_hobby",          # Первый канал
    "@your_second_channel",    # Второй канал (замени на реальный)
    # "-1001234567890",        # Приватный канал — числовой ID
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Правильный обработчик для Web App данных в aiogram 3.x
@dp.message(lambda message: message.web_app_data is not None)
async def handle_web_app(message: types.Message):
    # Данные приходят в message.web_app_data.data (строка JSON)
    try:
        payload = json.loads(message.web_app_data.data)
    except json.JSONDecodeError:
        await message.answer("Ошибка: неверные данные из формы.")
        return
    
    if payload.get("action") == "publish_hike":
        if "media" in payload:
            # Отправляем альбом фото в каждый канал
            for channel in CHANNELS:
                media_group = []
                for item in payload["media"]:
                    media_group.append(InputMediaPhoto(
                        media=item["media"],
                        caption=item.get("caption"),
                        parse_mode="HTML"
                    ))
                await bot.send_media_group(channel, media_group)
        else:
            # Только текст
            text = payload.get("text", "Новый поход")
            for channel in CHANNELS:
                await bot.send_message(
                    channel,
                    text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
        
        await message.answer("✅ Поход успешно опубликован во всех каналах!")

    else:
        await message.answer("Неизвестное действие.")

async def main():
    print("Бот запущен и работает...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())