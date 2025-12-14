import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

#BOT_TOKEN = "8305643499:AAF9qHFp7pvtVmmCeqzPiXW7ZY794cYh6qM"  # ← Вставьте свой токен
#CHANNEL_ID = "@KARAVAN_Velo"     # ← Укажите username канала или числовой ID (например, -1001234567890)

CHANNELS = [
    "@velotravelru",          # Первый канал
    "@VeloCaravan", # Второй канал
    # "-1001234567890",        # Или числовой ID (если приватный)
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(types.ContentType.WEB_APP_DATA)
async def handle_web_app(message: types.Message):
    payload = json.loads(message.web_app_data.data)
    
    if payload.get("action") == "publish_hike":
        if "media" in payload:
            media_group = []
            for item in payload["media"]:
                media_group.append(InputMediaPhoto(
                    media=item["media"],
                    caption=item.get("caption"),
                    parse_mode="HTML"
                ))
            await bot.send_media_group(CHANNEL_ID, media_group)
        else:
            text = payload.get("text", "Новый поход")
            await bot.send_message(CHANNEL_ID, text, parse_mode="HTML", disable_web_page_preview=True)
        
        await message.answer("✅ Поход успешно опубликован в канале!")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())