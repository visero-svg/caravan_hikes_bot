import asyncio
import json
import os
import http.server
import socketserver
from threading import Thread

from aiogram import Bot, Dispatcher, types
from aiogram.types import InputMediaPhoto

# Токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в переменных окружения!")

# Каналы для публикации
CHANNELS = [
    "@caravan_hobby",
    "@your_second_channel",  # Замени на свой второй канал
]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик данных из Web App
@dp.message(lambda message: message.web_app_data is not None)
async def handle_web_app(message: types.Message):
    try:
        payload = json.loads(message.web_app_data.data)
    except json.JSONDecodeError:
        await message.answer("Ошибка: неверный формат данных.")
        return

    if payload.get("action") == "publish_hike":
        if "media" in payload:
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
            text = payload.get("text", "Новый поход")
            for channel in CHANNELS:
                await bot.send_message(channel, text, parse_mode="HTML", disable_web_page_preview=True)
        
        await message.answer("✅ Поход опубликован во всех каналах!")
    else:
        await message.answer("Неизвестное действие.")

# HTTP-сервер для Render
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Отключаем логи

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Caravan Hikes Bot alive! 🚴‍♂️")

def run_http_server():
    port = int(os.getenv("PORT", 10000))  # Render передаёт порт через $PORT
    with socketserver.TCPServer(("0.0.0.0", port), QuietHandler) as httpd:
        print(f"HTTP-сервер запущен на порту {port} — Render доволен ✓")
        httpd.serve_forever()

async def start_polling():
    print("Запуск polling бота...")
    await dp.start_polling(bot)

async def main():
    # Запускаем HTTP-сервер в отдельном потоке (он будет основным процессом для Render)
    http_thread = Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Запускаем polling бота как асинхронную задачу
    await start_polling()

if __name__ == "__main__":
    asyncio.run(main())